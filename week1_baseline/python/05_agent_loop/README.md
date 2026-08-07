# Boukensha Step 4: API Client

This snapshot ports the Ruby Step 4 API Client on top of the Python Step 3
PromptBuilder. `Context` owns messages and tools, `Registry` owns tool creation
and explicit dispatch, provider backends serialize provider-specific requests,
`PromptBuilder` delegates that serialization, and `Client` performs one JSON
HTTP request and returns the raw parsed response. Client never interprets or
dispatches returned tool calls.

The snapshot supports Anthropic, Gemini, Ollama, Ollama Cloud, and OpenAI.
OpenAI uses `https://api.openai.com/v1/chat/completions`, supports
`gpt-5.6-luna`, function tools, `max_completion_tokens`, and
`reasoning_effort: "none"`. Tool results use `role: "tool"`,
`tool_call_id`, and `content`.

## HTTP contract

Client uses Python’s standard-library `urllib.request`, `urllib.error`,
`ssl`, and `json`. HTTPS uses the default certificate-verifying SSL context;
SSL verification is never disabled. Every attempt has a 30-second timeout.

There are three total attempts, including the initial request. Only HTTP 408,
409, 429, 500, 502, 503, and 504, transient connection/timeout failures, and
transient SSL/socket failures are retryable. Permanent 400/401/403/404,
malformed requests, unsupported models, invalid credentials, and other
permanent 4xx responses are not retried. `Retry-After` is honored when usable,
with every wait capped at five seconds. Otherwise backoff is 0.5 then 1.0
seconds.

Non-success responses raise `ApiError` with status, attempt, and a bounded
safe body detail. Malformed successful JSON also raises `ApiError`, chained
from the original JSON exception. Errors and example headers redact
credentials, Authorization values, `.env` contents, and credential-bearing
headers.

Assistant response content may be `null` when tool calls are present and the
finish reason is `tool_calls`. Outbound system and ordinary user message
content is converted to strings and is never serialized as required `null`.

## Configuration and running

The example resolves the repository-root `.boukensha` directory from its own
file path and selects `tasks.player.provider` and `tasks.player.model` from
`.boukensha/settings.yaml`. It registers `read_file` and `list_directory`, adds
the user message asking what files are in the current directory, constructs the
backend, PromptBuilder, and Client, then sends one request. It prints the
heading, Config, provider, model, URL, redacted headers, and raw parsed
response. Returned tools are not executed.

Use the shared environment at `week1_baseline/python/.venv`:

```bash
week1_baseline/python/.venv/bin/python -m pip install -r week1_baseline/python/04_api_client/requirements.txt
./week1_baseline/bin/python/04_api_client
```

The executable runner uses the shared environment by absolute repository path
and does not depend on the current directory:

```bash
(cd /tmp && /mnt/d/Tech/AI/Claude\ BC/claude-code-camp-2026-Q2/week1_baseline/bin/python/04_api_client)
```

No `.boukensha`, `.env`, secrets, virtual environments, `__pycache__`, or
`.pyc` files belong in this snapshot.
