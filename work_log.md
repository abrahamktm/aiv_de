# Work Log

- Task: Explain execution path for `run_one` (entrypoint -> graph -> agents -> tools) and provide a short map of files/responsibilities.
- Actions:
  - Listed repository contents to locate relevant modules.
  - Read `src/aiv_de/run_one.py` to identify entrypoint and runtime flow.
  - Read `src/aiv_de/graph.py` to map graph nodes, routing, and checkpointing.
  - Read agent modules to understand LLM and validation steps.
  - Read tool modules to capture feasibility and policy checks.
  - Read `src/aiv_de/types.py` for shared state/structures.
- Outcome: Provided a concise execution-path summary and file responsibility map in the chat response.

## Files Inspected

- `README.md`
- `src/aiv_de/run_one.py`
- `src/aiv_de/graph.py`
- `src/aiv_de/agents/requirements_analyst.py`
- `src/aiv_de/agents/architect.py`
- `src/aiv_de/agents/validator_governance.py`
- `src/aiv_de/agents/adr_writer.py`
- `src/aiv_de/tools/validate_feasibility.py`
- `src/aiv_de/tools/policy_check.py`
- `src/aiv_de/tools/lookup_hardware.py`
- `src/aiv_de/types.py`

## Run: 2026-01-05

- Action: Activated `.venv`, set `PYTHONPATH=src`, and ran `python -m aiv_de.run_one`.
- Result: Completed with HITL escalation after retries; no feasible hardware selected in options.
- Outputs:
  - `out/DE-MUC-01_ADR-001.md`
  - `out/DE-MUC-01_trace.json`

## Task: Execution path summary (repeat request)

- Action: Re-summarized `run_one` execution path and file responsibility map in chat.
- Files referenced (from prior reads):
  - `src/aiv_de/run_one.py`
  - `src/aiv_de/graph.py`
  - `src/aiv_de/agents/requirements_analyst.py`
  - `src/aiv_de/agents/architect.py`
  - `src/aiv_de/agents/validator_governance.py`
  - `src/aiv_de/agents/adr_writer.py`
  - `src/aiv_de/tools/validate_feasibility.py`
  - `src/aiv_de/tools/policy_check.py`
  - `src/aiv_de/tools/lookup_hardware.py`
  - `src/aiv_de/types.py`

## Change: Structured architect output + selection fallback + test

- Updated `src/aiv_de/agents/architect.py` to use Pydantic structured output, include available hardware IDs, and return structured options.
- Updated `src/aiv_de/graph.py` to consume structured options and ensure selected options include a fallback hardware ID.
- Added `tests/test_select_hardware.py` to assert hardware is set when an option lacks it.

## Request: Show where hardware list is added

- Provided code snippets from `src/aiv_de/agents/architect.py` (structured output prompt includes hardware IDs) and `src/aiv_de/graph.py` (fallback hardware injection in `n_select`).

## Change: Production-style structured outputs + repair loop

- Updated `src/aiv_de/agents/architect.py` with strict schema (`extra=forbid`), coercion validators for placement/list fields, schema hint in prompt, and a repair loop + fallback option.
- Ran `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='src'; python -m aiv_de.run_one`.
- Result: Structured options returned with hardware populated; flow still escalated due to power budget feasibility (`power_budget_exceeded_for_edge_hw`).
- Outputs:
  - `out/DE-MUC-01_ADR-001.md`
  - `out/DE-MUC-01_trace.json`

## Q&A: Option 2 demo change

- Explained that raising the site power budget in `data/sites.json` (e.g., DE-MUC-01 `power_budget_w` >= 30 for EDGE_GPU_25W_16GB) would avoid the `power_budget_exceeded_for_edge_hw` veto.
- Noted that option 2 is a demo shortcut vs production constraint enforcement.

## Rework: Strict architect output + veto feedback + demo power budget + run fix

- Removed coercion/fallback in `src/aiv_de/agents/architect.py`; added vetoes to prompt and explicit validation failure handling.
- Updated `src/aiv_de/graph.py` to pass vetoes to architect and record validation failures in trace.
- Raised `DE-MUC-01` power budget to 30W in `data/sites.json` for demo happy path.
- Fixed `src/aiv_de/run_one.py` to handle streamed ADR payloads when `adr` is nested dict.

## Fix: Stream printing on Windows console

- Updated `src/aiv_de/run_one.py` to print stream events with `json.dumps(..., ensure_ascii=True)` to avoid CP1252 UnicodeEncodeError.

