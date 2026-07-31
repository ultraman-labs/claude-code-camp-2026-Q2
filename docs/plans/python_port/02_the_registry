# Python Port Plan: `02_the_registry`

## Goal

Port the Ruby Week 1 Step 2 Tool Registry to Python while preserving the
verified Ruby architecture and behavior. This is a snapshot-style extension
of Step 1, not a redesign.

Ruby remains the source of truth:

```text
week1_baseline/ruby/02_the_registry
week1_baseline/bin/ruby/02_the_registry
```

Reuse and extend the previous Python snapshot:

```text
week1_baseline/python/01_struct_skeleton
week1_baseline/bin/python/01_struct_skeleton
```

Do not implement Python code as part of this plan. Do not modify unrelated
files, commit, or push anything.

## Behavioral contract

The port must retain these responsibilities and boundaries:

- `Context` owns the mutable `tools` mapping and continues to replace a
  previous tool when a duplicate name is registered.
- `Registry` receives an existing `Context`; it does not create or own a
  second tool store.
- `Registry.tool()` creates a `Tool`, normalizes its name with `str(name)`,
  accepts name, description, parameters, and callable/block, registers the
  new tool through `Context.register_tool`, and returns that same tool.
- The parameters default must be a fresh empty mapping on each call. Use a
  `None` sentinel (or equivalent) in Python rather than a mutable default
  object, then create `{}` per invocation. Preserve supplied mapping contents
  without introducing schema validation.
- `Registry.dispatch()` accepts a tool name and argument mapping, normalizes
  the requested name with `str(name)`, and looks up the tool through
  `Context.tools`.
- JSON/API-style string-keyed argument mappings must be converted into the
  keyword arguments expected by the Python callable. The callable result is
  returned directly, with no wrapping or coercion.
- A missing tool raises the custom `UnknownToolError` from a dedicated
  `boukensha/errors.py` module. The missing-name error must be exactly:
  `No tool registered as 'flee'` for the example dispatch.
- The example registers both `move` and `shout` through `Registry`, manually
  dispatches both, returns uppercase text from `shout`, returns exactly
  `You move north into a torch-lit corridor.` from `move`, then dispatches
  `flee`, catches `UnknownToolError`, and prints the error.
- This step still does not let an LLM decide when to dispatch tools; the
  example's calls remain explicit/manual.

Preserve all Step 1 behavior for `Config`, `Context`, `Message`, `Tool`, task
helpers, prompts, and Ruby-style string representations unless the Ruby Step 2
source explicitly requires a change. The only intended new runtime behavior is
registry creation, registration, lookup, dispatch, and unknown-tool errors.

## Files to create or copy

Create the new snapshot under:

```text
week1_baseline/python/02_the_registry/
```

The planned files are:

| File | Action and responsibility |
|---|---|
| `boukensha/__init__.py` | Copy Step 1 public exports and add `Registry` and `UnknownToolError`. |
| `boukensha/config.py` | Copy unchanged Step 1 `Config` behavior, including `BOUKENSHA_DIR`, `.env`, YAML, tasks, and prompt-directory handling. |
| `boukensha/context.py` | Copy unchanged Step 1 context behavior; its existing `tools` dictionary and `register_tool()` remain the storage boundary and replacement mechanism. |
| `boukensha/message.py` | Copy unchanged Step 1 `Message` dataclass and representation. |
| `boukensha/tool.py` | Copy unchanged Step 1 `Tool` dataclass, callable storage, parameter mapping, and representation. The registry will instantiate it. |
| `boukensha/errors.py` | New dedicated `UnknownToolError` exception class, equivalent to Ruby's `StandardError` subclass. |
| `boukensha/registry.py` | New `Registry` class receiving a `Context`, implementing `tool()` and `dispatch()` with the contract above. |
| `boukensha/tasks/__init__.py` | Copy unchanged Step 1 task exports. |
| `boukensha/tasks/base.py` | Copy unchanged Step 1 task configuration and prompt behavior. |
| `boukensha/tasks/player.py` | Copy unchanged Step 1 `Player` task. |
| `examples/example.py` | Port the Ruby Step 2 example: construct Config/Player/Context, register `move` and `shout` through Registry, manually dispatch them, and catch `UnknownToolError` for `flee`. |
| `prompts/system.md` | Copy the Step 1 default prompt unchanged. |
| `requirements.txt` | Copy the Step 1 dependency declaration and continue using `PyYAML` and `python-dotenv`. |
| `README.md` | New Python-specific explanation of the registry boundary, reused Step 1 behavior, environment, runner, commands, and verification contract. |
| `week1_baseline/bin/python/02_the_registry` | New portable Bash runner resolving its own directory, changing to the Step 2 implementation directory, and executing `examples/example.py` with the active environment's `python`. |

