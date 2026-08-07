# Python Week 1 Step 5 — Agent Loop Port Plan

## Goal

Port only the behavior introduced between:

- `week1_baseline/ruby/04_api_client`
- `week1_baseline/ruby/05_agent_loop`

into the copied Python Step 5 iteration:

- `week1_baseline/python/05_agent_loop`

Python Step 5 begins as a copy of the completed Python Step 4 API Client.

Preserve the completed Step 4 architecture, naming conventions, provider
interfaces, standard-library HTTP implementation, configuration behavior,
retry behavior, and existing serializers unless the Ruby Step 4 → Step 5
delta explicitly requires a change.

Do not redesign or reimplement the complete project.

The Ruby Step 5 implementation is the behavioral source of truth.

The completed result should provide a bounded agent loop in which:

1. the configured provider receives the conversation and available tools;
2. provider responses are normalized into one provider-independent shape;
3. tool calls are dispatched through `Registry`;
4. assistant tool-call messages and tool results are appended to `Context`
   in the correct order;
5. the updated conversation is sent back to the model;
6. the loop continues until final assistant text is returned or the
   configured iteration limit is reached;
7. reaching the iteration limit triggers one final tools-disabled wrap-up
   request rather than another normal work iteration.

---

# Ruby Step 4 → Step 5 Porting Rule

Implement only the changes introduced by Ruby Step 5.

The Python Step 5 directory is already based on the completed Python
Step 4 API Client, so existing working Step 4 functionality should be
preserved.

Expected Step 5 changes center on:

- new `boukensha/agent.py`;
- task settings for iteration/output limits;
- response parsing delegation;
- Client support for payload options required by Agent;
- normalized provider responses;
- provider-specific replay of assistant tool calls where required;
- public export of `Agent`;
- conversion of the example from a one-shot request into an Agent Loop;
- creation of the Python Step 5 runner;
- verification and portability checks.

Implementation must proceed in this exact order:

1. `agent.py`
2. `tasks/base.py`
3. `prompt_builder.py`
4. `client.py`
5. provider backends
6. `__init__.py`
7. `example.py`
8. runner
9. verification

---

# 1. `boukensha/agent.py` — New

## Ruby source

`week1_baseline/ruby/05_agent_loop/lib/boukensha/agent.rb`

## Python target

`week1_baseline/python/05_agent_loop/boukensha/agent.py`

## Purpose

Add the Agent orchestration layer introduced by Ruby Step 5.

The Agent coordinates:

- `Context`
- `Registry`
- `PromptBuilder`
- `Client`
- task settings
- iteration limits
- output-token limits

The Agent must not perform provider-specific parsing and must not make HTTP
requests directly.

Those responsibilities remain in the backend/PromptBuilder and Client layers.

## Constructor contract

Implement the Python equivalent of the Ruby Agent constructor.

Recommended Python interface:

```python
Agent(
    context,
    registry,
    builder,
    client,
    task_settings=None,
    max_iterations=None,
    max_output_tokens=None,
)