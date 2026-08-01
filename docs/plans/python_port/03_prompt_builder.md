# Python Week 1 Step 3: Prompt Builder implementation plan

## Objective and boundaries

Port the verified Ruby `week1_baseline/ruby/03_prompt_builder` iteration to
Python while preserving its data model and provider-specific serialization.
The implementation constructs request data only; it must not perform an HTTP
request, completion, or streaming operation. The active example configuration
is provider `openai`, model `gpt-5.6-luna`, with the default configuration
directory at the repository-root `.boukensha`.

Use the Step 2 Python snapshot as the starting point. Keep the shared
`week1_baseline/python/.venv` and `requirements.txt` workflow. Do not add
`pyproject.toml`, frameworks, an HTTP client, or a formal test suite.

## Files to create or copy

First copy the complete Step 2 tree to
`week1_baseline/python/03_prompt_builder`, preserving these existing files:

- `README.md`: Step 3 usage, architecture, configuration, and no-network
  behavior.
- `requirements.txt`: retain the existing `PyYAML` and `python-dotenv`
  dependencies; install/use them through the shared
  `week1_baseline/python/.venv`.
- `prompts/system.md`: retain the prompt fixture.
- `examples/example.py`: extend the Step 2 example with provider selection,
  backend construction, prompt building, safe metadata/header display, and
  JSON payload output.
- `boukensha/__init__.py`, `config.py`, `context.py`, `errors.py`,
  `message.py`, `registry.py`, `tool.py`, and `tasks/`: preserve their Step 2
  behavior and representations unless the Ruby Step 3 comparison requires a
  narrowly scoped interface addition.

Create these Step 3 files under that copied tree:

- `boukensha/prompt_builder.py`: retain the context and already-created
  backend, delegate payload, message, tool, header, and URL operations, and
  expose cost/metadata access without making network calls.
- `boukensha/backends/__init__.py`: export the common backend base and all five
  provider classes.
- `boukensha/backends/base.py`: implement model-table lookup, exact supported
  model validation/error behavior, metadata access, and Ruby-equivalent cost
  estimation.
- `boukensha/backends/anthropic.py`, `gemini.py`, `ollama.py`,
  `ollama_cloud.py`, and `openai.py`: port each Ruby model table and each
  provider’s message/tool/payload/header/URL rules exactly.

Create or copy `week1_baseline/bin/python/03_prompt_builder` as an executable
repository-independent launcher. It must resolve its own directory, change to
the absolute Step 3 directory, and run `examples/example.py`; it must not
depend on the caller’s current directory.

Do not modify `week1_baseline/python/02_the_registry`, its launcher, unrelated
files, or the Ruby source.

## Chosen backend contract

Choose design A: every backend’s public message conversion accepts the whole
`Context`, `to_messages(context)`. `to_payload(context, max_output_tokens=1024)`
may call that method and the backend’s `to_tools(context.tools)`. This keeps
system prompt ownership with the context and prevents provider callers from
reconstructing a partial context. `PromptBuilder.to_messages()` delegates
`self.backend.to_messages(self.context)` and never passes an incompatible
argument list.

All five backends must implement the same public methods:

`to_messages(context)`, `to_tools(tools)`, `to_payload(context,
max_output_tokens=1024)`, `headers()`, and `url()`.

This intentionally normalizes Ruby’s inconsistent interface: Ruby Anthropic
and Gemini define `to_messages(messages)`, while Ruby OpenAI, Ollama, and
Ollama Cloud define `to_messages(system, messages)`, although Ruby
`PromptBuilder#to_messages` always supplies only `context.messages`. The Ruby
example avoids the defect by using `to_api_payload`. Python must not reproduce
that broken public contract; payload output remains equivalent to the Ruby
payloads.

## Provider behavior to port

Copy every model name and metadata value from the five Ruby `MODELS` tables,
including Ollama Cloud’s `advertised_context_window` and `usage_level` fields.
Validation must accept string-like model names, return the normalized model,
and raise the existing `UnsupportedModelError` with the provider, rejected
model, and sorted supported-model list in the Ruby-equivalent message.

Preserve `context_window`, input/output cost per million, `usage_unit`,
optional usage level, and `estimate_cost`; return `None` when either cost is
unknown, retain zero-cost local Ollama behavior, and use the Ruby million-token
formula. Explicitly verify OpenAI `gpt-5.6-luna`: context window `1_050_000`,
input `1.0`, output `6.0`, unit `tokens`.

Preserve these serialization rules:

