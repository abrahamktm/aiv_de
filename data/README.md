# data/ -- Ground-truth inputs

Synthetic but realistic test data. Facts are separated from LLM text.

- **sites.json** -- 12 factory site profiles across Europe with constraints (power, latency, WAN, cameras, drift tolerance). Includes two adversarial cases:
  - `IMPOSSIBLE-11` -- contradictory constraints to prove safe refusal/escalation
  - `POISON-12` -- prompt injection payload to prove injection resistance

- **hardware_specs.json** -- Curated hardware capability DB (7 profiles: edge CPU/GPU, on-prem CPU/GPU). Power ratings are intentionally coarse ranges to avoid false precision.
