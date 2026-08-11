# Python Week 1 Step 7 — The Run DSL Port Plan

## Status

Ruby Step 6 → Step 7 architecture discovery complete.

Python Step 7 implementation has **not** begun.

This document is the implementation contract for porting the Ruby `Boukensha.run` DSL iteration into Python.

Do not modify Python Step 7 source files until this plan has passed the approval gate.

---

# 1. Objective

Step 7 introduces a higher-level public API for running Boukensha agents.

Previous iterations required callers to manually create and connect:

- `Config`
- `Context`
- `Registry`
- provider Backend
- `PromptBuilder`
- `Client`
- `Logger`
- `Agent`

Step 7 moves that assembly logic behind a single top-level entry point:

```text
Boukensha.run(...)
```

The caller should describe:

```text
what task to perform
what tools are available
optional runtime overrides
```

rather than manually constructing the framework's internal dependency graph.

The central architectural rule is:

> Step 7 simplifies the public API without redesigning the Step 6 engine.

---

# 2. Architectural Motivation

Step 7 introduces two closely related architectural concepts:

## 2.1 Composition Root

A composition root is the place where application components are:

- instantiated
- configured
- connected
- started

Before Step 7, the composition root effectively lived in:

```text
examples/example.rb
```

The example manually created all major framework objects.

Step 7 moves that responsibility into:

```text
Boukensha.run(...)
```

The framework now owns object construction and dependency wiring.

---

## 2.2 Domain-Specific Language

DSL means:

```text
Domain-Specific Language
```

The Step 7 DSL gives the caller a deliberately small vocabulary for describing an agent run.

The Ruby DSL block exposes only:

```text
tool(...)
```

through:

```text
Boukensha::RunDSL
```

The DSL should not expose:

```text
Registry
Context internals
Logger internals
Client internals
Agent internals
```

This keeps the public interface intentionally small.

---

# 3. Source of Truth

Ruby Step 6:

```text
week1_baseline/ruby/06_the_logger
```

Ruby Step 7:

```text
week1_baseline/ruby/07_the_run_dsl
```

Primary Step 7 architectural files:

```text
week1_baseline/ruby/07_the_run_dsl/lib/boukensha.rb
week1_baseline/ruby/07_the_run_dsl/lib/boukensha/run_dsl.rb
week1_baseline/ruby/07_the_run_dsl/examples/example.rb
week1_baseline/ruby/07_the_run_dsl/README.md
```

Supporting changed Ruby files:

```text
week1_baseline/ruby/07_the_run_dsl/lib/boukensha/config.rb
week1_baseline/ruby/07_the_run_dsl/lib/boukensha/context.rb
week1_baseline/ruby/07_the_run_dsl/lib/boukensha/logger.rb
week1_baseline/ruby/07_the_run_dsl/lib/boukensha/errors.rb
```

Python Step 6 baseline:

```text
week1_baseline/python/06_the_logger
```

Target Python iteration:

```text
week1_baseline/python/07_the_run_dsl
```

---

# 4. Verified Ruby Step 6 → Step 7 Scope

The Ruby directory comparison identified these meaningful differences.

## Modified

```text
README.md
examples/example.rb
lib/boukensha.rb
lib/boukensha/config.rb
lib/boukensha/context.rb
lib/boukensha/errors.rb
lib/boukensha/logger.rb
```

## New

```text
lib/boukensha/run_dsl.rb
```

The Ruby comparison did **not** identify meaningful Step 7 changes in:

```text
agent.rb
client.rb
prompt_builder.rb
registry.rb
tool.rb

backends/anthropic.rb
backends/base.rb
backends/gemini.rb
backends/ollama.rb
backends/ollama_cloud.rb
backends/openai.rb
```

Therefore those Python files should remain unchanged unless later evidence proves otherwise.

---

# 5. Before and After

## Step 6 — Manual Composition

Conceptually:

```text
Application
    │
    ├── Config
    ├── Context
    ├── Registry
    ├── Backend
    ├── PromptBuilder
    ├── Client
    ├── Logger
    └── Agent
          │
          ▼
       agent.run()
```

The application owns the dependency graph.

---

## Step 7 — Framework Composition

