import pytest
from pydantic import ValidationError

from aiv_de.agents.architect import ArchitectureOptionsResponse


def test_valid_payload_parses():
    payload = {
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
    parsed = ArchitectureOptionsResponse.model_validate(payload)
    assert parsed.options[0].placement["inference"] == "edge"


def test_bad_placement_type_raises():
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
    with pytest.raises(ValidationError):
        ArchitectureOptionsResponse.model_validate(bad_payload)
