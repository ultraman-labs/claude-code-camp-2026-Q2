# 02 · The Tool Registry (Python)

This is the Python Week 1 Step 2 port of the verified Ruby Tool Registry.
Ruby remains the source of truth, and this snapshot preserves the Step 1
configuration, task, message, context, tool, prompt, and representation
behavior.

## Registry design

`Context` continues to own the mutable `tools` mapping. `Registry` receives an
existing context and owns tool creation, registration, lookup, and dispatch
behavior without creating a second tool store.

`Registry.tool()` accepts a name, keyword-only description, optional
parameters, and a keyword-only `block` callable. Names are normalized with
`str()`. Omitted parameters become a fresh empty dictionary for each
registration. The method creates a `Tool`, registers it through
`Context.register_tool()`, and returns the same instance. Duplicate names
replace the existing context entry, matching Python dictionary and Ruby Hash
behavior.

`Registry.dispatch()` accepts a name and optional argument mapping. It
normalizes the name and looks up the tool only through `Context.tools`. It
normalizes argument keys with `str(key)`, invokes the stored callable with
keyword arguments, and returns the callable's result directly. A missing tool
raises `UnknownToolError` from `boukensha/errors.py` with the exact message
`No tool registered as 'flee'` for the example case.

The example manually dispatches `shout` and `move`; an LLM does not yet decide
when to dispatch tools.

## Shared virtual environment

All Week 1 Python iterations use `week1_baseline/python/.venv`. From the
repository root:

```bash
python3 -m venv week1_baseline/python/.venv
source week1_baseline/python/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r week1_baseline/python/02_the_registry/requirements.txt
```

This step uses `requirements.txt` with `PyYAML` and `python-dotenv`. It does
not use `pyproject.toml`, Pydantic, attrs, Poetry, an agent SDK, or a formal
test suite. The runner assumes the shared environment is already active and
does not create or activate it.

## Run the example

From the repository root:

```bash
./week1_baseline/bin/python/02_the_registry
```

From `/tmp`:

```bash
cd /tmp
/mnt/d/Tech/AI/Claude\ BC/claude-code-camp-2026-Q2/week1_baseline/bin/python/02_the_registry
```

The example defaults `BOUKENSHA_DIR` to the repository-root `.boukensha`
directory, independent of the current working directory. It prints both
registered tools, `DRAGON SPOTTED`,
`You move north into a torch-lit corridor.`, and
`UnknownToolError caught: No tool registered as 'flee'`.
