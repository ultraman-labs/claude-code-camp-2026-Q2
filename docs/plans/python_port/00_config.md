# Python Port Plan: `00_config`

## Goal

Port the Ruby configuration implementation in:

```text
week1_baseline/ruby/00_config
```

to Python while preserving the same externally visible behavior, configuration schema, directory resolution, prompt lookup behavior, launcher behavior, and example output.

This is a port, not a redesign.

The Ruby implementation is the source of truth.

The Python implementation should mirror the Ruby structure and behavior as closely as practical so that both versions can be reviewed side by side and future Week 1 iterations can follow the same snapshot-per-step progression.

Do not introduce additional frameworks, abstractions, validation systems, agent SDKs, or design patterns unless they are required to reproduce the Ruby behavior.

---

## Primary Objectives

The Python port must:

1. Preserve the behavior of the Ruby `00_config` implementation.
2. Use plain Python dictionaries for configuration data.
3. Preserve the existing `settings.yaml` schema.
4. Load secrets from the Boukensha `.env` file.
5. Support the `BOUKENSHA_DIR` environment-variable override.
6. Preserve default and user-overridden prompt behavior.
7. Provide a Python launcher that can be run from any working directory.
8. Provide a Python example that produces output equivalent to the Ruby example.
9. Document Python environment setup and execution in a Python-specific README.
10. Keep the Ruby and Python implementations separate and easy to compare.

---

## Source of Truth

Use the following Ruby files as the authoritative behavioral reference.

| Ruby source | Python port target | Responsibility |
|---|---|---|
| `week1_baseline/ruby/00_config/lib/boukensha/config.rb` | `week1_baseline/python/00_config/boukensha/config.py` | Configuration-directory resolution, `.env` loading, YAML loading, task lookup, MUD accessors, and nested lookup |
| `week1_baseline/ruby/00_config/lib/boukensha/tasks/base.rb` | `week1_baseline/python/00_config/boukensha/tasks/base.py` | Shared stateless task behavior, provider/model lookup, prompt override lookup, and prompt resolution |
| `week1_baseline/ruby/00_config/lib/boukensha/tasks/player.rb` | `week1_baseline/python/00_config/boukensha/tasks/player.py` | Concrete player task with task name `player` |
| `week1_baseline/ruby/00_config/lib/boukensha.rb` | `week1_baseline/python/00_config/boukensha/__init__.py` | Public package imports |
| `week1_baseline/ruby/00_config/prompts/system.md` | `week1_baseline/python/00_config/prompts/system.md` | Packaged default system prompt |
| `week1_baseline/ruby/00_config/examples/example.rb` | `week1_baseline/python/00_config/examples/example.py` | Runnable configuration example and smoke test |
| `week1_baseline/bin/ruby/00_config` | `week1_baseline/bin/python/00_config` | Python launcher |
| `week1_baseline/ruby/00_config/README.md` | `week1_baseline/python/00_config/README.md` | Python setup, structure, schema, and execution instructions |
| `week1_baseline/ruby/00_config/Gemfile` | `week1_baseline/python/00_config/requirements.txt` | Python runtime dependencies |

Do not port these Ruby-specific files:

```text
Gemfile.lock
.bundle/config
vendor/
```

The Python implementation should use Python-specific environment and dependency conventions instead.

---

## Target Directory Structure

Create the Python implementation under:

```text
week1_baseline/python/00_config/
```

Use this proposed structure:

```text
week1_baseline/
├── bin/
│   ├── ruby/
│   │   └── 00_config
│   └── python/
│       └── 00_config
├── ruby/
│   └── 00_config/
└── python/
    └── 00_config/
        ├── boukensha/
        │   ├── __init__.py
        │   ├── config.py
        │   └── tasks/
        │       ├── __init__.py
        │       ├── base.py
        │       └── player.py
        ├── examples/
        │   └── example.py
        ├── prompts/
        │   └── system.md
        ├── README.md
        └── requirements.txt
```

Mirror the Ruby directory structure as closely as practical.

Small Python-specific differences are acceptable when required by Python package conventions, but the structure should remain easy to compare with the Ruby implementation.

Do not replace or remove the Ruby implementation as part of this port.

Only modify an existing Ruby launcher when a path correction is explicitly required by the current repository layout.

---

## Dependency and Environment Policy

Keep the Python tooling simple.

Use:

```text
PyYAML
python-dotenv
```

