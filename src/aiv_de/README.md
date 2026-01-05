src/aiv_de/ — the “product code”

This is the engine.

Core plumbing

config.py

Reads .env (paths, model name, retry count)

Keeps your code portable across Windows/Mac/Linux

types.py

Defines the “contract” between agents (state schema)

Prevents “random dict soup” as your project grows


graph.py — the orchestrator (LangGraph)

This is the most important “agentic” part.

It wires nodes into a state machine:

requirements → architect → select → validate

After validate, it chooses a route:

If no vetoes → adr

If vetoes and retries left → revise → back to architect

If vetoes and retries exhausted → hitl

Also:

It uses SQLite checkpointer so state can be persisted by thread_id

That’s your “episodic memory foundation” (Day-1 baseline)

Think of it like: agent workflow = a compiled decision graph, not a script.

run_one.py — the CLI entry point

This is the “product interface” for now:

loads sites.json, hardware_specs.json, and policy_store/

runs one site through the graph

writes:

out/<site>_ADR-001.md

out/<site>_trace.json

This is what you demo in interviews.