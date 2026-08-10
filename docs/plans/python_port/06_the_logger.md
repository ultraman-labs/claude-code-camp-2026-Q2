# Python Week 1 Step 6 — The Logger Port Plan

## Status

Ruby Step 5 → Step 6 analysis complete.

Python implementation has **not** begun.

This document is the implementation contract for porting the Ruby Logger iteration into Python.

Do not make Python Step 6 changes outside the scope defined here unless a verified Ruby Step 5 → Step 6 delta requires them.

---

# 1. Purpose

Step 6 adds structured observability to the existing Agent Loop.

The Ruby implementation introduces `Boukensha::Logger`, a file-based logger that records each Agent run as structured JSON Lines (`.jsonl`).

The Logger is not user-facing application output.

Its purpose is to record machine-readable execution events such as:

- session start
- iteration
- prompt
- tool call
- tool result
- model response
- raw provider response when debugging is enabled
- iteration/turn termination
- token usage
- task/provider/model metadata
- estimated cost

The underlying Agent Loop behavior should remain functionally equivalent to Step 5.

Step 6 is primarily an **observability layer**, not a redesign of the Agent execution model.

---

# 2. Source of Truth

Ruby Step 5:

```text
week1_baseline/ruby/05_agent_loop
```

Ruby Step 6:

```text
week1_baseline/ruby/06_the_logger
```

Primary Ruby files:

```text
week1_baseline/ruby/06_the_logger/lib/boukensha/logger.rb
week1_baseline/ruby/06_the_logger/lib/boukensha/agent.rb
week1_baseline/ruby/06_the_logger/lib/boukensha.rb
week1_baseline/ruby/06_the_logger/examples/example.rb
week1_baseline/ruby/06_the_logger/lib/boukensha/backends/openai.rb
```

Python Step 5 baseline:

```text
week1_baseline/python/05_agent_loop
```

Target Python iteration:

```text
week1_baseline/python/06_the_logger
```

---

# 3. Architectural Overview

Step 5:

```text
User
  ↓
Context
  ↓
PromptBuilder
  ↓
Client
  ↓
Provider Backend
  ↓
Agent
  ↓
Registry / Tools
  ↓
Final Response
```

Step 6 introduces Logger instrumentation around that existing flow:

```text
                    Logger
                      ▲
                      │
          ┌───────────┼─────────────┐
          │           │             │
          │       execution         │
          │         events          │
          │           │             │
          ▼           ▼             ▼

User → Context → PromptBuilder → Client → Backend
                   ↑                  │
                   │                  ▼
                   └──── Agent ← normalized response
                          │
                          ├── iteration
                          ├── prompt
                          ├── raw response
                          ├── response
                          ├── tool call
                          ├── tool result
                          └── turn end
```

The Logger observes execution.

It does not:

- choose tools
- dispatch tools
- construct prompts
- make HTTP requests
- select providers
- determine when the Agent should stop

Those responsibilities remain with the existing components.

---

# 4. Verified Ruby Step 5 → Step 6 Scope

The Ruby comparison identified the following important changes:

```text
NEW:
lib/boukensha/logger.rb

CHANGED:
lib/boukensha/agent.rb
lib/boukensha.rb
examples/example.rb
lib/boukensha/backends/openai.rb

OTHER SMALL DELTAS:
README.md
config/context/errors/prompt_builder-related files may differ and must
be reviewed before deciding whether they require Python changes.
```

The provider comparison showed no material Step 6 implementation changes in:

```text
anthropic.rb
gemini.rb
ollama.rb
ollama_cloud.rb
```

Therefore those Python providers should not be modified unless later inspection proves a missing dependency.

---

# 5. Required Python Implementation Order

Port Step 6 in this order:

1. `logger.py`
2. `agent.py`
3. `__init__.py`
4. `example.py`
5. `openai.py` — only the verified Ruby Step 6 delta
6. runner
7. execute
8. verify

Each file must pass its review gate before proceeding to the next file.

---

# 6. Step 1 — Create `logger.py`

Target:

```text
week1_baseline/python/06_the_logger/boukensha/logger.py
```

Ruby source:

```text
week1_baseline/ruby/06_the_logger/lib/boukensha/logger.rb
```

This is a new Python file.

## 6.1 Logger Responsibilities

The Logger owns:

- session ID generation
- session log path selection
- creation of the session directory
- opening the JSONL log stream
- writing one JSON object per line
- flushing each log entry immediately
- timestamping events
- serialization of Context messages for prompt logging
- normalization of usage/token fields
- provider/model/task execution metadata
- estimated provider cost when backend pricing data is available

