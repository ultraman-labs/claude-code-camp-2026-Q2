# Python Port Plan — Step 8: The REPL Loop

## Status

**Architecture Discovery:** Complete
**Port Plan:** Proposed
**Implementation:** Not started
**Approval:** Pending

---

## 1. Purpose

Port the Ruby `08_the_repl_loop` iteration to Python while preserving the architecture, externally visible behavior, and pedagogical progression of the instructor implementation.

This iteration changes Boukensha from a framework that supports only a one-shot task through `run(...)` into one that also supports an interactive terminal REPL.

The REPL must:

* remain alive across multiple user prompts,
* preserve conversation history across turns,
* reuse the same `Context`, `Registry`, tools, `PromptBuilder`, `Client`, and `Logger`,
* create and run an `Agent` for each conversational turn,
* support built-in REPL commands,
* allow conversation history to be cleared without removing tools or the system prompt,
* exit cleanly through `/exit`, `/quit`, EOF, or interrupt handling.

The Python Step 8 implementation must begin as a copy of Python Step 7 and introduce only the behavior represented by the Ruby Step 7 → Step 8 delta.

---

## 2. Source of Truth

The source of truth for this port is the instructor's Ruby implementation:

```text
week1_baseline/ruby/07_the_run_dsl
week1_baseline/ruby/08_the_repl_loop
```

The port must be derived from their semantic delta.

Do not redesign Step 8 based on preferred Python architecture.

Do not silently correct instructor implementation choices that appear inefficient or awkward.

Where Ruby and Python syntax differ, preserve behavior and architectural responsibility rather than syntax.

---

## 3. Architecture Discovery Summary

The Ruby Step 7 → Step 8 comparison identified the following changed or new files:

```text
README.md
examples/example.rb
lib/boukensha.rb
lib/boukensha/agent.rb
lib/boukensha/client.rb
lib/boukensha/config.rb
lib/boukensha/context.rb

NEW:
lib/boukensha/repl.rb
lib/boukensha/version.rb
```

The Ruby runner also advances from:

```text
week1_baseline/ruby/bin/07_the_run_dsl
```

to:

```text
week1_baseline/ruby/bin/08_the_repl_loop
```

The runner architecture itself does not change. It continues to change into the selected iteration directory and execute the example.

---

## 4. High-Level Behavioral Delta

### Step 7

Step 7 provides a one-shot composition root:

```text
run(task)
   ↓
create Context
   ↓
register tools
   ↓
create backend/client/logger/agent
   ↓
Agent.run()
   ↓
return final response
   ↓
exit
```

### Step 8

Step 8 adds a persistent interactive mode:

```text
repl()
   ↓
create shared infrastructure
   ↓
start REPL
   ↓
┌──────────────────────────────┐
│ read input                   │
│                              │
│ built-in command?            │
│   ├─ yes → handle locally    │
│   └─ no                      │
│        ↓                     │
│ add user message             │
│        ↓                     │
│ create Agent                 │
│        ↓                     │
│ Agent.run()                  │
│        ↓                     │
│ assistant reply stored       │
│        ↓                     │
│ print reply                  │
│        ↓                     │
│ next terminal prompt         │
└──────────────────────────────┘
```

The existing one-shot `run(...)` API remains available.

Step 8 adds a second public execution mode rather than replacing Step 7 behavior.

---

## 5. Core REPL Architecture

Create a Python REPL primitive corresponding to Ruby:

```text
lib/boukensha/repl.rb
```

Proposed Python target:

```text
week1_baseline/python/08_the_repl_loop/boukensha/repl.py
```

The REPL object owns the interactive session loop.

Its responsibilities are:

* print the startup banner,
* print the terminal prompt,
* read stdin,
* detect EOF,
* normalize input,
* ignore empty input,
* dispatch built-in REPL commands,
* execute normal user input as an agent turn,
* print each final response,
* continue until explicitly terminated.

The REPL must not duplicate Registry, Context, Client, Agent, or Logger responsibilities.

---

## 6. Shared Session State

The following objects must be constructed before the REPL starts and reused throughout the interactive session:

```text
Context
Registry
registered tools
Backend
PromptBuilder
Client
Logger
```

