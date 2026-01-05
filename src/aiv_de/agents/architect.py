from __future__ import annotations
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI

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

def propose_options(llm: ChatOpenAI, site_profile: Dict[str, Any], requirements: Dict[str, Any],  run_id: str) -> Dict[str, Any]:
    msg = f"Site:\n{site_profile}\n\nRequirements:\n{requirements}\n\nReturn JSON list only."
    resp = llm.invoke([("system", SYSTEM), ("user", msg)])

    llm_logger.log(
        run_id=run_id,
        agent="architect",
        phase="json_list",
        prompt=msg,
        response=resp.content,
       meta={"site_id": site_profile.get("site_id")},
    )


    return {"raw": resp.content}