The Agent should not implement any of those responsibilities itself.

---

# 7. Logger Constructor Contract

Ruby Step 6 supports conceptually:

```ruby
Logger.new(
  session_id: nil,
  dir: nil,
  log: nil,
  snapshot: {}
)
```

Python should preserve the same behavior using Python conventions.

Conceptual target:

```python
Logger(
    session_id=None,
    dir=None,
    log=None,
    snapshot=None,
)
```

The exact Python argument spelling should follow established project conventions while preserving Ruby semantics.

## 7.1 Session ID

If no session ID is supplied, generate one.

The Ruby implementation uses:

```text
UTC timestamp + random hexadecimal suffix
```

Conceptually:

```text
YYYYMMDDTHHMMSSZ-<random>
```

The Python version should preserve that semantic format.

## 7.2 Default Session Directory

The Ruby default directory is:

```text
<Boukensha config dir>/sessions
```

Normal Step 6 usage should therefore write sessions beneath:

```text
.boukensha/sessions/
```

The Logger may also accept an explicit destination directory.

## 7.3 Log File

Normal session output:

```text
.boukensha/sessions/<session-id>.jsonl
```

A compatibility `log` argument may accept an explicit log path if the Ruby contract requires it.

---

# 8. JSONL Event Contract

Every line must be a complete JSON object.

Every event written by the Logger must contain at least:

```text
phase
session_id
at
```

plus event-specific fields.

Conceptual example:

```json
{"phase":"iteration","n":1,"max":25,"session_id":"...","at":"..."}
```

The writer must append a newline after every JSON object.

The log stream should be flushed after each event so that the file can be observed while the Agent is running.

---

# 9. Logger Public API

The Ruby README and implementation define one method per execution phase.

Python should preserve the same conceptual API.

## 9.1 `iteration`

Ruby:

```text
iteration(n:, max:)
```

Python conceptual API:

```python
iteration(n, max)
```

Log:

```text
phase: iteration
n
max
```

---

## 9.2 `limit_reached`

Ruby:

```text
limit_reached(kind:, n:, max:)
```

Log:

```text
phase: limit_reached
kind
n
max
```

This records when an Agent execution threshold is reached.

---

## 9.3 `turn_end`

Ruby:

```text
turn_end(reason:, iterations:, tokens: nil)
```

Log:

```text
phase: turn_end
reason
iterations
tokens
```

---

## 9.4 `prompt`

Ruby:

```text
prompt(messages:, tools:)
```

The event includes:

```text
phase: prompt
message_count
messages
tool_count
tools
```

Messages should be serialized into Logger-safe structures rather than writing arbitrary Python objects directly.

---

## 9.5 `tool_call`

Ruby:

```text
tool_call(name:, args:)
```

Log:

```text
phase: tool_call
name
args
```

---

## 9.6 `tool_result`

Ruby:

```text
tool_result(
    name:,
    result:,
    ok: true,
    error: nil
)
```

Log:

```text
phase: tool_result
name
result
ok
error
```

Tool failures should still generate a `tool_result` event.

---

## 9.7 `response`

Ruby:

```text
response(
    text:,
    usage: nil,
    stop_reason: nil,
    task: nil,
    backend: nil
)
```

The response event should contain:

```text
phase: response
text
usage
stop_reason
task
provider
model
usage_unit
usage_level
input_tokens
output_tokens
cost_usd
```

Fields unavailable from a provider should remain absent/null according to the Ruby behavior rather than being fabricated.

---

## 9.8 `raw`

Ruby:

```text
raw(data:)
```

Raw provider responses are written **only when debug mode is enabled**.

Normal Step 6 execution should not write raw provider data unless explicitly enabled.

---

## 9.9 `close`

The Logger should expose a way to close its log stream.

It should not leave file descriptors open indefinitely.

---

# 10. Usage Normalization

Provider APIs use different names for token usage.

The Ruby Logger normalizes several possible usage keys into:

```text
input
output
```

Examples found in the Ruby implementation include provider variants conceptually corresponding to:

```text
input_tokens
prompt_tokens
promptTokenCount
prompt_eval_count

output_tokens
completion_tokens
candidatesTokenCount
eval_count
```

The Python Logger must support the same Ruby Step 6 key aliases.

Do not introduce aliases that are not present in the Ruby implementation during this port.

---

# 11. Cost Estimation

Logger response events may include:

```text
cost_usd
```