- Anthropic: top-level `system`, `max_tokens`, `tools`; ordinary roles and
  tool results as a `user` message containing `tool_result` and
  `tool_use_id`; tools use `input_schema`.
- Gemini: `systemInstruction`, `contents`, `tools`, and `generationConfig`;
  assistant becomes `model`; tool results become a user `functionResponse`;
  tools use `functionDeclarations`.
- Ollama and Ollama Cloud: system message first, `stream: false`, chat URL,
  OpenAI-like function-wrapped tools, and tool results as `role: tool` with
  `tool_name`; Cloud adds the Bearer header.
- OpenAI: payload keys `model`, `messages`, `tools`, and
  `max_completion_tokens`; system is a `role: system` message; user and
  assistant roles are preserved; tool results are `role: tool` with
  `tool_call_id` and `content`; tools use `type: function`, nested function
  name/description/parameters, and JSON-schema object/properties/required.

For all providers, required parameter names must be serialized as strings.
Preserve exact Ruby URLs, content-type headers, provider API-key header names,
and model interpolation. Header inspection/output must redact API-key and
Authorization values; keys come only from environment/configuration, never
source code.

Provider selection belongs in `examples/example.py`, matching Ruby. The
builder receives the already-created backend and does not instantiate one.

## Implementation sequence

1. Copy Step 2 to the Step 3 directory and confirm Step 2 remains unchanged.
2. Add the shared backend base, error export, backend package exports, and
   model metadata tables.
3. Add the five provider serializers, porting one Ruby backend at a time and
   applying the single `to_messages(context)` contract.
4. Add `PromptBuilder` delegation and update package exports without changing
   existing Config, Context, Registry, Message, Tool, tasks, or representations
   unnecessarily.
5. Extend the example with the verified Luna/OpenAI configuration, safe
   headers, payload display, cost/metadata display, and no HTTP imports/calls.
6. Add README instructions using
   `./week1_baseline/bin/python/03_prompt_builder`, including invocation from
   both the repository root and `/tmp`, virtual-environment setup, and the
   no-network guarantee.
7. Add the executable launcher and verify it resolves the repository and
   configuration paths independently of the caller’s directory.

## Smoke verification commands

From the repository root, use the shared environment and run:

```bash
source week1_baseline/python/.venv/bin/activate
python -m pip install -r week1_baseline/python/03_prompt_builder/requirements.txt
./week1_baseline/bin/python/03_prompt_builder
```

From outside the repository, run:

```bash
(cd /tmp && /mnt/d/Tech/AI/Claude\ BC/claude-code-camp-2026-Q2/week1_baseline/bin/python/03_prompt_builder)
```

Use a small inline Python smoke script (with `PYTHONPATH` set to the Step 3
directory) to instantiate each backend with a supported model and fake
placeholder key, construct a Context containing system/user/assistant/tool
result messages and a tool, then inspect `to_messages(context)`,
`to_tools(context.tools)`, `to_payload(context)`, `headers()`, `url()`, and
`estimate_cost`. The script must assert model rejection for an unsupported
model, Luna metadata, all provider-specific shapes, exact URLs and header
names, and absence of network modules/calls. It must print only redacted
headers and never a secret or credential value.

## Final verification checklist

- [ ] Step 2 is byte-for-byte/unmodified where no shared-source correction is
      required; no unrelated files changed.
- [ ] All five exact Ruby model tables, validation, context windows, costs,
      usage units, optional usage levels, and Luna metadata are present.
- [ ] Unsupported-model errors match the documented Ruby behavior.
- [ ] All backends use `to_messages(context)` and the builder delegates the
      entire Context.
- [ ] Provider-specific message and tool shapes match Ruby, including system
      placement, assistant role conversion, tool-result identifiers, and
      string `required` names.
- [ ] Payloads, headers, and URLs are generated without network calls.
- [ ] Header output redacts API keys and Authorization values; no key is in
      source or example output.
- [ ] Cost estimation matches Ruby, including `None` for unknown Cloud costs
      and zero local Ollama cost.
- [ ] The root runner and `/tmp` runner both work, and the default config is
      repository-root `.boukensha`.
- [ ] README documents setup, invocation, architecture, and no-network scope.
- [ ] No `pyproject.toml`, framework, HTTP client, or formal test suite was
      introduced.
- [ ] `git diff --check` passes and `git status --short` shows no staged
      secrets, API-key files, cache files, or generated virtual-environment
      artifacts.
- [ ] Nothing is committed or pushed.