Conceptually:

```text
Application
    │
    ▼
run(...)
    │
    ├── Config
    ├── Context
    ├── Registry
    ├── Backend
    ├── PromptBuilder
    ├── Client
    ├── Logger
    └── Agent
          │
          ▼
       agent.run()
```

The framework owns the dependency graph.

The internal Step 6 objects still exist.

Only their construction moves behind the public API.

---

# 6. The Ruby `RunDSL` Contract

Ruby introduces:

```text
Boukensha::RunDSL
```

This class is intentionally tiny.

Its responsibilities are limited to:

1. storing a reference to the Registry;
2. exposing `tool(...)`;
3. forwarding tool registration to the Registry.

Conceptually:

```text
RunDSL
   │
   └── tool(...)
          │
          ▼
       Registry.tool(...)
```

`RunDSL` must not become another orchestration object.

The orchestration belongs in the top-level `run(...)` composition root.

---

# 7. Python `run_dsl.py`

Create:

```text
week1_baseline/python/07_the_run_dsl/boukensha/run_dsl.py
```

This is a new file.

Its conceptual responsibility should mirror the Ruby `RunDSL`.

Expected structure:

```python
class RunDSL:
    def __init__(self, registry):
        self._registry = registry

    def tool(...):
        ...
```

The Python implementation should preserve the existing Python Registry API rather than inventing a new registration mechanism.

Do not:

- create Config here
- create Context here
- create Backend here
- create Client here
- create Logger here
- create Agent here
- execute the Agent here

Those responsibilities belong to the composition root.

---

# 8. Python DSL Syntax

Ruby uses:

```ruby
Boukensha.run(...) do
  tool ...
end
```

Python does not have Ruby blocks or `instance_eval`.

Therefore the Python port must preserve the **architectural intent**, not force Ruby syntax into Python.

Before implementation, inspect existing Python project conventions and choose the smallest idiomatic equivalent.

Possible conceptual forms include:

```python
run(
    task="...",
    configure=lambda dsl: ...
)
```

or another minimal callback-based mechanism.

Do not choose the final Python DSL syntax until:

1. the Python Step 6 API is inspected;
2. the port design is reviewed;
3. the syntax preserves the intentionally small DSL surface.

The Python API must not expose the Registry merely for convenience if Ruby intentionally hides it.

---

# 9. The Composition Root

The central Step 7 implementation belongs in the package-level `run(...)` entry point.

Ruby `Boukensha.run(...)` performs the following sequence.

Python should preserve this sequence conceptually.

---

# 10. Step 1 — Load Config

Ruby:

```text
cfg = config
```

The global/package config instance loads:

```text
.boukensha configuration
.env
settings.yaml
```

Python Step 7 should continue using the existing Step 6 configuration machinery rather than creating a separate configuration system.

---

# 11. Step 2 — Resolve Task Class

Ruby uses:

```text
Tasks::Player
```

as the task class.

Python should mirror the existing Python equivalent:

```text
Player
```

Do not introduce dynamic task discovery unless the Ruby Step 7 implementation does.

---

# 12. Step 3 — Resolve Task Settings

Ruby retrieves task settings using the task's name.

Conceptually:

```text
cfg.tasks(task_class.task_name)
```

Python must preserve the existing Python task settings contract.

Pay particular attention to whether:

```text
task_name
```

is a method or property.

Do not repeat the Step 6 serialization mistake where a method object was passed instead of its return value.

---

# 13. Step 4 — Resolve System Prompt

If the caller does not explicitly supply a system prompt, Ruby resolves it from:

```text
task_class.system_prompt(...)
```

using:

```text
task settings
user prompt directory
default prompt directory
```

Python should reuse the existing Player prompt-resolution API.

Do not duplicate prompt-loading logic inside `run()`.

---

# 14. Step 5 — Resolve Model

If the caller does not supply a model:

```text
task_class.model(task_settings)
```

provides the configured value.

An explicit caller override should take precedence.

---

# 15. Step 6 — Resolve Provider / Backend Name

If the caller does not supply a backend/provider, Ruby resolves it from the Player task configuration.

The Ruby implementation supports:

```text
anthropic
openai
gemini
ollama
ollama_cloud
```

