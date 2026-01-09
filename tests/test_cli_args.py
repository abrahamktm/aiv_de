from __future__ import annotations

from aiv_de.run_one import parse_args


def main() -> None:
    site_id, stream = parse_args([])
    assert site_id == "DE-MUC-01"
    assert stream is True

    site_id, stream = parse_args(["POISON-12"])
    assert site_id == "POISON-12"
    assert stream is True

    site_id, stream = parse_args(["IMPOSSIBLE-11", "--stream"])
    assert site_id == "IMPOSSIBLE-11"
    assert stream is True


if __name__ == "__main__":
    main()
