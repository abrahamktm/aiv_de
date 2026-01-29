from aiv_de.run_one import parse_args


def test_defaults():
    site_id, stream = parse_args([])
    assert site_id == "DE-MUC-01"
    assert stream is True


def test_custom_site_id():
    site_id, stream = parse_args(["POISON-12"])
    assert site_id == "POISON-12"
    assert stream is True


def test_site_id_with_stream_flag():
    site_id, stream = parse_args(["IMPOSSIBLE-11", "--stream"])
    assert site_id == "IMPOSSIBLE-11"
    assert stream is True
