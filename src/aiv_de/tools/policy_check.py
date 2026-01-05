from __future__ import annotations
from typing import Any, Dict, List, Optional
import re

def detect_prompt_injection(text: str, patterns: List[str]) -> bool:
    t = text.lower()
    for p in patterns:
        if re.search(re.escape(p.lower()), t):
            return True
    return False

def policy_check(site_profile: Dict[str, Any], selected_option: Dict[str, Any], policy_store: Dict[str, Any]) -> Dict[str, Any]:
    violated: List[str] = []
    required_controls: List[str] = []

    # Data residency rule
    dr = policy_store.get("data_residency_policy", {})
    rules = dr.get("rules", [])
    if site_profile.get("data_residency_required", False):
        # We encode a simple: no cloud inference/storage if residency required
        placement = selected_option.get("placement", {})
        if any(v == "cloud" for v in placement.values()):
            violated.append("no_raw_to_cloud")

        for r in rules:
            if r.get("id") == "no_raw_to_cloud":
                required_controls.extend(r.get("then", {}).get("required_controls", []))

    # Prompt-injection check (if site includes poison_doc)
    sec = policy_store.get("security_policy", {})
    inj = sec.get("prompt_injection", {})
    patterns = inj.get("patterns", [])
    poison = site_profile.get("poison_doc", {})
    if poison.get("enabled") and detect_prompt_injection(poison.get("example_text", ""), patterns):
        violated.append("prompt_injection_detected")

    passed = len(violated) == 0
    hitl_action: Optional[str] = None
    if not passed:
        hitl_action = "BLOCK_AND_ESCALATE"

    return {
        "passed": passed,
        "violated_rules": violated,
        "required_controls": sorted(set(required_controls)),
        "hitl_action": hitl_action,
    }
