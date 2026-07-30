# Python Port Plan: `01_struct_skeleton`

## Goal

Port the Ruby Week 1 Step 1 struct skeleton to Python while preserving the
Ruby behavior, public shape, output formatting, and snapshot-style directory
layout. This is a small learning baseline, not a redesign.

Ruby remains the source of truth:

```text
week1_baseline/ruby/01_struct_skeleton
week1_baseline/bin/ruby/01_struct_skeleton
```

Reuse the already-ported Step 0 configuration and player-task behavior from:

```text
week1_baseline/python/00_config
week1_baseline/bin/python/00_config
```

No code should be implemented as part of this plan, and no existing source
file should be modified.

## Responsibilities and behavior

### `Tool`

Implement `Tool` as a Python dataclass representing one callable tool. Its
fields should correspond directly to Ruby's `Struct.new(:name, :description,
:parameters, :block)`:

- `name`: registration and lookup key;
- `description`: text shown to the agent;
- `parameters`: the tool input schema/data;
- `block` equivalent: the Python callable to invoke.

Store the callable directly on the instance (for example, in a field named
`block` or `callable`), rather than wrapping it in a framework object. The
callable is data held by the tool at this step; invocation mechanics are out
of scope.

Represent parameters as a plain dictionary, preserving the Ruby example's
shape, including nested dictionaries such as `{"direction": {"type":
"string", "description": "The direction to move"}}`. Display parameter
names from the dictionary keys in insertion order, using an intentional list
representation such as `params=['direction']`. Do not use the incidental repr
of `dict.keys()`.

`Tool.__str__`/`__repr__` should produce the Ruby-style form:

```text
#<Tool name=move description=... params=['direction']>
```

Preserve the Ruby truncation convention and trailing `...`: the source uses
`description.to_s[0..40]`, an inclusive Ruby range. The Python equivalent
must be `str(description)[:41]`, retaining up to 41 characters, followed by
`...` unconditionally, including when the original description is shorter.

### `Message`

Implement `Message` as a Python dataclass with fields `role`, `content`, and
optional `tool_use_id`, defaulting to `None`. It represents one ordered
conversation item for `user`, `assistant`, or `tool_result`.

Its string form must include the role, optional ID tag, and truncated content:

```text
#<Message role=user content=Explore north and tell me what you find....>
#<Message role=tool_result [toolu_01X] content=...>
```

Use the Ruby behavior of converting content to text, taking
`str(content)[:61]` (the Python equivalent of Ruby's inclusive
`content.to_s[0..60]`), and appending `...` unconditionally, including when
the original content is shorter. Do not omit the ID when it is present and do
not add an ID marker when it is absent.

### `Context`

Implement `Context` as a regular Python class, not a dataclass. Ruby's
`Context` owns mutable collections and behavior (`register_tool`,
`add_message`, `tool_count`, and `turn_count`), so a regular class best
matches its responsibility and avoids implying value-object equality or
generated initialization semantics.

The constructor should accept `task` and optional `system`, initialize fresh
empty `messages` and `tools`, and expose those values. It should:

- register tools in a dictionary keyed by `tool.name`;
- replace the existing value when a duplicate name is registered, matching
  Ruby hash assignment (no error and no duplicate entry);
- append messages to the list in call order;
- accept `tool_use_id` optionally in `add_message`, forwarding it to
  `Message`; and
- report `tool_count` as the number of registered names.

Preserve the Ruby interpretation of `turn_count`: it is exactly
`messages.size`, not an inferred number of conversational turns and not a
counter of user/assistant pairs. The context string should include the task's
`task_name`, message count as `turns`, and registered tool count:

```text
#<Context task=player turns=2 tools=1>
```

Use a safe task-name lookup equivalent to Ruby's `task&.task_name` for a
missing task, while keeping the normal `Player.task_name()` result as
`player`.

## Proposed Python structure

Create a new snapshot directory without changing Step 0:

```text
week1_baseline/python/01_struct_skeleton/
├── boukensha/
│   ├── __init__.py
│   ├── config.py                 # reused Step 0 behavior
│   ├── context.py
│   ├── message.py
│   ├── tool.py
│   └── tasks/
│       ├── __init__.py
│       ├── base.py                # reused Step 0 behavior
│       └── player.py              # reused Step 0 behavior
├── examples/example.py
├── prompts/system.md
├── README.md
└── requirements.txt
```

Copy the Step 0 Python configuration/task implementation into this snapshot
so each numbered iteration remains independently runnable, then add only the
Step 1 `Tool`, `Message`, and `Context` modules and exports. Keep
`requirements.txt` as the dependency declaration and continue using the
shared environment at `week1_baseline/python/.venv`. Do not create
`pyproject.toml`, Pydantic models, `attrs` classes, an agent SDK, or another
framework. Do not create a formal test suite for this baseline step.

Create the portable runner:

```text
week1_baseline/bin/python/01_struct_skeleton
```

It should resolve its own location, change into the Step 1 implementation
directory, and execute `examples/example.py` with the active environment's
`python`, just as the Step 0 runner does. It must work regardless of the
caller's current directory and must not create or activate `.venv`.

## Example port

Port `week1_baseline/ruby/01_struct_skeleton/examples/example.rb` faithfully:

1. import the Step 1 package;
2. set `BOUKENSHA_DIR` to the repository `.boukensha` path only when unset;
3. build `Config`, retrieve `player` settings, and obtain the existing Player
   system prompt using the Step 0 APIs;
4. create a `Context` with `Player` and that prompt;
5. register the `move` tool with the same name, description, parameter schema,
   and callable result;
6. append the two messages in the same order; and
7. print the Config, Context, registered tool, and messages in the same
   sections and indentation as the Ruby example.

Do not add API calls, tool execution, agent-loop behavior, or MUD behavior.

## README requirements

The new README should explain the struct-skeleton purpose and the
responsibilities/fields of `Tool`, `Message`, and `Context`, including why
`Tool` and `Message` are dataclasses while `Context` is a regular class. It
must document callable storage, dictionary parameter schemas, name-based
registration and replacement on duplicates, ordered message appends,
optional tool-use IDs, and `turn_count == len(messages)`.

Document the shared `.venv`, `requirements.txt`, configuration reuse, the
portable runner, direct example execution, and the fact that this is a
baseline without a formal test suite. Include representative Ruby-style
string outputs and the exact smoke commands below.

## Implementation sequence

1. Create the Step 1 directory/package skeleton and copy the Step 0
   configuration, task, prompt, and dependency files without altering Step 0.
2. Add public package exports for the copied APIs plus `Tool`, `Message`, and
   `Context`.
3. Implement the `Tool` dataclass, deterministic parameter-name list
   formatting, and Ruby-compatible string formatting using
   `str(description)[:41]` plus unconditional `...`.
4. Implement the `Message` dataclass, optional ID handling, and formatting
   using `str(content)[:61]` plus unconditional `...`.
5. Implement mutable `Context` registration, replacement, ordered append,
   counts, and formatting.
6. Port the example and create the portable runner.
7. Write the README and compare all output/paths against the Ruby source.

## Smoke verification

From the repository root, with `week1_baseline/python/.venv` activated and
dependencies installed:

```bash
./week1_baseline/bin/python/01_struct_skeleton
```

Also verify the launcher is independent of the current directory:

```bash
cd /tmp
/mnt/d/Tech/AI/Claude\ BC/claude-code-camp-2026-Q2/week1_baseline/bin/python/01_struct_skeleton
```

Optionally compare direct execution from the implementation directory:

```bash
cd /mnt/d/Tech/AI/Claude\ BC/claude-code-camp-2026-Q2/week1_baseline/python/01_struct_skeleton
python examples/example.py
```

Manually verify that output contains the Step 1 heading, the reused Config
line, `Context task=player turns=2 tools=1`, the `move` tool with its
description and deterministic `params=['direction']` display, and the two
messages in order. Verify long descriptions use `str(description)[:41]` and
long content uses `str(content)[:61]`, with `...` appended even for short
values.
Also exercise the small behavior cases interactively or with a temporary
one-off command: duplicate registration replaces by name, message IDs appear
only when supplied, long strings use the required truncation, and
`turn_count` equals the message-list length. Do not commit that command or
turn it into a test suite.

## Final verification checklist

- [ ] Only new Step 1 Python files, runner, README, and plan-specified assets
      were created; existing source files were not modified.
- [ ] Ruby remains unchanged and is still the behavioral reference.
- [ ] `Tool` and `Message` are dataclasses; `Context` is a regular class.
- [ ] Tool callables and plain dictionary parameter schemas are preserved.
- [ ] Tool parameter names use an intentional insertion-ordered list format
      such as `params=['direction']`, never `dict_keys(...)` repr output.
- [ ] Registration is name-keyed and duplicate names replace prior tools.
- [ ] Messages append in order and preserve optional `tool_use_id`.
- [ ] String formats match the Ruby output contract: descriptions use
      `str(description)[:41]` and content uses `str(content)[:61]`, with
      `...` appended unconditionally in both cases.
- [ ] `turn_count` is exactly the message count.
- [ ] Step 0 Config and Player behavior is reused faithfully.
- [ ] The runner works from both the repository root and `/tmp`.
- [ ] The shared `week1_baseline/python/.venv` and `requirements.txt` policy is
      documented and no `pyproject.toml` or framework was introduced.
- [ ] No formal test suite, external API call, MUD interaction, or commit was
      added.