when:

1. both normalized input and output token counts are available, and
2. the backend supports cost estimation.

The Logger should delegate cost calculation to the backend rather than duplicating pricing tables.

Conceptually:

```python
backend.estimate_cost(
    input_tokens=...,
    output_tokens=...,
)
```

If cost cannot be calculated, no artificial value should be generated.

---

# 12. Execution Metadata

Response events derive metadata from:

```text
task
backend
usage
```

Metadata may include:

```text
task
provider
model
usage_unit
usage_level
input_tokens
output_tokens
cost_usd
```

Provider naming should be derived consistently from the backend type, matching the Ruby behavior.

---

# 13. Step 2 — Port `agent.py`

Target:

```text
week1_baseline/python/06_the_logger/boukensha/agent.py
```

Source:

```text
Ruby Step 5 agent.rb
→
Ruby Step 6 agent.rb
```

The Step 5 Agent Loop behavior must remain intact.

Step 6 adds Logger instrumentation.

## 13.1 Constructor

Add Logger dependency injection.

Conceptually:

```python
Agent(
    context=...,
    registry=...,
    builder=...,
    client=...,
    logger=...,
    task_settings=...,
    max_iterations=...,
    max_output_tokens=...,
)
```

The Ruby implementation provides a default Logger instance.

Python should mirror the Ruby Step 6 semantics rather than requiring every caller to supply one if Ruby does not.

---

# 14. Agent Logging Points

The Ruby Agent adds Logger calls at specific execution points.

Python must instrument the same points.

## 14.1 Iteration Limit

When the iteration limit is reached:

```text
logger.limit_reached(...)
```

must be written before wrap-up behavior.

---

## 14.2 Iteration Start

For each normal Agent iteration:

```text
logger.iteration(...)
```

---

## 14.3 Prompt

Before making the Client request:

```text
logger.prompt(...)
```

using the current Context messages and tools.

---

## 14.4 Raw Provider Response

Immediately after the Client returns:

```text
logger.raw(...)
```

The Logger itself decides whether raw output is recorded based on debug mode.

---

## 14.5 Parsed Response

For a final response:

```text
logger.response(...)
```

must capture:

- final text
- usage
- stop reason
- active task
- backend

Then:

```text
logger.turn_end(...)
```

records completion.

---

## 14.6 Tool-Use Response

When a model response contains tool calls, the Agent should log the model response before dispatching the tools.

The Ruby implementation derives a text/reasoning representation when available and otherwise records a tool-use summary.

Do not invent provider-specific reasoning data beyond what the Ruby code exposes.

---

## 14.7 Tool Call

Before dispatch:

```text
logger.tool_call(...)
```

must record:

```text
tool name
tool arguments
```

---

## 14.8 Tool Success

After successful dispatch:

```text
logger.tool_result(
    ...,
    ok=True,
)
```

---

## 14.9 Tool Failure

The Ruby Agent catches tool dispatch exceptions and converts them into tool-result content rather than crashing the entire Agent loop.

Python should mirror that Step 6 behavior.

On failure:

```text
logger.tool_result(
    ...,
    ok=False,
    error=...
)
```

must be written.

The resulting error text should still be added to Context as a tool result according to the Ruby semantics.

---

# 15. Wrap-Up Logging

Step 5 wrap-up behavior remains.

Step 6 additionally logs:

```text
response
turn_end
```

for the wrap-up request.

If the wrap-up request fails with `ApiError`, the fallback message is still returned and `turn_end` must still be logged.

---

# 16. Usage Extraction in Agent

The Ruby Agent contains logic that extracts provider usage information from several response shapes.

Python should port only the Ruby-supported fields.

Examples include:

```text
response["usage"]
response["usageMetadata"]
```

and selected top-level token counters when present.

This normalized usage object is passed to Logger.

Usage normalization should not change provider payload behavior.

---

# 17. Step 3 — Public Package Interface

Target:

```text
week1_baseline/python/06_the_logger/boukensha/__init__.py
```

Ruby Step 6 introduces public logger/debug infrastructure.

The Python package should expose Logger if required to match the Ruby public API.

Expected addition conceptually:

```python
from .logger import Logger
```

and update:

```python
__all__
```

accordingly.

Do not modify unrelated existing exports.

---

# 18. Debug State

Ruby Step 6 introduces module-level state supporting:

```text
quiet!
loud!
quiet?

debug!
debug?
```

The Python port must inspect existing Python conventions before deciding the exact API spelling.

