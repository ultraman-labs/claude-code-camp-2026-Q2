# Python Week 1 Step 4: API Client implementation plan

## Objective and boundaries

Port Ruby `week1_baseline/ruby/04_api_client` to a new, independently
runnable Python snapshot at `week1_baseline/python/04_api_client`, starting by
copying `week1_baseline/python/03_prompt_builder`. Ruby Step 4 is the behavioral
source of truth; the Python Step 3 snapshot is the structural starting point.
This plan describes implementation only. No Python code, Ruby file, runner, or
commit/push is part of this planning task.

The result is one HTTP POST and one parsed JSON response. It must not add an
agent loop, tool-call interpretation, tool dispatch, streaming, or automatic
execution of returned tools. Existing Step 3 behavior remains unchanged unless
the narrowly identified Step 4 delta below requires it.

## Architecture and responsibility contract

The implementation must preserve these boundaries:

- `Context` owns conversation state (`system`, ordered `messages`) and the
  registered `tools` mapping.
- `Registry` creates tools and dispatches them when explicitly asked. Step 4
  only registers `read_file` and `list_directory`; `Client` never dispatches
  either one.
- Provider backends own provider-specific message serialization, tool schema,
  headers, URL, and payload formatting.
- `PromptBuilder` receives the context and selected backend and delegates
  payload, headers, and URL construction. It remains network-free.
- `Client` receives a `PromptBuilder`, obtains its URL, headers, and payload,
  sends exactly one JSON HTTP request (subject to documented Ruby-compatible
  retries), parses the JSON body, and returns the raw parsed object. It does not
  inspect finish reasons, content, or tool calls.

The Ruby-to-Python translation should retain Python’s existing Step 3
`to_messages(context)` normalization rather than reproducing Ruby’s
inconsistent backend method signatures. `Client` should call
`builder.to_api_payload(max_output_tokens=...)`, `builder.headers()`, and
`builder.url()` only.

## Ruby Step 3-to-Step 4 delta

Compare the actual Ruby Step 3 snapshot with Ruby Step 4 before coding. The
intended Step 4 delta is additive and narrow:

- add `boukensha/client.py`, using `urllib.request`/`urllib.error` (or the
  equivalent standard-library HTTP API) and `json`, `ssl`, and timeout-aware
  transport;
- add `ApiError` alongside the existing `UnknownToolError` and
  `UnsupportedModelError`;
- add the Step 4 task/config/backend metadata changes only where the Ruby
  snapshot differs from Python Step 3, preserving all supported providers and
  model tables;
- add OpenAI `reasoning_effort: "none"` to the payload while retaining
  `gpt-5.6-luna`, the exact Chat Completions URL, function tools,
  `max_completion_tokens`, and tool-result messages;
- replace the no-network Step 3 example with the one-request Step 4 example;
- update exports, README, and add the Step 4 launcher.

Do not rewrite working serializers or introduce a third-party HTTP client
unless comparison proves the existing architecture cannot express the Ruby
behavior. If a Ruby Step 4 change conflicts with a verified Python Step 3
contract, record it in the approval section before implementation.

## File-by-file implementation map

Create `week1_baseline/python/04_api_client/` by copying the complete Step 3
tree. The copied files are:

- `boukensha/config.py`, `context.py`, `errors.py`, `message.py`,
  `registry.py`, `tool.py`, `prompt_builder.py`;
- `boukensha/tasks/__init__.py`, `tasks/base.py`, `tasks/player.py`;
- `boukensha/backends/__init__.py`, `backends/base.py`, and all five backend
  modules: `anthropic.py`, `gemini.py`, `ollama.py`, `ollama_cloud.py`,
  `openai.py`;
- `requirements.txt` (retain the Step 3 dependency set), `prompts/system.md`,
  and `examples/example.py` as the starting snapshot.

New files:

- `boukensha/client.py`: `Client`, retry policy, explicit timeout, TLS
  verification, JSON request/response handling, and secret-safe `ApiError`
  messages.
- `README.md`: Step 4 architecture, environment, configuration path, retry
  semantics, safety rules, commands, and verification results/expectations.
- `week1_baseline/bin/python/04_api_client`: executable location-independent
  launcher.

Modified copied files:

- `boukensha/errors.py`: add `ApiError` while retaining existing exceptions.
- `boukensha/__init__.py`: export `Client` and `ApiError` so both are
  importable from `boukensha`.
- `backends/openai.py`: retain all Step 3 OpenAI behavior and add
  `reasoning_effort: "none"` for `gpt-5.6-luna` compatibility (if the Ruby
  comparison shows this is model-specific, guard it by model; otherwise
  preserve the Ruby payload exactly).
- Any copied config/task/backend files whose Ruby Step 4 delta requires a
  narrowly scoped update, with the README identifying each such change.
- `examples/example.py`: port the Ruby Step 4 setup and output.

Unchanged files after comparison: all copied Step 3 modules and fixtures that
already match Ruby Step 4, including Context/Registry ownership and all
provider serializers. The original Step 3 directory and runner remain
untouched. Do not copy `.boukensha/.env`, any virtual environment, caches, or
other repository configuration into the snapshot.

## Client and HTTP behavior

Implement `Client(builder)` and `call(max_output_tokens=1024)`. Serialize the
builder payload with `json.dumps`, send UTF-8 JSON via standard-library HTTPS
transport, and parse the response with `json.loads`. Use certificate-verifying
default TLS context; never use an unverified context or disable SSL checks.
Local Ollama HTTP URLs may remain plain HTTP exactly as the provider backend
defines them.

Use an explicit 30-second per-attempt HTTP timeout; never use an unbounded
socket timeout. The retry budget is three total attempts, including the
initial request. Retry only HTTP `408`, `409`, `429`, `500`, `502`, `503`, and
`504`, plus transient connection failures, timeout failures, and transient
SSL/socket failures that can reasonably succeed on another attempt. Do not
retry HTTP `400`, `401`, `403`, or `404`, malformed requests, unsupported
models, invalid credentials, or other clearly permanent 4xx responses.

Preserve useful provider `Retry-After` behavior when that header is present,
but cap every wait (including exponential backoff) at a documented finite
bound so tests and examples cannot hang indefinitely. With no usable
`Retry-After`, use the Ruby-compatible backoff values for the next attempts
(`0.5` then `1.0` seconds); never schedule an attempt beyond the three-attempt
budget.

For non-success HTTP responses, raise `ApiError` containing status, attempt
count, and useful bounded response details, plus safe exception information
where applicable. Redact authorization headers, API-key values, `.env`
contents, and any known secret strings. Never include full request headers or
credential values in the exception. If a successful response body is not
valid JSON, wrap the original JSON decoding exception in `ApiError` using
exception chaining (`raise ... from exc`) and include only a bounded,
secret-safe body excerpt.

## Configuration, paths, and runner

The example must set `BOUKENSHA_DIR` only when absent, to the resolved
repository-root `.boukensha` directory. Derive it from `__file__` (the Step 4
example is four directory levels below the repository root), not from the
caller’s current directory. `Config` then selects `tasks.player.provider` and
`tasks.player.model` from repository-root `.boukensha/settings.yaml`; the
repository-root `.boukensha/.env` remains ignored and is never copied.

The launcher must resolve its own directory, compute the absolute Step 4
implementation path, `cd` there, and invoke the example through the shared
environment at `week1_baseline/python/.venv`. Prefer the venv interpreter by
absolute path, `${REPO_ROOT}/week1_baseline/python/.venv/bin/python`, and fail
with a clear setup message if it is absent. This makes both commands
independent of the caller’s directory:

```bash
./week1_baseline/bin/python/04_api_client
(cd /tmp && /mnt/d/Tech/AI/Claude\ BC/claude-code-camp-2026-Q2/week1_baseline/bin/python/04_api_client)
```

Do not create or activate a new environment, modify runners from earlier
steps, or add dependencies beyond the existing Step 3 requirements without
approval.

## Example behavior and output contract

Port the Ruby example in this order:

1. resolve repository-root config;
2. construct `Config`, retrieve Player settings and system prompt;
3. create `Context` and `Registry`;
4. register `read_file(path)` and `list_directory(path)` with the Ruby
   descriptions and schemas;
5. add the user message `What files are in the current directory?`;
6. select the configured provider/model and instantiate Anthropic, Gemini,
   Ollama, Ollama Cloud, or OpenAI with the appropriate environment key;
