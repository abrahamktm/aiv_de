# src/aiv_de/ -- Product code

## Core plumbing

- **config.py** -- Reads `.env` (paths, model name, retry count). Keeps the code portable.
- **types.py** -- Defines the state schema (TypedDict contract between agents).

## graph.py -- The orchestrator (LangGraph)

Wires nodes into a state machine:

```
requirements --> architect --> select --> validate
                                           |
                    +----------------------+---------------------+
                    v                      v                     v
                 adr_writer           revise-->architect      hitl escalation
                (no vetoes)        (vetoes + retries left)  (retries exhausted)
```

- Uses SQLite checkpointer for state persistence by `thread_id`
- Each node logs `duration_s` into the trace
- Revise node logs veto feedback so the architect can self-correct

## run_one.py -- CLI entry point

- Loads sites, hardware DB, and policy store
- Runs one site through the graph
- Writes `out/<site_id>_ADR-001.md` and `out/<site_id>_trace.json`
- Graceful error if site_id not found (prints valid IDs)
