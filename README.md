cd aiv-de
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env


python -m src.aiv_de.run_one
python -m src.aiv_de.run_one POISON-12
python -m src.aiv_de.run_one IMPOSSIBLE-11

---

## Architecture Overview

```mermaid
flowchart TD
  A[run_one.py CLI] --> B[graph.py / LangGraph]
  B --> C[requirements_analyst]
  C --> D[architect]
  D --> E[select]
  E --> F[validator_governance]
  F -->|no vetoes| G[adr_writer]
  F -->|vetoes + retries left| D
  F -->|vetoes + retries exhausted| H[hitl escalation]
  G --> I[ADR + trace]
  H --> I[ADR + trace]
```

## Demo Script

```powershell
# Happy path (ADR generated)
python -m src.aiv_de.run_one DE-MUC-01

# Policy veto + HITL escalation (prompt injection)
python -m src.aiv_de.run_one POISON-12

# Feasibility veto + HITL escalation (impossible constraints)
python -m src.aiv_de.run_one IMPOSSIBLE-11
```

Expected outputs:
- `out/DE-MUC-01_ADR-001.md` and `out/DE-MUC-01_trace.json`
- `out/POISON-12_ADR-001.md` and `out/POISON-12_trace.json`
- `out/IMPOSSIBLE-11_ADR-001.md` and `out/IMPOSSIBLE-11_trace.json`


Cool â€” you basically just created a *mini â€œenterprise architecture decision factoryâ€*.

Hereâ€™s whatâ€™s going on, file-by-file, and how the whole thing behaves when you run it.

---

## The big picture: what AIV-DE does in one run

Input: **one factory site profile** (constraints + realities)
Output: **ADR-001** (auditable architecture decision) + **trace log** (why/how it decided)

Under the hood:

1. Requirements Analyst extracts constraints/assumptions
2. Architect proposes architectures
3. Validator + Governance runs **deterministic tools** and can **veto**
4. If veto â†’ revise and try again (limited retries)
5. If still bad â†’ **HITL escalation**
6. If OK â†’ ADR writer produces the final ADR

---

## Folder roles (why this structure looks â€œenterpriseâ€)

### `data/` â€” â€œGround truth inputsâ€ (public-safe)

This is your *scenario simulation world*.

* **`sites.json`**: synthetic factories with different constraints (power, latency, WAN, drift).

  * Includes **IMPOSSIBLE** to prove refusal/escalation
  * Includes **POISON** to prove injection resistance
* **`hardware_specs.json`**: curated hardware capability DB, **coarse** by design (safe + defensible).

  * Your tools reference this instead of LLM guessing hardware.

**Why interviewers like this:** you separated â€œfactsâ€ from â€œLLM text.â€

---

### `policy_store/` â€” â€œGovernance as codeâ€

These YAML files are your **enterprise policy layer**.
Theyâ€™re what turn this from â€œagent demoâ€ into â€œdecision engine.â€

* **`eu_ai_act_policy.yaml`**

  * Encodes a conservative risk stance: safety lines â†’ â€œhigh-riskâ€ behavior
  * Forces governance expectations (oversight, logging, escalation)
* **`data_residency_policy.yaml`**

  * Enforces â€œno raw images to cloudâ€ style constraints
* **`hitl_policy.yaml`**

  * Defines when to escalate to humans (validator exhausted, impossible, policy violation, high drift)
* **`security_policy.yaml`**

  * Defines prompt injection patterns and what to do when detected
* **`scoring_weights.yaml`**

  * Later (Day-5) used by the evaluator to compute a final score

**Why interviewers like this:** policies are explicit, reviewable, testable, version-controlled.

---

### `src/aiv_de/` â€” the â€œproduct codeâ€

This is the engine.

#### Core plumbing

* **`config.py`**

  * Reads `.env` (paths, model name, retry count)
  * Keeps your code portable across Windows/Mac/Linux
* **`types.py`**

  * Defines the â€œcontractâ€ between agents (state schema)
  * Prevents â€œrandom dict soupâ€ as your project grows

#### `tools/` â€” deterministic, auditable, â€œno hallucinationâ€ layer

These are the *non-LLM* parts that make decisions defensible.

* **`lookup_hardware.py`**

  * Takes `hardware` IDs from the architecture proposal and resolves them into known hardware records.
