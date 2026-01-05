agents/ — LLM “roles” that generate structured outputs

These are the “brains,” but they’re constrained to play specific roles.

requirements_analyst.py

Reads a site profile and extracts constraints/missing info/assumptions

Think: “systems engineer reading a spec”

architect.py

Proposes 2–3 architecture options (edge/on-prem/hybrid), pipeline steps, and hardware IDs

Think: “principal architect proposing alternatives”

validator_governance.py

Doesn’t call the LLM — it calls tools.

Has veto authority

Think: “safety/compliance reviewer + performance reviewer”

adr_writer.py

Writes the final ADR in a standard structure