This shared state is what allows multiple prompts to participate in one conversation.

The REPL must use one persistent `Context`.

Conversation messages accumulate in that Context across turns unless `/clear` is invoked.

---

## 7. Per-Turn Agent Construction

The Ruby Step 8 implementation creates a new `Agent` inside each REPL turn.

The Python port must preserve that behavior.

Conceptually:

```text
REPL session
   │
   ├── shared Context
   ├── shared Registry
   ├── shared Builder
   ├── shared Client
   ├── shared Logger
   │
   ├── turn 1
   │     └── Agent(...)
   │           └── run()
   │
   ├── turn 2
   │     └── Agent(...)
   │           └── run()
   │
   └── turn N
         └── Agent(...)
               └── run()
```

### Fidelity constraint

Do **not** refactor the Python version to create one reusable `Agent` for the entire REPL session.

The instructor explicitly observed that per-turn Agent creation may be inefficient, but this behavior belongs to the Ruby Step 8 layer and should remain faithful in the Python port.

Any potential redesign belongs to a later cleanup/refactoring step.

---

## 8. Conversation History Persistence

Step 8 requires a supporting change to `Agent`.

Before Step 8, the final assistant reply was returned but was not added back to Context.

That behavior is sufficient for one-shot execution because the process ends immediately.

It is insufficient for a REPL because future prompts must see previous assistant responses.

Python Step 8 must therefore ensure that the final assistant response is added to the shared Context before it is returned.

Conceptually:

```python
context.add_message("assistant", text)
return text
```

This must occur for the same result paths represented in the Ruby delta, including normal completion and supported fallback paths.

The goal is that after two conversational turns, Context resembles:

```text
user       prompt 1
assistant  response 1
user       prompt 2
assistant  response 2
```

rather than:

```text
user       prompt 1
user       prompt 2
```

---

## 9. Context Clearing

Add the Python equivalent of Ruby:

```ruby
Context#clear_messages!
```

Proposed Python API:

```python
Context.clear_messages()
```

or another naming form consistent with the existing Python conventions.

Behavior:

```text
Before /clear

system prompt       preserved
registered tools    preserved
conversation        present
```

After `/clear`:

```text
system prompt       preserved
registered tools    preserved
conversation        empty
```

Only conversational messages are removed.

Do not rebuild the Registry.

Do not unregister tools.

Do not remove the system prompt.

---

## 10. Built-In REPL Commands

The REPL must intercept commands before they are sent to the Agent.

### `/help`

Print the built-in command list.

It must not be added to conversation history and must not be sent to the model.

### `/quiet`

Suppress detailed logger output using the existing Boukensha quiet-mode behavior.

Expected confirmation is equivalent in meaning to:

```text
(logging suppressed — type /loud to re-enable)
```

### `/loud`

Restore logger output.

Expected confirmation is equivalent in meaning to:

```text
(logging enabled)
```

### `/clear`

Call the Context message-clearing behavior.

Reset the REPL turn counter if required by the Ruby behavior.

Print confirmation equivalent in meaning to:

```text
(conversation history cleared)
```

Tools remain registered.

### `/exit`

Print a goodbye message and terminate the REPL.

### `/quit`

Alias for `/exit`.

### EOF / Ctrl-D

If stdin returns EOF, leave the REPL cleanly.

### Ctrl-C / KeyboardInterrupt

The top-level REPL composition path must terminate gracefully rather than exposing an uncontrolled traceback.

The Ruby behavior prints an interruption message.

The Python port should provide equivalent user-visible behavior.

---

## 11. REPL Prompt

Preserve the Ruby REPL prompt semantics.

Expected form:

```text
boukensha>
```

The prompt should:

1. be printed before reading input,
2. remain visible without requiring a newline first,
3. flush stdout before waiting for input.

Python may use `input()` if it preserves the required visible behavior, or explicit stdout/stdin operations if needed for fidelity.

Do not introduce a third-party terminal or TUI library in this step.

This is intentionally a basic terminal REPL.

---

## 12. REPL Banner

The Ruby REPL displays startup information including:

* Boukensha name,
* version,
* configuration directory,
* provider,
* API key status,
* basic command hints.