7. construct `PromptBuilder`, then `Client`;
8. call the client exactly once and print the raw parsed response.

Print the Step 4 heading, Config, Provider, Model, destination URL, and raw
parsed response. Print headers only if useful for diagnostics, and then only
with the Authorization value replaced by a fixed redaction marker. Never
print, log, embed, or assert the real API key. Do not execute returned tool
calls. A successful OpenAI response is valid when it has assistant content, or
when `content` is legally `null` because `tool_calls` are present and
`finish_reason` is `"tool_calls"`.

When building outbound messages, system and ordinary user message content
must be strings. Preserve the configured system prompt and user prompt as
text, and do not serialize required system/user content as `null`. This does
not prohibit provider-defined nullable assistant content in a tool-call
response, which is response data and is not an outbound prompt message.

## Ruby-to-Python decisions and approval ambiguities

- Use `urllib` and the default verified `ssl` context because Ruby Step 4
  intentionally uses standard-library `net/http`; no requests/httpx layer is
  needed.
- Use Python `Path`/`__file__` resolution for stable repository paths rather
  than `cwd`, while preserving the existing `BOUKENSHA_DIR` override.
- Keep raw JSON as Python dictionaries/lists; do not normalize provider
  response shapes or dispatch tools.
- Use explicit redaction in example output and error formatting, even though
  Ruby’s sample prints a raw response, because the Python port must satisfy
  the no-secret contract.
- Map only transient connection, timeout, TLS, socket, and EOF-like failures
  that can reasonably succeed on another attempt; never catch broad
  `Exception`. The fixed retry budget is three total attempts, and
  `Retry-After` waits must be bounded.
- Malformed successful-response JSON is always surfaced as `ApiError` with the
  original JSON exception as its cause. The fixed per-attempt timeout is 30
  seconds.

## Proposed implementation order

1. Copy Step 3 into the new snapshot; verify Step 3 and its runner are
   unchanged and no `.env`/virtual-environment files were copied.
2. Compare Ruby Step 4 files and apply only the documented config/task/backend
   delta.
3. Add `ApiError` and `Client`; implement safe errors, timeout, TLS, JSON,
   retry statuses, transient failures, and no retry for 400.
4. Add OpenAI Luna reasoning effort and verify all provider exports/support.
5. Update package exports.
6. Port the example and add the absolute-path shared-venv runner.
7. Write the README and perform the focused checks below.

## Focused smoke checks

Run these against the later implementation, without making a real request
unless credentials and explicit external testing are authorized:

- compile every Step 4 `.py` file with `py_compile` and run `git diff --check`;
- import `boukensha`, assert `boukensha.Client` and
  `boukensha.ApiError`, and verify each backend is selectable;
- build the OpenAI Luna payload and assert the exact URL, model,
  `reasoning_effort == "none"`, `max_completion_tokens`, function-tool shape,
  and `role/tool_call_id/content` tool-result shape;
- assert displayed headers and errors redact Authorization/API-key values;
- stub the transport to assert `ApiError` for a 400 and exactly one attempt;
- stub retryable status/transient failures and assert the Ruby retry set and
  bounded attempt count;
- run the root runner and the absolute runner from `/tmp` using the shared
  venv (use a local stub or inspect-only mode if no API key is available);
- inspect and remove only generated `__pycache__`, `.pyc`, and other cache
  output after checks; assert no `.env`, secrets, or `.boukensha` files are in
  the snapshot or staged diff;
- verify provider selection comes from repository-root settings, not
  `week1_baseline/.boukensha`;
- verify `git diff --check` and a focused `git status --short` review.

## Final staging checklist

Before handing off, stage only these paths (do not stage during planning):

```text
docs/plans/python_port/04_api_client.md
week1_baseline/python/04_api_client
week1_baseline/bin/python/04_api_client
```

Explicitly exclude `docs/journal/1_baseline.md`, `.agents/`, `repo-errors.txt`,
`repo-search.json`, `test.json`, `week0_explore/`, `.boukensha/`, all `.env`
files, virtual environments, `__pycache__`, and all `.pyc` files. Do not stage
unrelated pre-existing worktree changes. Nothing may be committed or pushed
as part of this work.

## Approval gate

No implementation begins until this plan has been reviewed and explicitly
approved.
