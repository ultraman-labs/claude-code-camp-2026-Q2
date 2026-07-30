# 01 · Struct Skeleton (Python)

This is the Python Week 1 Step 1 port of the Ruby struct skeleton. Ruby is
the source of truth. The implementation keeps the data structures simple and
readable for learning.

## Data structures

`Tool` and `Message` are dataclasses. `Context` is a regular class because it
owns mutable message/tool collections and registration and append behavior.

- `Tool` stores a name, description, plain dictionary parameter schema, and
  the callable in its `block` field. The example stores the move callable but
  does not execute it. Tools are registered by name; a duplicate name replaces
  the previous tool. Parameter names are displayed deterministically as an
  insertion-ordered list such as `params=['direction']`.
- `Message` stores `role`, `content`, and optional `tool_use_id`. Messages are
  appended in order, and an ID tag is shown only when an ID is supplied.
- `Context` stores the task, system prompt, ordered messages, and name-keyed
  tools. `turn_count` is exactly the number of messages, matching Ruby's
  `messages.size`.

Tool descriptions use `str(description)[:41]` and messages use
`str(content)[:61]`, matching Ruby's inclusive ranges `[0..40]` and `[0..60]`.
Both representations append `...` unconditionally, including for short
values.

## Shared virtual environment

All Week 1 Python iterations use the shared environment at
`week1_baseline/python/.venv`. From the repository root:

```bash
python3 -m venv week1_baseline/python/.venv
source week1_baseline/python/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r week1_baseline/python/01_struct_skeleton/requirements.txt
```

The runner assumes the environment is already active and does not create or
activate it. This step uses `requirements.txt`; it does not use
`pyproject.toml` or an external framework.

## Running Step 1

From the repository root:

```bash
./week1_baseline/bin/python/01_struct_skeleton
```

The portable runner also works from another directory:

```bash
cd /tmp
/mnt/d/Tech/AI/Claude\ BC/claude-code-camp-2026-Q2/week1_baseline/bin/python/01_struct_skeleton
```

Direct execution from the implementation directory is also supported:

```bash
cd week1_baseline/python/01_struct_skeleton
python examples/example.py
```

The example reuses Step 0 configuration and Player task behavior, registers
the move tool, adds two messages, and prints the Ruby-style Config, Context,
Tool, and Message representations. It does not call an API, execute the
stored tool, connect to the MUD, or include a formal test suite.