At minimum, the Python Step 6 implementation must support the debug state required by:

```text
Logger.raw(...)
```

so that raw provider responses are logged only when debug mode is enabled.

Do not add unrelated command-line behavior during this step.

---

# 19. Step 4 — Port `example.py`

Target:

```text
week1_baseline/python/06_the_logger/examples/example.py
```

Source:

```text
Ruby Step 5 example.rb
→
Ruby Step 6 example.rb
```

Preserve the Step 5 Agent example behavior unless the Ruby Step 6 delta changes it.

Expected Step 6 integration:

```python
logger = Logger()

agent = Agent(
    context=context,
    registry=registry,
    builder=builder,
    client=client,
    logger=logger,
    task_settings=player_settings,
)
```

The example should continue to exercise a real Agent tool-use cycle.

It should produce a JSONL session file under the configured session directory.

---

# 20. Step 5 — OpenAI Backend Delta

Target:

```text
week1_baseline/python/06_the_logger/boukensha/backends/openai.py
```

Only port the verified Ruby Step 5 → Step 6 OpenAI delta.

Do not redesign the OpenAI backend.

The Ruby comparison showed changes related to existing model/payload metadata rather than broad logger-specific provider behavior.

Before editing Python:

```text
Compare Ruby 05 OpenAI
against Ruby 06 OpenAI
and map the exact delta.
```

No change should be made to:

```text
Anthropic
Gemini
Ollama
Ollama Cloud
```

unless a later verified mismatch requires it.

---

# 21. Files Not Planned for Modification

Unless a Ruby delta is proven during implementation, do not modify:

```text
boukensha/backends/anthropic.py
boukensha/backends/gemini.py
boukensha/backends/ollama.py
boukensha/backends/ollama_cloud.py
boukensha/client.py
boukensha/context.py
boukensha/message.py
boukensha/registry.py
boukensha/tool.py
boukensha/tasks/player.py
```

Any need to modify these files must trigger a review before proceeding.

---

# 22. Step 6 — Runner

Create:

```text
week1_baseline/bin/python/06_the_logger
```

Start from:

```text
week1_baseline/bin/python/05_agent_loop
```

Change only the iteration directory unless Step 6 requires additional runner behavior.

Target iteration:

```text
week1_baseline/python/06_the_logger
```

Runner requirements:

- repository-relative path resolution
- shared Python virtual environment
- executable mode
- works from repository root
- works from `/tmp`

Verification:

```bash
bash -n week1_baseline/bin/python/06_the_logger

stat -c '%A %a %n' \
  week1_baseline/bin/python/06_the_logger
```

Git mode must ultimately be:

```text
100755
```

---

# 23. Step 7 — Execute

Before the live run:

```bash
python -m compileall -q \
  week1_baseline/python/06_the_logger
```

Then remove generated caches.

Run:

```bash
./week1_baseline/bin/python/06_the_logger
```

Expected Agent behavior:

```text
iteration 1
model response
tool call
tool result
iteration 2
final response
```

Expected Logger behavior:

```text
one JSONL session file created
```

under the configured session directory.

---

# 24. Verify the JSONL Session

The JSONL session is a required Step 6 artifact.

Do **not** delete it after successful execution.

Inspect:

```bash
find .boukensha/sessions \
  -maxdepth 1 \
  -type f \
  -name '*.jsonl' \
  -print
```

Then inspect the generated log:

```bash
cat .boukensha/sessions/<session-id>.jsonl
```

Optionally use:

```bash
jq . .boukensha/sessions/<session-id>.jsonl
```

if `jq` handles the JSONL stream as expected.

Verify the session includes appropriate phases such as:

```text
session_start
iteration
prompt
response
tool_call
tool_result
turn_end
```

A raw phase should appear only when debug logging was intentionally enabled.

---

# 25. Verify JSONL Integrity

Every non-empty line must parse independently as JSON.

Example:

```bash
python - <<'PY'
import json
from pathlib import Path

path = Path(".boukensha/sessions/<session-id>.jsonl")

count = 0

for line_number, line in enumerate(
    path.read_text(encoding="utf-8").splitlines(),
    start=1,
):
    if not line.strip():
        continue

    json.loads(line)
    count += 1

print(f"Valid JSONL records: {count}")
PY
```

No parse failures should occur.

---

# 26. Verify Session Identity

Every event should carry the same:

```text
session_id
```

and each event should contain:

```text
at
phase
```

No event should silently switch session IDs.

---

# 27. Verify Token and Cost Metadata