Python should preserve the provider implementations already present in Step 6.

Do not redesign provider selection.

---

# 16. Step 7 — Resolve API Key

Ruby maps provider names to environment variables.

Conceptually:

```text
anthropic
    ↓
ANTHROPIC_API_KEY

openai
    ↓
OPENAI_API_KEY

gemini
    ↓
GEMINI_API_KEY

ollama_cloud
    ↓
OLLAMA_API_KEY

ollama
    ↓
no hosted API key required
```

Python should reuse the same environment values already expected by the existing backend classes.

Do not log API keys.

---

# 17. Step 8 — Create Context

Ruby creates:

```text
Context(
    task: Player,
    system: resolved_system_prompt
)
```

Python should use the existing Step 6 Context class.

No new Agent behavior should be introduced here.

---

# 18. Step 9 — Create Registry

Ruby creates:

```text
Registry(context)
```

Python should reuse the Step 6 Registry unchanged unless a verified Step 7 delta requires otherwise.

---

# 19. Step 10 — Execute the DSL Configuration

Ruby does:

```text
RunDSL.new(registry).instance_eval(&block)
```

This makes the DSL host responsible for registering tools before the Agent is created and executed.

Python must preserve that lifecycle:

```text
create registry
      ↓
create RunDSL
      ↓
caller registers tools through RunDSL
      ↓
continue composition
```

Tool configuration must happen before the agent begins execution.

---

# 20. Step 11 — Construct Backend

Ruby maps the selected backend name to an existing backend implementation.

Conceptually:

```text
anthropic
    ↓
Anthropic(...)

openai
    ↓
OpenAI(...)

gemini
    ↓
Gemini(...)

ollama
    ↓
Ollama(...)

ollama_cloud
    ↓
OllamaCloud(...)
```

Unknown providers raise an argument/configuration error.

Python should reuse the existing Step 6 backend constructors.

Do not modify provider internals unless a verified mismatch is discovered.

---

# 21. Step 12 — Construct PromptBuilder

Ruby creates:

```text
PromptBuilder(context, backend)
```

Python should reuse the existing Step 6 PromptBuilder.

No Step 7 PromptBuilder redesign is planned.

---

# 22. Step 13 — Construct Client

Ruby creates:

```text
Client(builder)
```

Python should reuse the Step 6 Client unchanged.

---

# 23. Step 14 — Resolve Iteration and Output Limits

Ruby resolves:

```text
max_iterations
max_output_tokens
```

from task settings.

An explicit `max_output_tokens` argument may override task configuration.

Python must preserve the existing Player resolver behavior.

Do not duplicate default values in multiple places if the existing task class already owns them.

---

# 24. Step 15 — Construct Logger

Ruby creates Logger with a session snapshot containing execution metadata.

The snapshot includes conceptually:

```text
task
max_iterations
max_output_tokens
model
provider
```

Python should preserve the Step 6 Logger API.

If Python Step 6 already supports:

```text
snapshot=
log=
```

reuse it.

Do not introduce a second logging implementation.

---

# 25. Step 16 — Construct Agent

Ruby creates the existing Agent with:

```text
context
registry
builder
client
logger
task_settings
max_iterations
max_output_tokens
```

Python should reuse the Step 6 Agent unchanged unless the Ruby Step 7 delta proves otherwise.

The architecture discovery currently indicates:

```text
agent.rb unchanged
```

Therefore Python `agent.py` should not be modified during Step 7 unless later evidence contradicts this.

---

# 26. Step 17 — Add User Task Message

Ruby adds:

```text
task
```

to Context as the user message immediately before agent execution.

Python should preserve the same lifecycle.

---

# 27. Step 18 — Run Agent

Ruby finishes composition by invoking:

```text
agent.run
```

Python `run(...)` should return the Agent's final result.

The DSL entry point should not alter the final response semantics.

---

# 28. Step 19 — Close Logger Reliably

Ruby uses:

```text
ensure
```

to close the logger even if execution raises.

Python should use an equivalent reliable cleanup mechanism such as:

```text
try / finally
```

The logger must be closed on both:

```text
successful execution
exceptional execution
```

Do not silently swallow execution errors merely to close the logger.

