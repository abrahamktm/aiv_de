from __future__ import annotations

import json
import os
import uuid

from aiv_de.config import SETTINGS
from aiv_de.graph import compile_graph, load_policy_store


def main(site_id: str = "DE-MUC-01", stream: bool = False) -> None:
    run_id = uuid.uuid4().hex[:12]
    thread_id = str(uuid.uuid4())

    sites = json.load(open(os.path.join(SETTINGS.data_dir, "sites.json"), "r", encoding="utf-8"))
    hw_db = json.load(open(os.path.join(SETTINGS.data_dir, "hardware_specs.json"), "r", encoding="utf-8"))
    policies = load_policy_store(SETTINGS.policy_dir)

    site = next(s for s in sites if s["site_id"] == site_id)

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

    # Run graph
    if stream:
        final_state = None
        for event in app.stream(inputs, config=config):
            # event is typically a dict of updates; printing helps you see progress
            print(event)
            # Keep updating final_state; last one will be the most complete
            if isinstance(event, dict):
                final_state = event
        # In some LangGraph versions, stream yields incremental updates rather than final state.
        # So, safest is: if we didn't end up with a dict containing "adr", fall back to invoke once.
        if not (isinstance(final_state, dict) and ("adr" in final_state or "trace" in final_state)):
            out = app.invoke(inputs, config=config)
        else:
            out = final_state
    else:
        out = app.invoke(inputs, config=config)

    # Write artifacts
    os.makedirs("out", exist_ok=True)
    with open(f"out/{site_id}_ADR-001.md", "w", encoding="utf-8") as f:
        f.write(out.get("adr", ""))
    with open(f"out/{site_id}_trace.json", "w", encoding="utf-8") as f:
        json.dump(out.get("trace", []), f, indent=2)

    print(f"[run_id={run_id}] Wrote out/{site_id}_ADR-001.md and out/{site_id}_trace.json")


if __name__ == "__main__":
    #main()
    main(stream=True)

