from __future__ import annotations
from typing import Any, Dict
from langchain_openai import ChatOpenAI

SYSTEM = """You are an ADR writer.
Write ADR-001 in a professional, audit-ready style.
Include: Context, Decision (+ alternatives), Assumptions, Trade-offs, Risks & mitigations,
Governance + HITL triggers, Evidence & tool calls used, Rollout plan, Consequences.
Return markdown.
"""

def write_adr(llm: ChatOpenAI, site_profile: Dict[str, Any], selected_option: Dict[str, Any], validation: Dict[str, Any], trace: Any) -> str:
    msg = f"""Site:\n{site_profile}

Selected option:\n{selected_option}

Validation:\n{validation}

Trace summary:\n{trace}

Write ADR-001."""
    resp = llm.invoke([("system", SYSTEM), ("user", msg)])
    return resp.content


