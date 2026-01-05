data/ — “Ground truth inputs” (public-safe)

This is your scenario simulation world.

sites.json: synthetic factories with different constraints (power, latency, WAN, drift).

Includes IMPOSSIBLE to prove refusal/escalation

Includes POISON to prove injection resistance

hardware_specs.json: curated hardware capability DB, coarse by design (safe + defensible).

Your tools reference this instead of LLM guessing hardware.

separated “facts” from “LLM text.”