For responses where the provider supplies usage information, verify that response log records contain normalized values when available:

```text
input_tokens
output_tokens
```

and:

```text
cost_usd
```

when the backend supports cost estimation.

Do not require cost fields from providers that do not expose the information necessary for estimation.

---

# 28. Debug Verification

Run a controlled debug-mode execution.

Verify:

```text
raw
```

events appear when debug mode is enabled.

Then run without debug mode and verify raw provider responses are not included.

Take care not to expose credentials in JSONL logs.

---

# 29. Credential Safety

The Logger must not write secrets such as:

```text
Authorization headers
API keys
environment secrets
```

into JSONL output.

Before committing generated logs, inspect them:

```bash
grep -RniE \
  'authorization|api[_-]?key|bearer|secret' \
  .boukensha/sessions
```

Review any match manually.

Do not assume every textual match is a secret, but do not commit credentials.

---

# 30. Portability Verification

After a successful repository-root execution:

```bash
cd /tmp
```

Run the Step 6 runner by absolute path.

It must still:

- locate the Python environment
- locate `.boukensha`
- run the Agent
- generate the correct JSONL session

Then return to the repository root.

---

# 31. Log Visualizer

The instructor repository contains a Ruby visualizer at:

```text
week1_baseline/ruby/log_viz
```

This visualizer is a consumer of the JSONL logs.

It is not required to implement the Python Logger itself.

Do not port the visualizer as part of the core Python Step 6 implementation unless the bootcamp explicitly requires a Python version.

The existing visualizer may be used later to inspect compatible JSONL session logs.

---

# 32. Git Hygiene

Before staging:

```bash
git diff --check
```

Remove:

```text
__pycache__
*.pyc
*.pyo
Zone.Identifier
```

Do not remove the required Step 6 JSONL validation session.

Review:

```bash
git status --short
```

Stage only the Step 6 Python implementation, port plan, runner, and required validation logs.

Do not use:

```bash
git add .
```

---

# 33. Expected Python Step 5 → Step 6 Delta

Expected meaningful differences:

```text
NEW
boukensha/logger.py

CHANGED
boukensha/agent.py
boukensha/__init__.py
examples/example.py
boukensha/backends/openai.py   # only verified Ruby delta

NEW
week1_baseline/bin/python/06_the_logger

NEW / GENERATED
required JSONL session log(s)
```

Any additional changed Python source file requires review before staging.

---

# 34. Verification Gate

Before committing, all of the following must pass:

```text
[ ] Python Step 6 compiles.
[ ] logger.py behavior matches Ruby logger.rb.
[ ] Agent Loop still completes normally.
[ ] Tool calls still execute.
[ ] Tool failures are logged and handled according to Ruby behavior.
[ ] A JSONL session file is generated.
[ ] Every JSONL line parses independently.
[ ] Session IDs are consistent.
[ ] Required phases are present.
[ ] Token usage is normalized when available.
[ ] Cost estimation is recorded when supported.
[ ] Raw responses appear only in debug mode.
[ ] No credentials are present in logs.
[ ] Runner works from repository root.
[ ] Runner works from /tmp.
[ ] No caches or Zone.Identifier files are staged.
[ ] Required JSONL validation logs are retained.
[ ] Only expected Step 6 files are staged.
[ ] Runner mode is 100755.
```

---

# 35. Implementation Approval Gate

Python implementation may begin only when this document has been reviewed and accepted.

Approved implementation order:

```text
1. logger.py
2. agent.py
3. __init__.py
4. example.py
5. openai.py — verified delta only
6. runner
7. execute
8. verify
```

Each stage must stop for review before advancing.

---

# 36. Final Acceptance Criteria

Step 6 is complete when:

1. The Python Logger writes one structured JSONL file per Agent session.
2. The Agent records the same execution phases as the Ruby Step 6 implementation.
3. Logging does not change the Step 5 Agent's functional behavior.
4. Tool calls and results remain correctly represented in Context.
5. Provider responses include normalized observability metadata when available.
6. Raw provider responses are debug-only.
7. Logs contain no credentials.
8. The runner works independent of the caller's current directory.
9. The generated validation JSONL file is retained for instructor review.
10. The completed Step 6 implementation is reviewed, committed, and pushed.

---

# 37. Guiding Principle

The Step 6 port must preserve one central architectural property:

> Logging observes Agent execution; it does not control Agent execution.

The Ruby Step 5 → Step 6 delta defines the Python scope.

Do not use Step 6 as an opportunity for unrelated refactoring.