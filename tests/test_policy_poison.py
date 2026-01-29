import json
from pathlib import Path

from aiv_de.graph import load_policy_store
from aiv_de.tools.policy_check import policy_check
from aiv_de.config import SETTINGS


def test_poison_site_detected():
    sites_path = Path(SETTINGS.data_dir) / "sites.json"
    sites = json.load(open(sites_path, "r", encoding="utf-8"))
    site = next(s for s in sites if s["site_id"] == "POISON-12")
    policies = load_policy_store(SETTINGS.policy_dir)

    out = policy_check(site, {"placement": {}}, policies)
    assert out["passed"] is False
    assert "prompt_injection_detected" in out["violated_rules"]
