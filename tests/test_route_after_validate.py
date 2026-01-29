from aiv_de.graph import route_after_validate


def test_no_vetoes_routes_to_adr():
    assert route_after_validate({"vetoes": []}) == "adr"


def test_vetoes_with_retries_routes_to_revise():
    assert route_after_validate({"vetoes": [{"reason": "x"}], "hitl_required": False}) == "revise"


def test_vetoes_exhausted_routes_to_hitl():
    assert route_after_validate({"vetoes": [{"reason": "x"}], "hitl_required": True}) == "hitl"
