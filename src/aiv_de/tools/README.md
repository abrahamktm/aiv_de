tools/ — deterministic, auditable, “no hallucination” layer

These are the non-LLM parts that make decisions defensible.

lookup_hardware.py

Takes hardware IDs from the architecture proposal and resolves them into known hardware records.

validate_feasibility.py

Quick “engineering sanity check”:

power budget vs edge box class

safety latency vs cloud dependency

multi-cam/high-fps/high-res vs low power → likely impossible

Outputs: is_possible + margin + bottlenecks + suggested_pipeline

policy_check.py

Enforces policy store:

data residency rules

prompt injection detection (POISON site)

Outputs: passed/failed + violated rules + required controls + HITL action

Key idea: LLM proposes, tools dispose.
The LLM is not allowed to be “the final authority.”