Declare these dependencies in:

```text
week1_baseline/python/00_config/requirements.txt
```

Do not introduce:

```text
Pydantic
Poetry
Pipenv
Hatch
a Python agent SDK
a configuration framework
```

Do not create a `pyproject.toml` for this step unless the repository already requires one for the Python baseline.

Use one reusable Python virtual environment for the Week 1 Python iterations rather than creating a separate environment inside every numbered step.

Place the shared virtual environment at:

```text
week1_baseline/python/.venv
```

The README should instruct the user to create and activate it.

From the repository root:

```bash
python3 -m venv week1_baseline/python/.venv
source week1_baseline/python/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r week1_baseline/python/00_config/requirements.txt
```

The launcher should assume that the environment has already been created and that the required dependencies have already been installed.

The launcher must not create, modify, or automatically activate the virtual environment.

Ensure that `.venv/` remains ignored by Git.

---

## Configuration Behavior

Implement a Python `Config` class that preserves the behavior of:

```text
week1_baseline/ruby/00_config/lib/boukensha/config.rb
```

### Configuration Directory Resolution

Resolve the configuration directory in this order:

1. Use `BOUKENSHA_DIR` when it is set.
2. Otherwise use:

```text
~/.boukensha
```

Expand `~` and convert the resulting path into an absolute path.

Do not assume the caller is running from the repository root.

Expose the resolved configuration directory through a clear Python attribute or property.

---

### Environment File Loading

Load:

```text
<BOUKENSHA_DIR>/.env
```

before the caller attempts to access API-key environment variables.

A missing `.env` file is valid and must not raise an error.

The `.env` file must remain external configuration and must not be committed.

Use `python-dotenv` to load the file.

Do not overwrite an environment variable that is already set in the caller's process environment unless the Ruby implementation explicitly does so.

---

### YAML Settings Loading

Load:

```text
<BOUKENSHA_DIR>/settings.yaml
```

using safe YAML loading.

Use plain Python dictionaries.

Do not introduce typed configuration models or schema-validation frameworks in this step.

The following cases must safely produce an empty settings dictionary:

- `settings.yaml` does not exist.
- `settings.yaml` exists but is empty.
- The YAML document resolves to `null`.

Preserve string keys such as:

```yaml
tasks:
  player:
    provider: OpenAI
    model: gpt-5.6-luna
```

Do not redesign or rename the existing configuration schema.

If the YAML root value is not a dictionary, fail with a clear and useful error rather than allowing unrelated failures later in execution.

---

### Task Lookup

Preserve the Ruby task lookup behavior.

The Python API should support retrieving:

- the complete task mapping;
- a named task such as `player`;
- `None` when the requested task does not exist.

The exact Python method signature may follow Python conventions, but its behavior should remain easy to compare with:

```ruby
config.tasks
config.tasks(:player)
```

Use plain dictionaries rather than custom configuration objects.

---

### Nested Lookup

Provide a small nested lookup helper equivalent to Ruby's `dig`.

For example, the implementation should be able to retrieve a value corresponding to:

```text
tasks → player → provider
```

The helper should:

- accept a sequence of keys;
- traverse dictionaries;
- return `None` when a path does not exist;
- not raise an exception merely because an intermediate key is absent.

Do not create a general-purpose configuration framework.

---

### MUD Configuration Accessors

Preserve the existing MUD configuration behavior.

Expose values equivalent to:

```text
mud.host
mud.port
mud.username
mud.password
```

Use these defaults only when the corresponding setting is absent:

```text
host: localhost
port: 4000
```

Do not replace an explicitly configured false-like value merely because it evaluates as false in Python.

For example, avoid implementing defaults with logic that incorrectly replaces:

```yaml
port: 0
```

Use absence-aware lookup rather than a simple `value or default` expression.

`mud_username` and `mud_password` may return `None` when they are not configured.

---

### User Prompt Directory

Expose the user prompt directory as:

```text
<BOUKENSHA_DIR>/prompts
```

Prompt lookup code should use this resolved path rather than duplicating path construction in multiple places.

---

## Task Behavior

Port the behavior from:

```text
week1_baseline/ruby/00_config/lib/boukensha/tasks/base.rb
week1_baseline/ruby/00_config/lib/boukensha/tasks/player.rb
```

The task API should remain stateless.

Use class-level behavior where it helps preserve the Ruby calling style and keeps future Ruby-to-Python comparisons straightforward.

