import json
import os
import sys
import uuid

from aiv_de.config import SETTINGS
from aiv_de.graph import compile_graph, load_policy_store


def parse_args(argv: list[str]) -> tuple[str, bool]:
    site_id = "DE-MUC-01"
    stream = True
    for arg in argv:
        if arg == "--stream":
            stream = True
        else:
            site_id = arg
    return site_id, stream


def main(site_id: str = "DE-MUC-01", stream: bool = False) -> None:
    run_id = uuid.uuid4().hex[:12]
    thread_id = str(uuid.uuid4())

    sites = json.load(open(os.path.join(SETTINGS.data_dir, "sites.json"), "r", encoding="utf-8"))
    hw_db = json.load(open(os.path.join(SETTINGS.data_dir, "hardware_specs.json"), "r", encoding="utf-8"))
    policies = load_policy_store(SETTINGS.policy_dir)

    # Look up the requested site, fail gracefully if not found
    site_index = {s["site_id"]: s for s in sites}
    if site_id not in site_index:
        valid_ids = sorted(site_index.keys())
        print(f"Error: site_id '{site_id}' not found.\nValid site IDs: {valid_ids}")
        sys.exit(1)
    site = site_index[site_id]

    app = compile_graph()

    inputs = {
        "run_id": run_id,
        "site_profile": site,
        "hw_db": hw_db,
        "policies": policies,
        "retries": 0,
        "max_retries": SETTINGS.max_retries,
        "hitl_required": False,
        "trace": [],
    }

    config = {"configurable": {"thread_id": thread_id}}

    if stream:
        final_state = None
        for event in app.stream(inputs, config=config):
            if isinstance(event, dict):
                print(json.dumps(event, ensure_ascii=True))
            else:
                print(event)
            if isinstance(event, dict):
                final_state = event

        if not (isinstance(final_state, dict) and ("adr" in final_state or "trace" in final_state)):
            out = app.invoke(inputs, config=config)
        else:
            out = final_state
    else:
        out = app.invoke(inputs, config=config)

    # Write artifacts
    adr_value = out.get("adr", "")
    if isinstance(adr_value, dict):
        adr_text = adr_value.get("adr", "")
        trace_value = adr_value.get("trace", out.get("trace", []))
    else:
        adr_text = adr_value
        trace_value = out.get("trace", [])

    os.makedirs("out", exist_ok=True)
    with open(f"out/{site_id}_ADR-001.md", "w", encoding="utf-8") as f:
        f.write(adr_text)
    with open(f"out/{site_id}_trace.json", "w", encoding="utf-8") as f:
        json.dump(trace_value, f, indent=2)

    print(f"[run_id={run_id}] Wrote out/{site_id}_ADR-001.md and out/{site_id}_trace.json")


if __name__ == "__main__":
    site_id, stream = parse_args(sys.argv[1:])
    main(site_id=site_id, stream=stream)
