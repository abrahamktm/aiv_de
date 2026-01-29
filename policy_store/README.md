# policy_store/ -- Governance as code

Enterprise policy layer defined in versioned YAML files.

- **eu_ai_act_policy.yaml** -- Risk tiers (unacceptable/high/limited/minimal). Safety lines trigger high-risk classification, forcing HITL and oversight requirements.

- **data_residency_policy.yaml** -- Enforces "no raw images to cloud" when residency is required. Defines required controls (encryption, access logging, least privilege).

- **hitl_policy.yaml** -- Defines escalation triggers: validator exhausted, impossible constraints, policy violations, high drift.

- **security_policy.yaml** -- Prompt injection detection patterns and response actions.

- **scoring_weights.yaml** -- Weights for future evaluator scoring (constraint satisfaction, ADR completeness, evidence quality, etc.).