`@classmethod` is acceptable for this implementation.

Do not instantiate task objects unless the Ruby implementation requires state.

---

### Base Task Requirements

The base task must require each concrete subclass to define a task name.

Calling task functionality without a concrete task name should fail clearly.

The concrete player task must report:

```text
player
```

as its task name.

---

### Provider and Model Lookup

For a task's settings, provide lookup behavior equivalent to the Ruby implementation for:

```text
provider
model
```

When either required value is missing, fail with a clear exception that identifies:

- the missing field;
- the affected task name.

Do not silently substitute a provider or model.

Do not add provider-specific validation in this step.

Preserve the configured provider and model strings without normalizing, renaming, or changing their capitalization.

---

### Prompt Override Lookup

Preserve the existing `prompt_override` behavior.

For a prompt named `system`, the override is enabled only when the corresponding loaded YAML value is Python Boolean `True`.

For example:

```yaml
prompt_override:
  system: true
```

A missing override setting means the override is disabled.

Do not manually coerce arbitrary strings or numbers into Boolean values.

Values such as these should not be manually interpreted as Boolean `True` by application code:

```yaml
prompt_override:
  system: "true"
```

```yaml
prompt_override:
  system: 1
```

Use the value produced by the YAML parser and require identity with Boolean `True`.

---

### Prompt Lookup Order

For task `player` and prompt `system`, resolve the prompt in this order:

1. When the override is enabled, try:

```text
<BOUKENSHA_DIR>/prompts/player/system.md
```

2. If the override is disabled, absent, or the user prompt file does not exist, fall back to the packaged prompt:

```text
week1_baseline/python/00_config/prompts/system.md
```

3. If neither file exists, return `None`.

Read prompt files as text and strip surrounding whitespace to match the Ruby behavior.

Do not raise an error merely because an optional prompt file is absent.

Copy the existing Ruby default `prompts/system.md` content unchanged unless a Python-specific change is genuinely required.

---

## Python Package Exports

Use:

```text
week1_baseline/python/00_config/boukensha/__init__.py
```

to expose the primary public classes required by the example.

The example should not need to import deeply nested implementation modules unless that is necessary.

Keep exports explicit and minimal.

Do not create a global executable or publishable Python package in this step.

---

## Example Behavior

Port:

```text
week1_baseline/ruby/00_config/examples/example.rb
```

to:

```text
week1_baseline/python/00_config/examples/example.py
```

The Python example must:

1. Preserve an existing `BOUKENSHA_DIR` value when it is already set.
2. Otherwise set `BOUKENSHA_DIR` to:

```text
week1_baseline/.boukensha
```

3. Load the Python configuration implementation.
4. Load the `player` task settings.
5. Print output equivalent in meaning and order to the Ruby example.
6. Print whether the OpenAI API key is set.
7. Never print the API key itself.
8. Demonstrate that the default or overridden system prompt was loaded.
9. Be runnable through the Python launcher.

The Python output does not need to reproduce Ruby object formatting byte-for-byte.

Readable Python-native output is acceptable, but the displayed fields and values should match the Ruby example semantically.

Preserve labels such as:

```text
Tasks:
Provider:
Model:
Prompt override?
System prompt:
MUD user:
API key set?
```

where practical so the Ruby and Python examples remain easy to compare.

Use:

```text
OPENAI_API_KEY
```

for the API-key Boolean check in this implementation.

The example must not contain an API key or another secret.

---

## Launcher Behavior

Create:

```text
week1_baseline/bin/python/00_config
```

as an executable Bash launcher.

It must:

1. Work when called from the repository root.
2. Work when called from another current working directory.
3. Resolve its own filesystem location.
4. Resolve the correct Python `00_config` directory.
5. Run the Python example.
6. Propagate the Python process exit code.
7. Avoid printing secrets.
8. Avoid creating or activating a virtual environment automatically.

A possible implementation is:

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASELINE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
STEP_DIR="$BASELINE_DIR/python/00_config"

