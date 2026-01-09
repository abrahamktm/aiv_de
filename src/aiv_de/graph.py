from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import yaml
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver  # persistence

from aiv_de.config import SETTINGS
from aiv_de.types import AIVDEState
from aiv_de.agents.requirements_analyst import run_requirements
from aiv_de.agents.architect import propose_options
from aiv_de.agents.validator_governance import validate_and_veto
from aiv_de.agents.adr_writer import write_adr

def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _load_yaml(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_policy_store(policy_dir: str) -> Dict[str, Any]:
    return {
        "eu_ai_act_policy": _load_yaml(os.path.join(policy_dir, "eu_ai_act_policy.yaml")),
        "data_residency_policy": _load_yaml(os.path.join(policy_dir, "data_residency_policy.yaml")),
        "hitl_policy": _load_yaml(os.path.join(policy_dir, "hitl_policy.yaml")),
        "security_policy": _load_yaml(os.path.join(policy_dir, "security_policy.yaml")),
        "scoring_weights": _load_yaml(os.path.join(policy_dir, "scoring_weights.yaml")),
    }

def n_requirements(state: AIVDEState) -> Dict[str, Any]:
    llm = ChatOpenAI(model=SETTINGS.model_name)
    run_id = state.get("run_id", "no_run_id")
    req = run_requirements(llm, state["site_profile"], run_id)
    trace = state.get("trace", [])
    trace.append({"node": "requirements", "event": "done"})
    return {"requirements": req, "trace": trace}

def n_architect(state: AIVDEState) -> Dict[str, Any]:
    llm = ChatOpenAI(model=SETTINGS.model_name)
    opts = propose_options(
        llm,
        state["site_profile"],
        state.get("requirements", {}),
        state.get("hw_db", []),
        state.get("vetoes", []),
        state.get("run_id", "no_run_id"),
    )

    trace = state.get("trace", [])
    if opts.get("error"):
        trace.append({"node": "architect", "event": "validation_failed", "error": opts.get("error")})
    else:
        trace.append({"node": "architect", "event": "proposed_structured"})
    return {"options": opts.get("options", []), "trace": trace}

def n_select(state: AIVDEState) -> Dict[str, Any]:
    # For skeleton: pick first option or a minimal default if not present
    options = state.get("options", [])
    selected = options[0] if options else {
        "option_id": "DEFAULT_EDGE",
        "summary": "Default edge-local inference with telemetry-only.",
        "placement": {"inference": "edge", "storage": "onprem"},
        "pipeline": ["roi_detection", "tiling_or_downsample", "local_inference", "telemetry_only"],
        "hardware": ["EDGE_GPU_25W_16GB"],
        "pros": ["Low latency", "Residency-compliant"],
        "cons": ["More edge ops overhead"],
        "risks": ["Drift across sites"],
        "mitigations": ["Canary rollout + drift monitoring + HITL gates"]
    }
    hw_db = state.get("hw_db", [])
    if not selected.get("hardware") and hw_db:
        selected = {**selected, "hardware": [hw_db[0].get("hw_id")]}

    trace = state.get("trace", [])
    trace.append({"node": "select", "event": "selected", "option_id": selected.get("option_id")})
    return {"selected_option": selected, "trace": trace}

def n_validate(state: AIVDEState) -> Dict[str, Any]:
    out = validate_and_veto(
        site_profile=state["site_profile"],
        selected_option=state["selected_option"],
        hw_db=state["hw_db"],
        policy_store=state["policies"],
    )
    trace = state.get("trace", [])
    trace.append({"node": "validate", "event": "validated", "vetoes": out["vetoes"]})
    hitl_required = len(out["vetoes"]) > 0 and (state.get("retries", 0) >= state.get("max_retries", SETTINGS.max_retries))
    return {**out, "trace": trace, "hitl_required": hitl_required}

def n_revise(state: AIVDEState) -> Dict[str, Any]:
    # Increment retries and allow architect to re-propose (in a real build, feed veto reasons)
    retries = int(state.get("retries", 0)) + 1
    trace = state.get("trace", [])
    trace.append({"node": "revise", "event": "retry", "retries": retries})
    return {"retries": retries, "trace": trace}

def n_adr(state: AIVDEState) -> Dict[str, Any]:
    llm = ChatOpenAI(model=SETTINGS.model_name)
    validation = {"feasibility": state.get("feasibility"), "policy": state.get("policy"), "vetoes": state.get("vetoes", [])}
    adr_md = write_adr(llm, state["site_profile"], state["selected_option"], validation, state.get("trace", []))
    trace = state.get("trace", [])
    trace.append({"node": "adr", "event": "written"})
    return {"adr": adr_md, "trace": trace}

def n_hitl(state: AIVDEState) -> Dict[str, Any]:
    # Minimal: mark escalation; in later days you can implement an approval UI
    trace = state.get("trace", [])
    trace.append({"node": "hitl", "event": "escalated"})
    return {"adr": "# ADR-001\n\n**ESCALATED TO HUMAN**: constraints/policies could not be satisfied within retry budget.\n",
            "trace": trace}

def route_after_validate(state: AIVDEState) -> str:
    vetoes = state.get("vetoes", [])
    if not vetoes:
        return "adr"
    if state.get("hitl_required", False):
        return "hitl"
    return "revise"

def build_graph() -> Any:
    g = StateGraph(AIVDEState)
    g.add_node("requirements", n_requirements)
    g.add_node("architect", n_architect)
    g.add_node("select", n_select)
    g.add_node("validate", n_validate)
    g.add_node("revise", n_revise)
    g.add_node("adr", n_adr)
    g.add_node("hitl", n_hitl)

    g.add_edge(START, "requirements")
    g.add_edge("requirements", "architect")
    g.add_edge("architect", "select")
    g.add_edge("select", "validate")

    g.add_conditional_edges("validate", route_after_validate, {
        "adr": "adr",
        "revise": "revise",
        "hitl": "hitl"
    })

    g.add_edge("revise", "architect")
    g.add_edge("adr", END)
    g.add_edge("hitl", END)
    return g

#def compile_graph() -> Any:
#   graph = build_graph()
#   with SqliteSaver.from_conn_string(SETTINGS.sqlite_path) as checkpointer:
#       return graph.compile(checkpointer=checkpointer)

import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from aiv_de.config import SETTINGS

def compile_graph():
    graph = build_graph()

    # Keep connection open for the lifetime of the compiled app
    conn = sqlite3.connect(SETTINGS.sqlite_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    app = graph.compile(checkpointer=checkpointer)

    # store references so they don't get garbage-collected
    app._aivde_sqlite_conn = conn
    app._aivde_checkpointer = checkpointer
    return app