---

# 29. Proposed Python Public API

The final API must remain simple.

Conceptually:

```python
result = run(
    task="Read README.md and summarize it",
    ...
)
```

plus a mechanism for configuring tools through the intentionally limited `RunDSL`.

The exact callback/block-equivalent syntax must be chosen during implementation review.

Public caller concerns should be limited to:

```text
task
optional system override
optional model override
optional backend override
optional API key override
optional Ollama host override
optional log path override
optional max output token override
tool registration
```

Internal plumbing must remain hidden.

---

# 30. Ruby `run(...)` Parameters

Ruby Step 7 exposes:

```text
task
system
model
backend
api_key
ollama_host
log
max_output_tokens
```

Python should preserve the same conceptual options unless Python naming conventions require minor syntactic differences.

Do not add extra Step 7 arguments merely because they might be useful.

---

# 31. Source Documentation Discrepancy

There is a documentation mismatch in the supplied Ruby sources that must not be silently reconciled.

The README table describes the backend option more narrowly:

```text
anthropic
ollama
```

while the actual Ruby `Boukensha.run` implementation supports:

```text
anthropic
openai
gemini
ollama
ollama_cloud
```

For the Python port:

1. treat the executable Ruby implementation as the behavioral source of truth;
2. preserve the discrepancy in notes;
3. do not rewrite unrelated Ruby documentation;
4. do not invent additional backends beyond those implemented.

---

# 32. `config.py`

Ruby `config.rb` differs between Step 6 and Step 7.

Before editing Python:

```text
compare Ruby Step 6 config.rb
against Ruby Step 7 config.rb
```

Only port the proven delta.

The Step 7 Ruby Config shown during architecture discovery supports:

```text
BOUKENSHA_DIR override
default ~/.boukensha
.env loading
settings.yaml loading
task settings
user prompt directory
MUD configuration accessors
```

Do not assume all of those are new in Step 7.

The direct diff must determine Python scope.

---

# 33. `context.py`

Ruby `context.rb` differs between Step 6 and Step 7.

The Step 7 Context remains responsible for:

```text
task
system
messages
tools
register_tool
add_message
tool_count
turn_count
```

Before editing Python:

```text
compare Ruby Step 6 context.rb
against Ruby Step 7 context.rb
```

Only port the actual delta.

Do not move DSL orchestration into Context.

---

# 34. `logger.py`

Ruby `logger.rb` differs between Step 6 and Step 7.

The Step 7 Logger shown during architecture discovery includes:

```text
session_start
turn
iteration
limit_reached
turn_end
prompt
tool_call
tool_result
response
raw
subscribe
close
```

It also:

```text
writes JSONL
flushes each record
supports subscribers
derives execution metadata
estimates cost
```

Do not assume every method is new.

Before editing Python:

```text
compare Ruby Step 6 logger.rb
against Ruby Step 7 logger.rb
```

Only port proven Step 7 behavior.

---

# 35. `errors.py`

Ruby `errors.rb` appears in the changed-file list.

Its exact Step 6 → Step 7 functional delta has not yet been inspected.

Therefore:

```text
DO NOT modify Python errors.py yet.
```

First compare:

```text
Ruby Step 6 errors.rb
against
Ruby Step 7 errors.rb
```

If the difference is:

```text
formatting
comments
unrelated cleanup
```

skip the Python file.

If a functional error type required by `run(...)` was added, port only that delta.

---

# 36. `__init__.py`

Python Step 7 package-level work is expected to be significant.

Target:

```text
week1_baseline/python/07_the_run_dsl/boukensha/__init__.py
```

Expected conceptual responsibilities:

```text
preserve Step 6 exports
export RunDSL if appropriate
expose top-level run(...)
preserve config()
preserve debug API
preserve quiet/loud API
```

Do not remove existing Step 6 public interfaces.

The package-level `run(...)` function becomes the Python composition root.

---

# 37. `example.py`

Target:

```text
week1_baseline/python/07_the_run_dsl/examples/example.py
```

The example should become substantially simpler.

It should demonstrate the **new public API**, not manually construct framework internals.

The Python example should no longer manually instantiate:

