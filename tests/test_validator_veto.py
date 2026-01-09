from __future__ import annotations

from aiv_de.agents.validator_governance import validate_and_veto


def main() -> None:
    site_profile = {
        "power_budget_w": 10,
        "use_case": "safety_line",
        "latency_budget_ms": 50,
    }
    selected_option = {
        "placement": {"inference": "edge", "storage": "onprem"},
        "pipeline": ["local_inference"],
        "hardware": ["EDGE_GPU_25W_16GB"],
    }
    hw_db = [
        {"hw_id": "EDGE_GPU_25W_16GB", "class": "edge", "power_class_w": "15-30"}
    ]
    policy_store = {"data_residency_policy": {}, "security_policy": {}}

    out = validate_and_veto(site_profile, selected_option, hw_db, policy_store)
    veto_reasons = [v["reason"] for v in out["vetoes"]]
    assert "Feasibility failed" in veto_reasons
    assert "power_budget_exceeded_for_edge_hw" in out["feasibility"]["bottlenecks"]


if __name__ == "__main__":
    main()