* **`validate_feasibility.py`**

  * Quick â€œengineering sanity checkâ€:

    * power budget vs edge box class
    * safety latency vs cloud dependency
    * multi-cam/high-fps/high-res vs low power â†’ likely impossible
  * Outputs: is_possible + margin + bottlenecks + suggested_pipeline
* **`policy_check.py`**

  * Enforces policy store:

    * data residency rules
    * prompt injection detection (POISON site)
  * Outputs: passed/failed + violated rules + required controls + HITL action

**Key idea:** LLM proposes, tools dispose.
The LLM is not allowed to be â€œthe final authority.â€

---

#### `agents/` â€” LLM â€œrolesâ€ that generate structured outputs

These are the â€œbrains,â€ but theyâ€™re constrained to play specific roles.

* **`requirements_analyst.py`**

  * Reads a site profile and extracts constraints/missing info/assumptions
  * Think: â€œsystems engineer reading a specâ€
* **`architect.py`**

  * Proposes 2â€“3 architecture options (edge/on-prem/hybrid), pipeline steps, and hardware IDs
  * Think: â€œprincipal architect proposing alternativesâ€
* **`validator_governance.py`**

  * Doesnâ€™t call the LLM â€” it calls tools.
  * Has veto authority
  * Think: â€œsafety/compliance reviewer + performance reviewerâ€
* **`adr_writer.py`**

  * Writes the final ADR in a standard structure

---

### `graph.py` â€” the *orchestrator* (LangGraph)

This is the most important â€œagenticâ€ part.

It wires nodes into a state machine:

* `requirements` â†’ `architect` â†’ `select` â†’ `validate`
* After `validate`, it chooses a route:

  * If no vetoes â†’ `adr`
  * If vetoes and retries left â†’ `revise` â†’ back to `architect`
  * If vetoes and retries exhausted â†’ `hitl`

Also:

* It uses **SQLite checkpointer** so state can be persisted by thread_id

  * Thatâ€™s your â€œepisodic memory foundationâ€ (Day-1 baseline)

Think of it like: *agent workflow = a compiled decision graph*, not a script.

---

### `run_one.py` â€” the CLI entry point

This is the â€œproduct interfaceâ€ for now:

* loads `sites.json`, `hardware_specs.json`, and `policy_store/`
* runs one site through the graph
* writes:

  * `out/<site>_ADR-001.md`
  * `out/<site>_trace.json`

This is what you demo in interviews.

---

## What happens when you run the POISON and IMPOSSIBLE cases?

### `POISON-12`

* Site includes `poison_doc.example_text` with â€œIGNORE ALL PREVIOUSâ€¦â€
* `policy_check.py` detects injection patterns (from `security_policy.yaml`)
* Validator returns a veto â†’ either:

  * revise (if retries left), or
  * HITL escalation if retry budget is exhausted

**This proves:** injection-aware architecture decisions, not doc-following.

### `IMPOSSIBLE-11`

* Constraints are intentionally contradictory: ultra-low latency + ultra-low power + many cameras + high fps
* `validate_feasibility.py` flags infeasible (bottlenecks)
* After retries â†’ HITL escalation ADR

**This proves:** refusal and safe escalation.

---

## Why the current skeleton feels â€œroughâ€ (and thatâ€™s intentional)

Right now the `architect.py` returns **raw JSON text**, and `graph.py` stores it as a placeholder option (`RAW_OPTIONS`) until you implement parsing + validation.

Thatâ€™s not a bug â€” itâ€™s the intended Day-2/Day-3 build step:

* Add Pydantic schema parsing
* If architect output invalid â†’ validator rejects â†’ architect retries
* That becomes your â€œself-correction loopâ€ with real structure

---

## One mental model (how to explain to an interviewer)

> â€œI treat the LLM as a proposal generator.
> Deterministic validators enforce physics (power/latency) and governance (residency/security).
> A LangGraph state machine controls retries and HITL escalation.
> Every run produces an ADR plus a full trace of tools/vetoes for auditability.â€

Thatâ€™s the whole story.

---

If you want the next step without any extra discussion: I can give you **Day-2 upgrade** that makes this â€œrealâ€:

* strict Pydantic models for `ArchitectureOption`
* parse/validate Architect JSON
* if invalid JSON or missing fields â†’ automatic retry with feedback
* generate a Mermaid graph from the `trace.json` automatically