```text
Context
Registry
Backend
PromptBuilder
Client
Logger
Agent
```

unless Python language constraints make a specific object necessary.

The example should primarily show:

```text
configuration display
run(...)
tool declarations
final response
```

---

# 38. Files Expected to Remain Unchanged

Based on the verified Ruby Step 6 → Step 7 directory comparison, do not modify the Python equivalents of:

```text
agent.py
client.py
prompt_builder.py
registry.py
tool.py

backends/base.py
backends/anthropic.py
backends/gemini.py
backends/ollama.py
backends/ollama_cloud.py
backends/openai.py
```

Any proposed edit to one of these files requires a new evidence review before proceeding.

---

# 39. Python Implementation Order

Approved provisional implementation order:

```text
1. copy Python 06_the_logger → 07_the_run_dsl

2. run_dsl.py
   NEW DSL host

3. __init__.py
   add run() composition root

4. example.py
   replace manual composition with DSL usage

5. config.py
   ONLY verified Ruby delta

6. context.py
   ONLY verified Ruby delta

7. logger.py
   ONLY verified Ruby delta

8. errors.py
   ONLY if functional Ruby delta requires it

9. runner

10. execute

11. verify
```

Supporting-file steps may be skipped entirely if their Ruby changes do not require Python changes.

---

# 40. Runner

Create:

```text
week1_baseline/bin/python/07_the_run_dsl
```

Start from:

```text
week1_baseline/bin/python/06_the_logger
```

The expected runner delta should be minimal:

```text
06_the_logger
      ↓
07_the_run_dsl
```

Preserve:

```text
repository-relative path discovery
shared Python virtual environment
caller-directory independence
bash strict mode
executable permissions
```

The runner itself should not contain DSL logic.

---

# 41. Build Verification

Before the first API execution:

```text
compile all Python Step 7 files
remove __pycache__
check runner syntax
verify runner executable permissions
verify no Zone.Identifier files
```

No live API execution should occur until the source review gates pass.

---

# 42. End-to-End Verification

A successful Step 7 execution must demonstrate:

```text
run(...) called
      ↓
Config resolved
      ↓
Context created
      ↓
Registry created
      ↓
DSL tools registered
      ↓
Backend created
      ↓
PromptBuilder created
      ↓
Client created
      ↓
Logger created
      ↓
Agent created
      ↓
User task added
      ↓
Agent executes
      ↓
Tool calls work
      ↓
Final response returned
      ↓
Logger closed
```

---

# 43. Behavioral Regression Gate

Step 7 must preserve Step 6 behavior.

Verify:

```text
Agent still performs multiple iterations when necessary.
Tool calls still dispatch correctly.
Tool results still enter Context.
Final response still returns.
JSONL session file still appears.
Response metadata still logs.
Debug raw logging remains debug-only.
Iteration limits still work.
```

The Run DSL must change the **entry point**, not the Agent's execution semantics.

---

# 44. DSL Encapsulation Gate

The Python Step 7 API should not require application callers to understand or manually manipulate:

```text
Registry
PromptBuilder
Client
Logger
Agent
```

for the normal "hello world" path.

If callers still need to manually wire those components, the Step 7 port has failed its architectural objective even if the program technically runs.

---

# 45. Configuration Override Verification

Test both:

```text
configured defaults
```

and at least one explicit override.

Potential controlled overrides include:

```text
model
backend
max_output_tokens
log path
```

Do not expose credentials during verification.

---

# 46. Tool Registration Verification

Verify that a tool registered through the Python DSL:

```text
appears in Context
is sent to the model
can be selected by the model
dispatches through Registry
returns a tool result
allows the Agent loop to continue
```

This proves the DSL is more than cosmetic syntax.

---

# 47. Logger Lifecycle Verification

Because `run(...)` owns Logger creation, it must also own Logger cleanup.

Verify:

```text
Logger session file is created.
Logger records the normal lifecycle.
Logger closes after successful execution.
Logger closes when an execution exception occurs.
```

The cleanup path should use Python `try/finally` or equivalent semantics.

---

# 48. JSONL Verification

Validate the generated Step 7 session:

```text
every non-empty line parses independently
one session ID is used throughout
expected phases appear
raw is absent during normal mode
credentials are absent
```