cd "$STEP_DIR"
python examples/example.py
```

Codex must inspect and verify the repository's actual directory structure before finalizing the launcher path.

Do not blindly copy this example if the actual paths differ.

Use `python` so the launcher runs the interpreter supplied by the user's currently activated virtual environment.

Ensure the launcher is executable.

---

## README Requirements

Create:

```text
week1_baseline/python/00_config/README.md
```

Use the Ruby README as the behavioral and educational reference, but rewrite commands and structure for Python.

The Python README must explain:

- the purpose of Step 0;
- the Python directory layout;
- how `BOUKENSHA_DIR` is resolved;
- where `.env` belongs;
- where `settings.yaml` belongs;
- where prompt overrides belong;
- the expected YAML schema;
- how to create the shared Python virtual environment;
- how to activate the environment;
- how to install dependencies;
- how to run the example directly;
- how to run the Python launcher;
- what output to expect;
- that secrets and local configuration must not be committed.

The README should include commands that can be copied from the repository root.

Do not claim a formal test suite exists unless one is actually implemented.

Do not include an actual API key in any example.

Use a placeholder such as:

```text
OPENAI_API_KEY=your-api-key-here
```

---

## Implementation Sequence

Execute the port in the following order.

### 1. Inspect the Ruby Source

Read every source file listed in the source-of-truth table before creating Python files.

Confirm:

- method behavior;
- configuration keys;
- defaults;
- path calculations;
- prompt lookup order;
- example output;
- launcher path behavior.

Do not infer behavior from file names alone.

Do not begin implementation until the referenced files and actual repository paths have been inspected.

---

### 2. Create the Python Structure

Create:

```text
week1_baseline/python/00_config
```

and the package, task, example, and prompt directories.

Create the required `__init__.py` files.

Copy the packaged `system.md` prompt unchanged.

---

### 3. Implement Configuration Loading

Implement:

```text
boukensha/config.py
```

with:

- configuration-directory resolution;
- `.env` loading;
- safe YAML loading;
- empty or missing YAML handling;
- task lookup;
- nested lookup;
- prompt-directory resolution;
- MUD accessors and defaults.

Keep the implementation small and directly traceable to `config.rb`.

---

### 4. Implement Tasks

Implement:

```text
boukensha/tasks/base.py
boukensha/tasks/player.py
```

with:

- required task-name behavior;
- provider lookup;
- model lookup;
- Boolean prompt-override lookup;
- user prompt lookup;
- packaged prompt fallback;
- missing-prompt behavior.

Keep the implementation stateless and close to the Ruby design.

---

### 5. Add Dependencies

Create:

```text
requirements.txt
```

with only the runtime packages required for this step.

Expected dependencies:

```text
PyYAML
python-dotenv
```

Do not add unrelated development dependencies.

Do not add a testing framework.

---

### 6. Port the Example

Implement:

```text
examples/example.py
```

and preserve the meaning and order of the Ruby example output.

Ensure the repository-local `.boukensha` directory is selected only when `BOUKENSHA_DIR` is not already set.

Do not print secrets.

---

### 7. Create the Launcher

Create and make executable:

```text
week1_baseline/bin/python/00_config
```

Verify that its paths match the actual repository layout.

Do not automatically create or activate the virtual environment.

---

### 8. Write the README

Document the exact setup and execution process used by the completed Python implementation.

Do not document commands that have not been verified.

---

### 9. Review Before Running

Before execution, compare every generated Python file with its corresponding Ruby source.

Confirm that the implementation has not introduced:

- Pydantic;
- an agent SDK;
- unnecessary abstractions;
- a redesigned settings schema;
- hard-coded secrets;
- a separate virtual environment inside the numbered step;
- automatic environment creation in the launcher;
- formal testing infrastructure not requested by this plan.

---

### 10. Run Smoke Verification

Use the example as the primary smoke test for this step.

Run it:

1. directly from the Python `00_config` directory;
2. through the launcher from the repository root;
3. through the launcher from another current working directory.

Do not add a formal test suite as part of this step.

Small temporary scripts or shell commands may be used to verify edge cases, but do not introduce `pytest`, committed `unittest` files, or TDD infrastructure unless separately requested.

Clean up temporary verification files after use.

---

## Verification Checklist

The implementation is complete only when all relevant checks pass.

### Path and Environment Checks

- `BOUKENSHA_DIR` overrides the default directory.
- The default directory resolves to `~/.boukensha`.
- `~` is expanded correctly.
- Relative override paths are converted to absolute paths.
- The implementation does not depend on the caller's current working directory.
- A missing `.env` file does not raise an error.
- `.env` is loaded before the example checks `OPENAI_API_KEY`.
- Existing process environment variables are not unexpectedly overwritten.

### YAML Checks

- A missing `settings.yaml` produces an empty dictionary.
- An empty `settings.yaml` produces an empty dictionary.
- A YAML `null` document produces an empty dictionary.
- Task keys remain ordinary Python strings.
- The existing settings schema works without modification.
- A non-dictionary YAML root produces a clear error.
- No Pydantic or typed schema layer is introduced.

### Task Checks

- Retrieving all tasks works.
- Retrieving the `player` task works.
- Retrieving an unknown task returns `None`.
- Missing provider information raises a clear error.
- Missing model information raises a clear error.
- Error messages identify the affected task.

### Prompt Checks

- A missing override setting uses the packaged prompt.
- A disabled override uses the packaged prompt.
- An enabled override with an existing user file uses the user prompt.
- An enabled override with a missing user file falls back to the packaged prompt.
- Missing packaged and user prompts return `None`.
- Prompt content is stripped of surrounding whitespace.
- Only Boolean `True` enables an override.

### MUD Checks

- A missing host defaults to `localhost`.
- A missing port defaults to `4000`.
- Explicitly configured values are preserved.
- An explicitly configured false-like value is not replaced merely because it is false-like.
- A missing username or password may return `None`.

### Example Checks

- The example loads the expected task.
- The example displays the configured provider.
- The example displays the configured model.
- The example reports whether prompt override is enabled.
- The example displays the resolved system prompt.
- The example displays the MUD username.
- The example prints `API key set?` as a Boolean result.
- The API key itself is never printed.

### Launcher Checks

- The launcher works from the repository root.
- The launcher works from another working directory.
- The launcher resolves the correct Python step directory.
- The launcher returns a nonzero status when Python execution fails.
- The launcher does not create or activate a virtual environment.
- The launcher file is executable.

### Repository Checks

- `.env` is not staged.
- `.boukensha/` is not staged.
- `.venv/` is not staged.
- `__pycache__/` directories are not staged.
- `.pyc` files are not staged.
- The Ruby implementation remains intact.
- The Python implementation is isolated under `week1_baseline/python/00_config`.
- No temporary verification files remain.

---

## Out of Scope

Do not implement later Week 1 functionality in this port.

The following are out of scope:

- struct skeleton;
- tool registry;
- prompt builder beyond Step 0 prompt-file lookup;
- API client;
- agent loop;
- logging;
- DSL;
- REPL;
- global executable;
- MCP;
- TUI;
- context compaction;
- long-term memory;
- automated MUD gameplay;
- provider-specific API calls;
- formal unit-test or TDD infrastructure;
- Pydantic configuration models;
- packaging the Python project for publication.

Do not implement future task settings such as:

```text
max_iterations
max_turn_tokens
max_output_tokens
compaction_threshold
```

unless they already participate in the Ruby `00_config` runtime behavior.

---

## Decisions Resolved for This Implementation

Use the following decisions unless the existing repository structure makes one impossible.

### 1. Python Location

```text
week1_baseline/python/00_config
```

### 2. Configuration Representation

Use plain Python dictionaries loaded with `yaml.safe_load`.

### 3. Dependencies

```text
PyYAML
python-dotenv
```

### 4. Dependency File

```text
requirements.txt
```

### 5. Virtual Environment

Use one shared environment at:

```text
week1_baseline/python/.venv
```

### 6. Task API

Preserve stateless class-level behavior using `@classmethod` where appropriate.

### 7. Testing Approach

Use the example and targeted smoke verification.

Do not add a formal test suite in this step.

### 8. Output Compatibility

Preserve equivalent fields, values, and ordering.

Byte-for-byte Ruby formatting is not required.

### 9. Prompt Structure

Preserve the existing task-specific user prompt path and packaged fallback behavior.

### 10. Design Approach

Mirror the Ruby implementation.

Do not redesign, modernize, or expand it.

---

## Final Implementation Instructions

Before making changes:

1. Inspect every referenced Ruby source file.
2. Confirm the actual repository paths.
3. Confirm that the target Python directories do not conflict with existing work.
4. Report any important conflict or ambiguity before proceeding.

Then implement this plan exactly within the defined scope.

After implementation:

1. Summarize every file created or modified.
2. Explain any necessary difference from the Ruby implementation.
3. List the commands used for smoke verification.
4. Report the result of each verification command.
5. Identify any unresolved issue instead of silently working around it.
6. Show the final relevant `git status --short` output.
7. Do not commit or push the changes unless explicitly instructed to do so.