The Python port should reproduce the same informational intent.

The banner must never print the API key itself.

It may report only whether a key appears present or absent.

Example conceptual content:

```text
BOUKENSHA MUD Assistant
version: ...
config: ...
provider: ...

/quiet or /loud    toggle logging
/clear             reset conversation history
/exit or /quit     leave the REPL
```

Exact whitespace and decorative formatting may follow Python conventions unless output parity is explicitly required later.

---

## 13. Version Support

Ruby Step 8 introduces:

```ruby
Boukensha::VERSION = "0.8.0"
```

Python Step 8 must add equivalent version information.

Preferred implementation should follow the simplest architecture consistent with the existing Step 8 package.

Possible target:

```text
boukensha/version.py
```

with:

```python
VERSION = "0.8.0"
```

The version must be available to the REPL banner.

Do not introduce packaging metadata, semantic-version libraries, or build-system changes merely to represent this constant.

---

## 14. Top-Level `repl()` Composition Root

Python Step 8 must add a top-level REPL entry point alongside the existing `run()` entry point.

Conceptually:

```python
repl(
    system=None,
    model=None,
    backend=None,
    api_key=None,
    ollama_host="http://localhost:11434",
    log=None,
    max_output_tokens=None,
    configure=None,
)
```

The exact signature should preserve the Python Step 7 conventions while matching the Ruby Step 8 behavior.

Unlike `run()`, `repl()` has no required initial `task`.

The user supplies tasks interactively.

The composition flow should remain equivalent to:

```text
Config
  ↓
Task settings
  ↓
Context
  ↓
Registry
  ↓
RunDSL configuration
  ↓
Backend
  ↓
PromptBuilder
  ↓
Client
  ↓
Logger
  ↓
Repl
  ↓
start()
```

The same registered tools must remain available during the entire REPL session.

---

## 15. Run DSL Reuse

Step 8 does not introduce a second tool-registration DSL.

The existing Run DSL should be reused.

Conceptually:

```python
def configure_tools(dsl):
    dsl.tool(...)
    dsl.tool(...)

repl(configure=configure_tools)
```

or the equivalent API already established by Python Step 7.

Do not duplicate Registry or tool registration logic inside `Repl`.

---

## 16. Config Directory Resolution

Ruby Step 8 changes configuration-directory precedence.

The Python Step 8 port must compare the existing Python `Config` behavior and apply the Ruby delta if it is not already present.

Required precedence:

```text
1. BOUKENSHА_DIR environment variable
2. .boukensha in the current working directory, if present
3. ~/.boukensha
```

Conceptually:

```text
BOUKENSHA_DIR set?
      │
      ├── yes → use it
      │
      └── no
           ↓
./.boukensha exists?
      │
      ├── yes → use it
      │
      └── no
           ↓
~/.boukensha
```

Do not alter other configuration-loading behavior unless required by the Ruby delta.

---

## 17. Client Authentication Error

Ruby Step 8 adds special handling for HTTP 401.

Python Step 8 should port equivalent behavior if the Python Step 7 Client does not already provide it.

Expected semantic behavior:

```text
HTTP 401
   ↓
ApiError
   ↓
authentication failed (401) — check your API key
```

Do not log or expose the API key.

Other HTTP failure behavior should remain unchanged.

---

## 18. Example Migration

Copy Python Step 7 into:

```text
week1_baseline/python/08_the_repl_loop
```

Then update:

```text
examples/example.py
```

from one-shot execution:

```text
run(task=...)
```

to interactive execution:

```text
repl(...)
```

The example should continue to register the same functional tools:

```text
read_file
list_directory
```

Those tools must remain registered for the lifetime of the REPL.

Directory listing output should match the Ruby Step 8 deterministic behavior by sorting entries if the existing Python implementation does not already do so.

The example should not print a separate `FINAL RESPONSE` block because responses are now printed per REPL turn.

---

## 19. Example Working Directory

The Ruby Step 8 example deliberately points its file tools at the prior Run DSL iteration directory as a useful playground.

The Python implementation should preserve the instructor's intended behavior while adapting paths to the Python tree.

Expected conceptual target:

```text
week1_baseline/python/07_the_run_dsl
```