The exact number of records depends on the Agent execution.

Do not assert an invented fixed event count.

---

# 49. Portability Verification

The runner must work from:

```text
repository root
/tmp
```

or another unrelated caller directory.

This proves the runner does not depend on the current working directory.

---

# 50. Git Hygiene

Before staging:

```text
remove __pycache__
remove *.pyc
remove *.pyo
remove Zone.Identifier artifacts
run git diff --check
review git status
```

Do not use:

```text
git add .
```

Stage only the Step 7 implementation, runner, plan, and explicitly required validation artifacts.

---

# 51. Expected Python Step 6 → Step 7 Delta

Expected meaningful files:

```text
NEW
boukensha/run_dsl.py

CHANGED
boukensha/__init__.py
examples/example.py

POSSIBLY CHANGED — ONLY AFTER RUBY DELTA REVIEW
boukensha/config.py
boukensha/context.py
boukensha/logger.py
boukensha/errors.py

NEW
week1_baseline/bin/python/07_the_run_dsl
```

Expected unchanged core engine:

```text
agent.py
client.py
prompt_builder.py
registry.py
tool.py
provider backends
```

Unexpected core-engine changes require review before staging.

---

# 52. Verification Checklist

Before commit:

```text
[ ] Python Step 7 baseline copied from completed Step 6.
[ ] Ruby changed-file scope documented.
[ ] run_dsl.py mirrors Ruby RunDSL responsibility.
[ ] RunDSL exposes only the intended DSL surface.
[ ] top-level run() acts as composition root.
[ ] Config resolves before backend creation.
[ ] task settings resolve correctly.
[ ] explicit overrides take precedence where Ruby supports them.
[ ] Context is created internally.
[ ] Registry is created internally.
[ ] DSL tools register before Agent execution.
[ ] selected Backend is created internally.
[ ] PromptBuilder is created internally.
[ ] Client is created internally.
[ ] Logger is created internally.
[ ] Agent is created internally.
[ ] task message is added internally.
[ ] Agent result is returned by run().
[ ] Logger closes reliably.
[ ] Step 6 Agent behavior is preserved.
[ ] Tool calls execute successfully.
[ ] JSONL session logging still works.
[ ] no credentials appear in logs.
[ ] runner works from repository root.
[ ] runner works from /tmp.
[ ] no Python caches are staged.
[ ] no Zone.Identifier files are staged.
[ ] only intentional Step 7 files are staged.
[ ] runner is executable.
```

---

# 53. Approval Gate

Do not begin Python implementation until this document is reviewed.

The approval review must answer:

```text
1. Does the Python design preserve the Ruby composition-root architecture?

2. Is RunDSL intentionally small?

3. Does run() hide internal plumbing?

4. Are unchanged Step 6 engine files protected from unnecessary edits?

5. Are supporting-file changes evidence-driven rather than assumed?

6. Is the proposed Python DSL idiomatic without exposing extra internal state?

7. Is Logger lifecycle ownership clear?

8. Is the verification plan sufficient to prove both simplicity and behavioral parity?
```

---

# 54. Guiding Principle

The central Step 7 principle is:

> The framework should own the plumbing; the caller should describe the intent.

Or, stated architecturally:

```text
Step 6:
caller owns composition

Step 7:
framework owns composition
```

The Run DSL must simplify how Boukensha is used without changing how the underlying Agent Loop behaves.

Do not use Step 7 as an opportunity for unrelated refactoring.

---

# 55. Final Acceptance Criteria

Step 7 is complete when:

1. Python exposes a single high-level `run(...)` entry point.
2. The caller can register tools through a deliberately limited DSL surface.
3. The caller no longer manually creates the standard Boukensha dependency graph.
4. Existing Step 6 engine components remain behaviorally unchanged.
5. Configuration and provider defaults resolve automatically.
6. Explicit supported overrides work.
7. Tool calls execute correctly.
8. Final Agent responses are returned correctly.
9. JSONL logging still records the run.
10. Logger cleanup is reliable.
11. The Step 7 runner works independent of caller directory.
12. Git scope is clean.
13. The completed implementation is reviewed, committed, and pushed.