from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from aiv_de.observability.llm_logger import SafeLLMLogger
from aiv_de.config import SETTINGS

llm_logger = SafeLLMLogger(
    base_dir=SETTINGS.llm_log_dir,
    enabled=SETTINGS.log_llm_io,
)


SYSTEM = """You are the Architect for AIV-DE.
Propose 2-3 viable architectures that respect data residency.
Return JSON list of options with keys:
option_id, summary, placement, pipeline, hardware, pros, cons, risks, mitigations.
No vendor-locked claims. No precise performance numbers.
"""

class ArchitectureOptionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    option_id: str
    summary: str
    placement: Dict[str, str]
    pipeline: List[str]
    hardware: List[str] = Field(default_factory=list)
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    mitigations: List[str] = Field(default_factory=list)

class ArchitectureOptionsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    options: List[ArchitectureOptionModel]

def propose_options(
    llm: ChatOpenAI,
    site_profile: Dict[str, Any],
    requirements: Dict[str, Any],
    hw_db: List[Dict[str, Any]],
    vetoes: Optional[List[Dict[str, Any]]],
    run_id: str,
) -> Dict[str, Any]:
    hw_ids = [h.get("hw_id") for h in hw_db if h.get("hw_id")]
    veto_summary = vetoes or []
    schema_hint = (
        "Schema example:\n"
        "{\n"
        '  "options": [\n'
        "    {\n"
        '      "option_id": "OPT-1",\n'
        '      "summary": "Short summary",\n'
        '      "placement": {"inference": "edge", "storage": "onprem"},\n'
        '      "pipeline": ["roi_detection", "local_inference"],\n'
        '      "hardware": ["EDGE_GPU_25W_16GB"],\n'
        '      "pros": ["Low latency"],\n'
        '      "cons": ["Higher ops overhead"],\n'
        '      "risks": ["Drift across sites"],\n'
        '      "mitigations": ["Canary rollout"]\n'
        "    }\n"
        "  ]\n"
        "}\n"
    )
    msg = (
        "Site:\n"
        f"{site_profile}\n\n"
        "Requirements:\n"
        f"{requirements}\n\n"
        "Vetoes from last validation (if any):\n"
        f"{veto_summary}\n\n"
        "Available hardware IDs (choose 1+ per option):\n"
        f"{hw_ids}\n\n"
        f"{schema_hint}"
        "Return structured options only."
    )
    structured_llm = llm.with_structured_output(
        ArchitectureOptionsResponse, method="function_calling"
    )
    last_error: Optional[str] = None
    resp: Optional[ArchitectureOptionsResponse] = None
    for _ in range(2):
        messages = [("system", SYSTEM), ("user", msg)]
        if last_error:
            messages.append(
                (
                    "user",
                    "Previous output failed validation. Fix and return only the "
                    f"schema-conformant tool output. Error: {last_error}",
                )
            )
        try:
            resp = structured_llm.invoke(messages)
            break
        except ValidationError as exc:
            last_error = str(exc)

    if resp is None:
        return {"options": [], "error": last_error or "validation_failed"}

    llm_logger.log(
        run_id=run_id,
        agent="architect",
        phase="json_list",
        prompt=msg,
        response=json.dumps(resp.model_dump(), ensure_ascii=True),
       meta={"site_id": site_profile.get("site_id")},
    )


    return {"options": [opt.model_dump() for opt in resp.options]}
