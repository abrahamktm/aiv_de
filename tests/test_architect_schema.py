from __future__ import annotations

from pydantic import ValidationError

from aiv_de.agents.architect import ArchitectureOptionsResponse


def main() -> None:
    ok_payload = {
        "options": [
            {
                "option_id": "OPT-1",
                "summary": "Edge inference with on-prem storage.",
                "placement": {"inference": "edge", "storage": "onprem"},
                "pipeline": ["roi_detection", "local_inference"],
                "hardware": ["EDGE_GPU_25W_16GB"],
                "pros": ["Low latency"],
                "cons": ["Ops overhead"],
                "risks": ["Drift"],
                "mitigations": ["Canary rollout"],
            }
        ]
    }
    parsed = ArchitectureOptionsResponse.model_validate(ok_payload)
    assert parsed.options[0].placement["inference"] == "edge"

    bad_payload = {
        "options": [
            {
                "option_id": "OPT-1",
                "summary": "Bad placement type.",
                "placement": "edge",
                "pipeline": ["roi_detection"],
                "hardware": ["EDGE_GPU_25W_16GB"],
                "pros": [],
                "cons": [],
                "risks": [],
                "mitigations": [],
            }
        ]
    }
    try:
        ArchitectureOptionsResponse.model_validate(bad_payload)
    except ValidationError:
        return
    raise AssertionError("expected ValidationError for invalid placement type")


if __name__ == "__main__":
    main()
