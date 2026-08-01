# 03 · Prompt Builder (Python)

This is the Python Week 1 Step 3 port of the verified Ruby Prompt Builder.
It constructs provider-specific request dictionaries and never performs an
HTTP, completion, or streaming request.

`PromptBuilder` receives a `Context` and an already-created backend. Every
backend implements the same contract: `to_messages(context)`, `to_tools(tools)`,
`to_payload(context, max_output_tokens=1024)`, `headers()`, and `url()`.
Provider selection remains in `examples/example.py`.

The five backends preserve Ruby’s model tables, validation, metadata, costs,
message/tool conversions, payloads, headers, and URLs. The Python interface
normalizes the Ruby signature inconsistency by passing the whole Context to
`to_messages`. OpenAI supports `gpt-5.6-luna` with a 1,050,000-token context
window and input/output prices of 1.0/6.0 per million tokens.

## Setup

All Week 1 Python iterations use the shared environment:

```sh
python3 -m venv week1_baseline/python/.venv
source week1_baseline/python/.venv/bin/activate
python -m pip install -r week1_baseline/python/03_prompt_builder/requirements.txt
```

No `pyproject.toml`, framework, HTTP client, or formal test suite is used.
API keys, when required to construct runtime headers, come from environment or
configuration. Example output redacts them.

## Run

From the repository root:

```sh
./week1_baseline/bin/python/03_prompt_builder
```

From `/tmp`:

```sh
cd /tmp
/mnt/d/Tech/AI/Claude\ BC/claude-code-camp-2026-Q2/week1_baseline/bin/python/03_prompt_builder
```

The launcher resolves the Step 3 directory independently of the current
directory. The example defaults `BOUKENSHA_DIR` to the repository-root
`.boukensha` and prints only a redacted header view plus the constructed JSON
payload.
