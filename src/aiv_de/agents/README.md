# agents/ -- LLM "roles" that generate structured outputs

Each agent is constrained to a specific role in the pipeline.

- **requirements_analyst.py** -- Extracts constraints, missing info, and assumptions from a site profile. Returns raw LLM text (structured extraction is a future enhancement).

- **architect.py** -- Proposes 2-3 architecture options (edge/on-prem/hybrid) with Pydantic schema enforcement (`extra="forbid"`) and a repair loop for validation failures. Receives veto feedback on retries.

- **validator_governance.py** -- Pure deterministic validator (no LLM). Calls feasibility and policy tools, combines vetoes. Has veto authority over the architect.

- **adr_writer.py** -- Writes the final ADR in a standard audit-ready structure using all context from the pipeline.
