from __future__ import annotations

from aiv_de.graph import n_select


def main() -> None:
    state = {
        "options": [
            {
                "option_id": "OPT-1",
                "summary": "Option with missing hardware.",
                "placement": {"inference": "edge"},
                "pipeline": ["local_inference"],
                "hardware": [],
                "pros": [],
                "cons": [],
                "risks": [],
                "mitigations": [],
            }
        ],
        "hw_db": [{"hw_id": "EDGE_GPU_25W_16GB"}],
    }

    out = n_select(state)
    selected = out.get("selected_option", {})
    assert selected.get("hardware"), "expected hardware to be set for selected option"


if __name__ == "__main__":
    main()
