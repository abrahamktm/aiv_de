# tools/ -- Deterministic validation layer

These are the non-LLM guardrails. "LLM proposes, tools dispose."

- **lookup_hardware.py** -- Resolves hardware IDs from architect proposals against the known hardware DB. Marks unknown IDs.

- **validate_feasibility.py** -- Engineering sanity checks:
  - Power budget vs edge hardware class
  - Safety-line latency vs cloud dependency
  - Multi-cam / high-fps / high-res vs low power (infeasible)
  - Returns: `is_possible`, `margin`, `bottlenecks`, `suggested_pipeline`

- **policy_check.py** -- Governance enforcement:
  - Data residency: blocks cloud placement if residency is required
  - Prompt injection: regex detection against security policy patterns
  - Returns: `passed`, `violated_rules`, `required_controls`, `hitl_action`
