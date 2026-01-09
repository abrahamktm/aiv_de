from __future__ import annotations

from aiv_de.graph import route_after_validate


def main() -> None:
    assert route_after_validate({"vetoes": []}) == "adr"
    assert route_after_validate({"vetoes": [{"reason": "x"}], "hitl_required": False}) == "revise"
    assert route_after_validate({"vetoes": [{"reason": "x"}], "hitl_required": True}) == "hitl"


if __name__ == "__main__":
    main()
