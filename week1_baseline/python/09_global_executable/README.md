# Boukensha Step 9: Global Executable

This snapshot ports the Ruby Step 9 Global Executable milestone to Python on top of the Step 8 REPL Loop.

Step 8 introduced the persistent interactive REPL:

```text
REPL
    ↓
user input
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
assistant response
    ↓
next user input
```

Step 9 makes that REPL available as an installable global command.

After installing the package, Boukensha can be launched with:

```bash
boukensha
```

instead of requiring execution from inside the project source tree.

The installed command resolves to:

```text
boukensha
    ↓
boukensha.cli:main
    ↓
repl()
```

## Package Installation

Step 9 introduces `pyproject.toml` and packages Boukensha using setuptools.

The package defines the console-script entry point:

```text
boukensha = boukensha.cli:main
```

and requires Python 3.10 or newer.

Runtime dependencies include:

```text
PyYAML
python-dotenv
```

## Configuration

The global executable must work independently of the current working directory.

Boukensha resolves its configuration directory using:

```text
BOUKENSHA_DIR
    ↓
explicit configuration directory, when provided

otherwise

~/.boukensha
```

The runtime settings file is:

```text
settings.yaml
```

A task configuration can select a provider and model:

```yaml
tasks:
  player:
    provider: openai
    model: gpt-5.4-mini
```

Provider credentials are supplied through environment variables such as:

```text
OPENAI_API_KEY
```

Credentials should not be stored in `settings.yaml`.

## Packaged System Prompt

Because Step 9 must run after installation and outside the repository source tree, the system prompt is owned by the installed `boukensha` package:

```text
boukensha/
└── prompts/
    └── system.md
```

The package metadata includes:

```text
prompts/system.md
```

as Boukensha package data.

This allows the installed runtime to load the system prompt regardless of the caller's current working directory.

## REPL Commands

The Step 8 REPL behavior remains available through the global executable.

Supported commands include:

```text
/clear
/quiet
/loud
/quit
/exit
```

`/clear` resets the current conversation history.

`/quiet` suppresses iteration logging while leaving normal assistant responses enabled.

`/loud` restores iteration logging.

`/quit` and `/exit` terminate the REPL cleanly.

## Tools and Configuration

The bare global executable starts the generic REPL without automatically registering application-specific tools.

Tools can be supplied through the existing configuration callback mechanism:

```text
repl(configure=configure_tools)
```

The Step 9 example demonstrates this by registering tools such as:

```text
read_file
list_directory
```

This preserves the separation between:

```text
global Boukensha executable
        ↓
generic REPL

and

configured application
        ↓
REPL + user-supplied tools
```

## Step 9 Runtime Flow

The installed execution path is:

```text
boukensha
    ↓
console-script entry point
    ↓
boukensha.cli:main
    ↓
configuration resolution
    ↓
packaged system prompt
    ↓
REPL
    ↓
Agent
    ↓
configured provider
    ↓
assistant response
```

When tools are supplied through a configuration callback, the Agent loop additionally supports:

```text
user request
    ↓
model tool call
    ↓
registered Python tool
    ↓
tool result
    ↓
Agent continuation
    ↓
final assistant response
```

Step 9 therefore changes how Boukensha is packaged and launched while preserving the Agent, tool, context, and REPL architecture developed in the earlier steps.