Do not copy Ruby `Gemfile`, `Gemfile.lock`, or other Ruby-only dependency
artifacts. Do not modify the Step 1 files; the new numbered directory is an
independent snapshot so it remains runnable and reviewable on its own.

## Registry design

`Registry.__init__(context)` should retain the supplied context reference.
It should not initialize `tools` and should not duplicate registration logic.

`Registry.tool(name, description, parameters=None, block/callable=...)` should:

1. normalize `name` with `str(name)`;
2. turn `None` into a new `{}` for that invocation, while retaining a supplied
   plain mapping as the tool's parameter data;
3. construct the existing `Tool` shape with the callable in its `block`
   field;
4. call `context.register_tool(tool)`; and
5. return the newly constructed `Tool`.

The implementation should use a Python callable parameter convention that is
clear at call sites and maps directly to Ruby's block. Do not add decorators,
dependency injection, validation, or framework objects.

`Registry.dispatch(name, args=None)` should normalize the lookup name with
`str(name)`, use `context.tools` for lookup, and raise `UnknownToolError` when
the key is absent. Treat omitted arguments as an empty mapping. Convert each
string key from the supplied argument mapping to the keyword name used by the
callable, then invoke the stored `Tool.block` and return its result unchanged.
The error text should interpolate the requested name so the example's
`dispatch("flee")` produces exactly `No tool registered as 'flee'`.

## Example and configuration path

Port the Ruby Step 2 example's setup and output sections while using the
Python Step 1 APIs. Set `BOUKENSHA_DIR` only when it is unset, with a path
derived from the example file's location that resolves to the repository-root
`.boukensha` directory. Do not rely on the caller's current directory.

Register:

- `move`, with the Ruby description and direction parameter schema, whose
  callable returns `f"You move {direction} into a torch-lit corridor."`;
- `shout`, with the Ruby description and message parameter schema, whose
  callable returns `message.upper()`.

Print the context and its tools after registration, then manually dispatch
`shout` with `{"message": "dragon spotted"}` and `move` with
`{"direction": "north"}`. Catch only the custom `UnknownToolError` around the
`flee` dispatch and print its exact message. Do not add API calls, an agent
loop, automatic dispatch decisions, or MUD behavior.

## Environment and README requirements

Document the shared virtual environment at:

```text
week1_baseline/python/.venv
```

Document installation using the new step's `requirements.txt`, for example:

```bash
python3 -m venv week1_baseline/python/.venv
source week1_baseline/python/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r week1_baseline/python/02_the_registry/requirements.txt
```

The runner assumes the environment is already active and must not create or
activate it. Do not create `pyproject.toml`. Do not introduce Pydantic, attrs,
Poetry, agent SDKs, or other frameworks. Do not create a formal test suite for
this baseline step.

The README must include the correct run command:

```bash
./week1_baseline/bin/python/02_the_registry
```

It must also document the `/tmp` invocation using the repository's absolute
path, direct example execution if useful, the Context/Registry ownership
boundary, fresh parameter defaults, string-keyed dispatch conversion,
replacement semantics, direct return values, exact error type/message, and
the fact that dispatch remains manually driven.

## Implementation sequence