## Run: Happy-path ADR (demo shortcut)

- Command: `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH=src; python -m aiv_de.run_one`
- Result: Non-HITL ADR generated for DE-MUC-01.
- Outputs:
  - `out/DE-MUC-01_ADR-001.md`
  - `out/DE-MUC-01_trace.json`

## Runs for POISON/IMPOSSIBLE

- Attempted `python -m aiv_de.run_one POISON-12` and `IMPOSSIBLE-11`, but CLI currently ignores argv so it still ran DE-MUC-01.
- Need to add CLI arg parsing in `src/aiv_de/run_one.py` to allow site_id selection for poison/impossible traces.

## CLI arg support + POISON/IMPOSSIBLE runs

- Added CLI arg parsing in `src/aiv_de/run_one.py` for site_id and `--stream`.
- Ran `python -m aiv_de.run_one POISON-12` -> produced vetoes, retries, HITL escalation.
- Ran `python -m aiv_de.run_one IMPOSSIBLE-11` -> produced feasibility vetoes, retries, HITL escalation.
- Outputs:
  - `out/POISON-12_ADR-001.md`
  - `out/POISON-12_trace.json`
  - `out/IMPOSSIBLE-11_ADR-001.md`
  - `out/IMPOSSIBLE-11_trace.json`

## Added architecture diagram and demo script

- Inserted Mermaid architecture flow and demo commands into `README.md`.

## Tests added

- Added tests for architect schema validation, validator veto on power budget, policy poison detection, graph routing, and CLI arg parsing.
- Added `parse_args` helper in `src/aiv_de/run_one.py` to support CLI parsing tests.

## Code Review and Cleanup (2026-01-29)

Full review of all source files, tests, data, and policies.

### Issues Found

#### Redundant inline comments
Every file had end-of-line comments restating the code. Stripped all of them
to improve readability.

#### Duplicate imports in graph.py
`SqliteSaver` and `SETTINGS` imported twice. Commented-out old `compile_graph` left in.
Cleaned up.

#### Verbose schema hint in architect.py
18-line string concatenation replaced with triple-quoted string.

#### Stray debug global in config.py
`AIVDE_ANNOTATE_ADR=1` was outside the Settings class and unused.

### Improvements Added

1. **Timing in trace entries** — `duration_s` per node for production awareness.
2. **Veto feedback in revise trace** — audit trail now shows what the architect
   received on retry.
3. **Graceful error on bad site_id** — prints valid IDs instead of crashing.
4. **Converted tests to pytest style** — `test_*()` functions, discoverable by pytest.
5. **Removed stray config global.**

## Changes Applied (2026-01-29)

All planned changes implemented and verified. 11/11 tests pass.

### Code cleanup (human-readable)
- Stripped all ChatGPT echo comments from: graph.py, architect.py, adr_writer.py, llm_logger.py, run_one.py, lookup_hardware.py
- Removed duplicate imports and commented-out code in graph.py
- Replaced verbose string-concatenation schema hint in architect.py with triple-quoted string
- Removed `from __future__ import annotations` where unnecessary
- Config.py stray global already cleaned by linter

### Features added
- **Timing in trace**: every LLM-calling node now logs `duration_s` (graph.py)
- **Veto feedback in revise trace**: `n_revise()` now logs `veto_feedback` list so the audit trail shows what the architect received on retry
- **Graceful bad site_id**: run_one.py prints valid IDs and exits cleanly instead of crashing with StopIteration

### Tests
- All 6 test files converted to pytest style (`test_*()` functions, no `if __name__` blocks)
- Installed pytest in venv
- 11/11 tests pass

### READMEs updated
- Main README.md: rewrote from scratch (removed mojibake, outdated Day-2 references, wrong run commands). Now accurate and concise.
- src/aiv_de/README.md: reformatted with markdown structure
- agents/README.md: updated to reflect structured output + repair loop
- tools/README.md: reformatted with markdown
- data/README.md: reformatted with markdown
- policy_store/README.md: reformatted with markdown

### Files modified
- src/aiv_de/graph.py
- src/aiv_de/agents/architect.py
- src/aiv_de/agents/adr_writer.py
- src/aiv_de/run_one.py
- src/aiv_de/observability/llm_logger.py
- src/aiv_de/tools/lookup_hardware.py
- tests/test_cli_args.py
- tests/test_route_after_validate.py
- README.md
- src/aiv_de/README.md
- src/aiv_de/agents/README.md
- src/aiv_de/tools/README.md
- data/README.md
- policy_store/README.md
