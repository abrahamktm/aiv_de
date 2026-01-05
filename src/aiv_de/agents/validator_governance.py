from __future__ import annotations
from typing import Any, Dict, List

from aiv_de.tools.validate_feasibility import validate_feasibility
from aiv_de.tools.policy_check import policy_check

def validate_and_veto(
    site_profile: Dict[str, Any],
    selected_option: Dict[str, Any],
    hw_db: List[Dict[str, Any]],
    policy_store: Dict[str, Any]
) -> Dict[str, Any]:
    feasibility = validate_feasibility(site_profile, selected_option, hw_db)
    policy = policy_check(site_profile, selected_option, policy_store)

    vetoes: List[Dict[str, Any]] = []
    if not feasibility["is_possible"]:
        vetoes.append({"reason": "Feasibility failed", "violated_rules": feasibility["bottlenecks"]})
    if not policy["passed"]:
        vetoes.append({"reason": "Policy failed", "violated_rules": policy["violated_rules"]})

    return {"feasibility": feasibility, "policy": policy, "vetoes": vetoes}
