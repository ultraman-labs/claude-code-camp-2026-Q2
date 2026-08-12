# Agent Loop Architecture (Step 5)

## Purpose

Step 5 introduces the first true **Agent Loop** into Boukensha.

Previous iterations sent a single request to the language model and immediately returned the response.

Step 5 fundamentally changes that architecture.

Instead of stopping after the first response, the system repeatedly:

1. Sends context to the model.
2. Receives a response.
3. Executes requested tools.
4. Appends tool results back into the conversation.
5. Sends the updated conversation back to the model.
6. Continues until the model produces a final answer or the maximum iteration count is reached.

This transforms the application from a simple API client into an iterative reasoning system.

---

# High-Level Architecture

```
                User Request
                      │
                      ▼
                Conversation Context
                      │
                      ▼
                PromptBuilder
                      │
                      ▼
                    Client
                      │
                      ▼
          Provider Backend
(OpenAI / Anthropic / Gemini / Ollama)
                      │
                      ▼
              parse_response()
                      │
                      ▼
            Normalized Content
                      │
                      ▼
                   Agent
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
     Tool Calls              Final Answer
          │
          ▼
      Registry
          │
          ▼
     Execute Tool
          │
          ▼
      Tool Result
          │
          └──────────────► back into Context
```

---

# Why an Agent Exists

The Agent is responsible for coordinating the entire reasoning loop.

The Agent **does not**:

- build prompts
- perform HTTP requests
- know provider-specific APIs

Instead, it coordinates the conversation.

Its responsibilities are:

- request model responses
- detect tool calls
- dispatch tools
- append tool results
- determine when execution is complete
- enforce maximum iteration limits

The Agent is therefore the orchestration layer.

---

# Why PromptBuilder Does Not Execute Tools

PromptBuilder has one responsibility:

Convert Conversation Context into a provider request.

It should never:

- execute tools
- inspect files
- call APIs
- mutate the conversation

Keeping PromptBuilder focused on serialization makes it reusable across every provider.

---

# Why Client Is Provider-Agnostic

The Client is responsible only for transport.

It knows:

- HTTP
- retries
- SSL
- headers
- authentication
- JSON transport

It intentionally does **not** understand:

- OpenAI messages
- Anthropic content blocks
- Gemini parts
- tool semantics

Those responsibilities belong to provider backends.

---

# Why Every Backend Implements parse_response()

Each provider returns responses differently.

OpenAI

- tool_calls
- JSON strings
- finish_reason

Anthropic

- content blocks
- tool_use blocks
- stop_reason

Gemini

- candidates
- parts
- functionCall

Ollama

- tool_calls
- message content

If the Agent had to understand every provider's response format, it would become tightly coupled to every API.

Instead, each backend translates provider-specific responses into a common internal representation.

This normalized representation looks conceptually like:

```python
{
    "stop_reason": "...",
    "content": [
        {
            "type": "text",
            ...
        },
        {
            "type": "tool_use",
            ...
        }
    ]
}
```

The Agent only understands this normalized structure.

---

# Why Replay Assistant Tool Calls

Large language models are stateless.

Each request must include the complete conversation history.

After a tool executes, the next request must include:

Assistant:

"I want to call read_file()."

Tool:

"Here is the file."

Without replaying the assistant tool call, the model loses the reasoning chain that led to the tool execution.

Each provider reconstructs this history differently.

OpenAI

- tool_calls

Gemini

- functionCall parts

Anthropic

- content blocks

Ollama

- tool_calls

The provider backend performs this reconstruction.

---

# Registry

The Registry separates tool discovery from tool execution.

Instead of the Agent containing logic for every tool, the Agent simply asks:

```
Registry.execute(...)
```

The Registry decides:

- which tool exists
- how it should be executed
- how parameters are validated

This allows new tools to be added without modifying the Agent.

---

# Context

Context represents the current conversation state.

It stores:

- system prompt
- user messages
- assistant messages
- tool calls
- tool results

Every iteration appends additional messages to Context.

PromptBuilder serializes Context for the next provider request.

---

# Why Normalize Everything

Normalization creates a provider-independent architecture.

Instead of:

```
if provider == OpenAI
...
elif provider == Anthropic
...
elif provider == Gemini
...
```

the Agent simply consumes normalized messages.

This dramatically reduces complexity.

Adding a new provider only requires implementing a new backend.

The Agent remains unchanged.

---

# Iteration Lifecycle

```
User
 │
 ▼
Context
 │
 ▼
PromptBuilder
 │
 ▼
Client
 │
 ▼
Provider Backend
 │
 ▼
parse_response()
 │
 ▼
Agent
 │
 ├───────────────► Final Answer
 │
 ▼
Tool Calls
 │
 ▼
Registry
 │
 ▼
Execute Tool
 │
 ▼
Tool Result
 │
 ▼
Context
 │
 └───────────────► next iteration
```

---

# Architectural Principles Learned

During the Step 5 Python port several important design principles became apparent.

## Single Responsibility

Each component performs one job.

Agent

Coordinates execution.

PromptBuilder

Serializes Context.

Client

Performs HTTP communication.

Backend

Translates provider-specific formats.

Registry

Executes tools.

---

## Separation of Concerns

Every layer depends only on the layer immediately below it.

No component reaches across architectural boundaries.

---

## Adapter Pattern

Every provider backend is effectively an Adapter.

It translates between:

Provider API

⇅

Normalized Agent representation

---

## Open/Closed Principle

The Agent never changes when a new provider is added.

Instead, a new backend implements the provider interface.

---

## Portability

The runner resolves repository-relative paths.

The implementation successfully executes regardless of the current working directory.

This was verified by running the Step 5 Agent Loop from `/tmp`.

---

# Lessons Learned

The Step 5 Agent Loop demonstrates an important software engineering principle:

> Normalize variation at the system boundary.

Every provider speaks a different protocol.

Rather than spreading provider-specific logic throughout the application, Boukensha isolates those differences inside backend adapters.

Everything above the backend layer operates on a single consistent conversation model.

This architecture minimizes coupling, improves maintainability, and makes the addition of future providers straightforward.

---

# Summary

Step 5 transforms Boukensha from a single-request API client into a provider-independent, iterative Agent Loop capable of:

- maintaining conversation state,
- executing tools,
- replaying reasoning,
- supporting multiple model providers,
- and producing a final response after one or more reasoning iterations.

This architecture becomes the foundation for subsequent iterations involving planning, sub-agents, memory systems, and Model Context Protocol (MCP) integration.