The exact implementation should use repository-relative path construction and must not depend on a user-specific absolute path.

---

## 20. Python Step 8 Runner

Create:

```text
week1_baseline/bin/python/08_the_repl_loop
```

Use the existing Python Step 7 runner as the direct baseline:

```text
week1_baseline/bin/python/07_the_run_dsl
```

The runner must preserve the existing Python runner architecture.

Expected functional delta:

```diff
- STEP_DIR=".../python/07_the_run_dsl"
+ STEP_DIR=".../python/08_the_repl_loop"
```

Preserve:

* Bash shebang,
* `set -euo pipefail`,
* repository-relative path discovery,
* shared Python virtual environment,
* interpreter existence/executable check,
* `cd` into the selected iteration,
* execution of `examples/example.py`.

Do not add REPL logic to the runner.

The REPL belongs in Python application code.

---

## 21. Expected File-Level Python Delta

The expected Python Step 7 → Step 8 semantic delta is:

```text
week1_baseline/python/08_the_repl_loop/

README.md
    update for REPL behavior

boukensha/__init__.py
    add public repl() composition root
    expose REPL/version as appropriate

boukensha/repl.py
    NEW
    interactive REPL implementation

boukensha/version.py
    NEW or equivalent
    VERSION = "0.8.0"

boukensha/agent.py
    persist final assistant responses in Context

boukensha/context.py
    add conversation-history clearing

boukensha/config.py
    add current-directory .boukensha resolution

boukensha/client.py
    special 401 authentication error

examples/example.py
    convert run() example into repl() example

week1_baseline/bin/python/08_the_repl_loop
    NEW runner copied from Step 7 and retargeted
```

Any additional changed Python file must be justified by the Ruby Step 8 delta or by a language-specific necessity.

---

## 22. Files Expected to Remain Unchanged

Files with no semantic Ruby Step 7 → Step 8 delta should remain copied unchanged unless Python-specific dependencies require otherwise.

Likely unchanged areas include:

```text
backends/*
message.py
prompt_builder.py
registry.py
run_dsl.py
tasks/*
tool.py
prompts/system.md
requirements.txt
```

This list must be verified during implementation rather than treated as permission to modify them.

The default rule is:

> If the Ruby counterpart did not change and Python does not require a compatibility adjustment, leave the Python file unchanged.

---

## 23. Fidelity Constraints

### Preserve per-turn Agent construction

Do not optimize it away.

### Preserve one shared Context

Conversation history must persist across prompts.

### Preserve one shared Registry

Tools must remain registered across prompts.

### Preserve one shared Logger

The REPL session should remain one logging session rather than silently creating a new log per terminal prompt.

### Preserve built-in command ownership

Commands such as `/clear` and `/exit` belong to the REPL and must not be sent to the LLM.

### Preserve existing `run()`

Step 8 adds `repl()`; it does not replace or redesign the one-shot API.

### Do not introduce a TUI

No Rich, Textual, prompt-toolkit, curses, or similar library in this step.

### Do not redesign legacy logging controls

If `/quiet` and `/loud` rely on existing Boukensha behavior, port that behavior faithfully even if later cleanup may change it.

---

## 24. Explicit Non-Goals

Do not:

* reuse one Agent across all turns,
* introduce long-term memory,
* summarize or compress conversation history,
* add token-budget pruning beyond existing Agent behavior,
* add persistent conversation storage beyond existing Logger behavior,
* implement command history or arrow-key navigation,
* implement autocomplete,
* implement multiline editing,
* build a text-user interface,
* refactor the backend architecture,
* redesign RunDSL,
* change tool schemas unnecessarily,
* redesign logging,
* remove existing one-shot `run()` behavior,
* “clean up” instructor architecture during the port.

These may be reasonable future improvements, but they are outside Step 8.

---

## 25. Implementation Order

Implementation should proceed in the following order.

### Phase 1 — Copy baseline

Copy:

```text
week1_baseline/python/07_the_run_dsl
```

to:

```text
week1_baseline/python/08_the_repl_loop
```

Do not implement features yet.

### Phase 2 — Supporting state changes

Implement:

```text
Context.clear_messages()
Agent final-response persistence
Config directory-resolution delta
Client HTTP 401 handling
Version constant
```

### Phase 3 — REPL primitive

Create:

```text
boukensha/repl.py
```

Implement:

```text
banner
prompt
stdin loop
/help
/quiet
/loud
/clear
/exit
/quit
EOF
run_turn()
per-turn Agent construction
error display
```

### Phase 4 — Top-level composition

Add:

```text
repl(...)
```

to the package's public interface.

Wire:

```text
Config
Context
Registry
RunDSL
Backend
PromptBuilder
Client
Logger
Repl
```

### Phase 5 — Example

Convert the Step 7 example from one-shot to interactive REPL usage.

### Phase 6 — Runner

Copy Python Step 7 runner and retarget it to Step 8.

### Phase 7 — Static verification

Compile and inspect before live execution.

### Phase 8 — Interactive verification

Run the REPL and verify its observable behavior.

---

## 26. Static Verification Plan

Before any live API execution:

### Python compilation

```bash
python3 -m compileall -q \
  week1_baseline/python/08_the_repl_loop/boukensha \
  week1_baseline/python/08_the_repl_loop/examples
```

Expected:

```text
no output
```

Remove generated caches afterward.

### Runner syntax

```bash
bash -n week1_baseline/bin/python/08_the_repl_loop
```

Expected:

```text
no output
```

### Runner executable check

```bash
test -x week1_baseline/bin/python/08_the_repl_loop
```

### Artifact scan

Check for:

```text
__pycache__
*.pyc
*.pyo
Zone.Identifier
```

None should remain before staging.

### Step 7 → Step 8 semantic review

Compare:

```text
python/07_the_run_dsl
python/08_the_repl_loop
```

and verify that every changed file corresponds to the approved port plan.

---

## 27. Interactive Verification Plan

The live REPL test should verify the new behavior rather than merely prove that the process launches.

### Test 1 — Startup

Run:

```text
week1_baseline/bin/python/08_the_repl_loop
```

Verify:

* banner prints,
* version appears,
* provider/config information appears,
* API key value is not exposed,
* `boukensha>` prompt appears.

### Test 2 — First agent turn

Ask a question requiring one of the registered tools.

Example:

```text
List the files in the current directory.
```

Verify:

* Agent executes,
* expected tool is called,
* final answer prints,
* REPL returns to `boukensha>`.

### Test 3 — Conversation persistence

Ask a follow-up that depends on the previous exchange.

Example:

```text
How many files did you just list?
```

Verify the answer uses accumulated context.

### Test 4 — `/help`

Enter:

```text
/help
```

Verify command help prints and no model call occurs.

### Test 5 — `/quiet`

Enter:

```text
/quiet
```

Verify detailed logger output is suppressed.

### Test 6 — `/loud`

Enter:

```text
/loud
```

Verify logger output resumes.

### Test 7 — `/clear`

Enter:

```text
/clear
```

Verify confirmation prints.

Then ask a question that depends on the pre-clear conversation.

Verify prior conversational messages are no longer available.

Registered tools must continue to function.

### Test 8 — `/exit`

Enter:

```text
/exit
```

Verify:

* goodbye message prints,
* REPL exits,
* shell prompt returns,
* exit status is successful.

### Optional Test 9 — `/quit`

Verify it behaves as an alias for `/exit`.

### Optional Test 10 — EOF

Verify Ctrl-D exits cleanly if practical.

---

## 28. Logging Verification

The Step 8 session should continue using JSONL logging.

Verify:

* one session log is created for the REPL session,
* multiple REPL turns are represented inside that session,
* tool calls/results remain logged,
* final model responses are represented,
* no API key or authorization secret is written into the log.

Do not print sensitive values during inspection.

Use structured parsing rather than blindly dumping an entire session log.

---

## 29. Acceptance Criteria

Python Step 8 is complete only when all of the following pass:

* [ ] Python Step 8 begins from the Step 7 baseline.
* [ ] Only approved Step 8 semantic deltas are introduced.
* [ ] `repl.py` exists.
* [ ] version support exists.
* [ ] public `repl()` entry point exists.
* [ ] existing `run()` still exists.
* [ ] same tool-registration DSL is reused.
* [ ] one shared Context survives across REPL turns.
* [ ] one shared Registry survives across REPL turns.
* [ ] assistant final responses are persisted into Context.
* [ ] `/clear` clears messages only.
* [ ] tools survive `/clear`.
* [ ] system prompt survives `/clear`.
* [ ] `/help` works.
* [ ] `/quiet` works.
* [ ] `/loud` works.
* [ ] `/exit` works.
* [ ] `/quit` works.
* [ ] EOF exits cleanly.
* [ ] Ctrl-C is handled gracefully at the REPL boundary.
* [ ] new Agent construction occurs per conversational turn.
* [ ] REPL prompt repeats after each completed turn.
* [ ] conversation history affects follow-up prompts.
* [ ] local `.boukensha` directory resolution follows the Ruby precedence.
* [ ] HTTP 401 produces the improved authentication error.
* [ ] example uses the REPL rather than one-shot `run()`.
* [ ] directory-listing output is deterministic where required.
* [ ] Python Step 8 runner exists.
* [ ] runner targets only Python Step 8.
* [ ] runner uses the shared Python virtual environment.
* [ ] Python compilation passes.
* [ ] runner Bash syntax passes.
* [ ] no runtime artifacts remain.
* [ ] live REPL execution succeeds.
* [ ] JSONL logging is verified.
* [ ] no credential leakage is detected.
* [ ] Git scope contains only intended Step 8 work.

---

## 30. Git Scope

Expected Step 8 deliverables:

```text
docs/plans/python_port/08_the_repl_loop.md

week1_baseline/python/08_the_repl_loop/

week1_baseline/bin/python/08_the_repl_loop
```

The restored instructor Ruby Step 8 source and Ruby runner material may also need to be committed to the local canonical repository if they are not already tracked, but that is a repository-synchronization concern separate from the Python implementation.

Do not use:

```bash
git add .
```

Stage explicit Step 8 paths only.

Before committing, verify:

```bash
git diff --cached --name-status
```

and confirm no runtime, credential, cache, unrelated documentation, or temporary analysis artifacts are included.

---

## 31. Architectural Observations — Do Not Fix During Port

The following observations should be documented but not corrected in Step 8:

### Agent recreated every turn

A persistent Agent could potentially be more efficient.

Do not change this behavior.

### REPL is intentionally primitive

The terminal interface is based on ordinary stdin/stdout.

Do not introduce a richer terminal framework yet.

### Conversation growth is unbounded at the REPL layer

The REPL itself does not add summarization, pruning, or long-term memory.

Do not introduce those capabilities.

### Quiet/loud may later be redesigned

Preserve the current behavior.

### Composition duplication exists between `run()` and `repl()`

Both composition roots perform similar setup.

Do not refactor this duplication during the faithful Step 8 port.

---

## 32. Architectural Meaning of Step 8

Step 7 introduced a simplified one-shot composition root.

Step 8 introduces persistent interaction.

The important progression is:

```text
Step 7
one task
   ↓
run()
   ↓
Agent loop
   ↓
one final answer
```

becoming:

```text
Step 8
REPL session
   ↓
many user turns
   ↓
each turn invokes Agent loop
   ↓
shared Context preserves conversation
```

This produces two nested loops:

```text
OUTER LOOP
REPL conversation
   │
   ├── turn 1
   │     └── INNER Agent loop
   │
   ├── turn 2
   │     └── INNER Agent loop
   │
   └── turn N
         └── INNER Agent loop
```

The REPL loop manages human interaction.

The Agent loop manages model/tool reasoning.

Keeping those responsibilities separate is the central architectural lesson of this iteration.

---

## 33. Approval Gate

No Python Step 8 implementation should begin until this plan is reviewed and explicitly approved.

Required sequence:

```text
Ruby Architecture Discovery
        ✓

Port Plan
        ↓

Review
        ↓

Approval
        ↓

Python implementation
```

### Current state

```text
Ruby Step 8 architecture discovery    COMPLETE
Python Step 8 port plan               PROPOSED
Plan review                           PENDING
Plan approval                         PENDING
Python Step 8 implementation          NOT STARTED
```

**Stop here for review.**
