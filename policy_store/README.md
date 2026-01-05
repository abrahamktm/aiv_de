policy_store/ — “Governance as code”

These YAML files are your enterprise policy layer.
They’re what turn this from “agent demo” into “decision engine.”

eu_ai_act_policy.yaml

Encodes a conservative risk stance: safety lines → “high-risk” behavior

Forces governance expectations (oversight, logging, escalation)

data_residency_policy.yaml

Enforces “no raw images to cloud” style constraints

hitl_policy.yaml

Defines when to escalate to humans (validator exhausted, impossible, policy violation, high drift)

security_policy.yaml

Defines prompt injection patterns and what to do when detected

scoring_weights.yaml

Later  used by the evaluator to compute a final score

policies are explicit, reviewable, testable, version-controlled.