1. Create the Step 2 directory structure and copy the Step 1 package modules,
   task modules, prompt, and `requirements.txt` without altering Step 1.
2. Add `errors.py` and export `UnknownToolError`; add `registry.py` and export
   `Registry`.
3. Implement `Registry.tool()` using the existing `Tool` and
   `Context.register_tool()` APIs, including name normalization, fresh
   parameter defaults, and returning the new tool.
4. Implement `Registry.dispatch()` using `Context.tools`, string-name lookup,
   keyword conversion for string-keyed mappings, direct callable results, and
   the exact unknown-tool exception behavior.
5. Port the Step 2 example and create the location-independent runner.
6. Write the README with the design contract, shared environment policy,
   commands, smoke checks, and final checklist.
7. Compare the Python structure and output against the Ruby source and inspect
   the diff to confirm that only the requested plan file was changed during
   planning; implementation changes belong to a later task.

## Smoke verification commands for the later implementation

From the repository root, with the shared environment active and dependencies
installed:

```bash
./week1_baseline/bin/python/02_the_registry
```

From `/tmp`, verify the runner does not depend on the current directory:

```bash
cd /tmp
/mnt/d/Tech/AI/Claude\ BC/claude-code-camp-2026-Q2/week1_baseline/bin/python/02_the_registry
```

Optionally verify direct execution:

```bash
cd /mnt/d/Tech/AI/Claude\ BC/claude-code-camp-2026-Q2/week1_baseline/python/02_the_registry
python examples/example.py
```

The output should show two registered tools, uppercase `DRAGON SPOTTED`, the
exact move sentence, and:

```text
UnknownToolError caught: No tool registered as 'flee'
```

Use one-off smoke commands (not committed tests and not a formal test suite)
to verify all of the following:

- registering a duplicate name replaces the previous `Context.tools` value;
- `Registry.tool()` with omitted parameters gives each tool a distinct fresh
  empty mapping;
- dispatch accepts string-keyed arguments and passes them as Python keyword
  arguments;
- dispatch returns an arbitrary callable result directly, preserving identity
  where applicable;
- missing lookup raises `UnknownToolError`, not `KeyError` or a generic
  exception;
- `str(exc)` is exactly `No tool registered as 'flee'` for the example case;
- the root runner succeeds;
- the `/tmp` runner succeeds; and
- no generated cache files (`__pycache__`, `.pyc`, coverage output, or similar)
  or secrets (`.env`, API keys, settings containing secrets) are staged.

## Final verification checklist

- [ ] Plan and implementation locations match the requested paths.
- [ ] Only the Step 2 snapshot files are created during implementation; Step 1,
      Ruby sources, and unrelated worktree changes are untouched.
- [ ] `Registry` receives an existing `Context` and does not own storage.
- [ ] Tool storage remains on `Context`; duplicate names replace prior tools.
- [ ] `Registry.tool()` creates, normalizes, registers, and returns a `Tool`.
- [ ] Parameters use a fresh empty mapping when omitted.
- [ ] `Registry.dispatch()` normalizes names and looks up only through
      `Context.tools`.
- [ ] String-keyed argument mappings become callable keyword arguments.
- [ ] Dispatch returns the callable result directly.
- [ ] `UnknownToolError` lives in `boukensha/errors.py` and has the exact
      `No tool registered as 'flee'` message.
- [ ] The example registers and manually dispatches `move` and `shout`, catches
      `flee`, and does not add LLM-driven dispatch.
- [ ] Existing Step 1 Config, Context, Message, Tool, tasks, prompts, and
      representations remain behaviorally unchanged.
- [ ] The shared `week1_baseline/python/.venv` and `requirements.txt` policy is
      documented; no `pyproject.toml` or framework was introduced.
- [ ] No formal test suite was created.
- [ ] The default example configuration path resolves to the repository-root
      `.boukensha` directory.
- [ ] The root and `/tmp` runner checks pass.
- [ ] No generated cache files or secrets are staged.
- [ ] Nothing is committed or pushed.
