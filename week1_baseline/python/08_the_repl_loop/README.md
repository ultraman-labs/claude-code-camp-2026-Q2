# Boukensha Step 8: The REPL Loop

This snapshot ports the Ruby Step 8 REPL Loop to Python on top of the Step 7
`Boukensha.run` DSL.

Step 7 introduced a high-level one-shot composition root:

```text
run(task=...)
    ↓
Context
    ↓
Registry + tools
    ↓
Backend
    ↓
PromptBuilder
    ↓
Client
    ↓
Logger
    ↓
Agent.run()
    ↓
final response
    ↓
process exits