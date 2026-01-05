from __future__ import annotations
from typing import Any, Dict
from langchain_openai import ChatOpenAI

from aiv_de.observability.llm_logger import SafeLLMLogger
from aiv_de.config import SETTINGS

llm_logger = SafeLLMLogger(
    base_dir=SETTINGS.llm_log_dir,
    enabled=SETTINGS.log_llm_io,
)


SYSTEM = """You are the Requirements Analyst for AIV-DE.
Extract constraints, categorize safety vs quality, and list assumptions.
Be concise, structured JSON only.
"""

def run_requirements(llm: ChatOpenAI, site_profile: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    msg = f"Site profile:\n{site_profile}\n\nReturn JSON with keys: constraints, missing_info, assumptions."
    resp = llm.invoke([("system", SYSTEM), ("user", msg)])
    # Keep skeleton simple: store raw text; parse later if desired

    llm_logger.log(
        run_id=run_id,
        agent="requirements_analyst",
        phase="extract_constraints",
        prompt=msg,                     # <-- use msg
        response=resp.content,
        meta={"site_id": site_profile.get("site_id")},
    )

    
    return {"raw": resp.content}

