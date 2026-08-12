# Week 1 Journal — Porting Step 0 from Ruby to Python

**Date:** 2026-07-28

---

# Objective

Complete a faithful Python implementation of the Week 1 Step 0 (`00_config`)
baseline while preserving the architecture and behavior of the existing Ruby
implementation.

The goal was **not** to redesign the system or create a more "Pythonic"
implementation.

The Ruby implementation served as the source of truth.

---

# What I Learned

One of the biggest lessons from this exercise is that **software architecture
is more important than the programming language**.

Although Ruby and Python have different syntax, the important ideas remained
identical:

- configuration loading
- environment variables
- prompt loading
- YAML parsing
- launcher behavior
- repository organization
- separation of secrets from source code

The language changed.

The architecture did not.

---

# What "Porting" Means

Before this exercise I thought a software port was simply translating code from
one language into another.

I now understand that a port means:

> Reimplement the same software in another language while preserving the
> externally visible behavior.

A good port preserves:

- inputs
- outputs
- configuration
- side effects
- directory layout
- user experience

It does **not** necessarily preserve syntax.

---

# Planning Before Coding

Instead of immediately asking Codex CLI to generate Python code, I first asked
it to create a written implementation plan.

That plan was then reviewed and improved before any code was generated.

The workflow became:

```text
Study Ruby
        ↓
Generate implementation plan
        ↓
Review the plan
        ↓
Improve the plan
        ↓
Execute the plan
        ↓
Review generated code
        ↓
Correct deviations
        ↓
Verify behavior
```

This produced a much better implementation than asking the AI to simply
"translate Ruby to Python."

---

# Major Design Decisions

## Configuration

Use plain Python dictionaries.

Do not introduce:

- Pydantic
- configuration frameworks
- validation libraries

This preserves the simplicity of the Ruby implementation.

---

## Environment Variables

Continue using:

```text
BOUKENSHA_DIR
```

to locate the user's configuration.

Load:

```text
.env
```

using:

```text
python-dotenv
```

Do not overwrite environment variables that already exist.

---

## Dependencies

The implementation uses only:

```text
PyYAML
python-dotenv
```

Dependencies are installed using:

```text
requirements.txt
```

No:

- pyproject.toml
- Poetry
- Pipenv
- Hatch

were introduced.

---

## Virtual Environment

Use one shared virtual environment for all Week 1 Python iterations.

Location:

```text
week1_baseline/python/.venv
```

Creation:

```bash
python3 -m venv week1_baseline/python/.venv
```

Activation:

```bash
source week1_baseline/python/.venv/bin/activate
```

Dependency installation:

```bash
python -m pip install --upgrade pip
python -m pip install -r week1_baseline/python/00_config/requirements.txt
```

The launcher assumes the environment is already active.

It never creates or activates the virtual environment itself.

---

# Launcher Lessons

Both Ruby and Python launchers were designed to work from any current working
directory.

This required each launcher to determine its own location before launching the
example.

A launcher should **never** assume the user is standing inside the project
directory.

The Ruby launcher initially contained an incorrect relative path.

The bug was found by launching it from:

```text
/tmp
```

The corrected launcher now computes the proper path before execution.

The Python launcher was verified from both:

- repository root
- /tmp

---

# YAML Improvements

The Python implementation now correctly handles:

- missing settings.yaml
- empty settings.yaml
- YAML null documents

All return an empty dictionary.

Additionally:

If the YAML root is not a mapping, the implementation raises a clear
ValueError describing:

- the file
- the unexpected root type

This prevents subtle configuration bugs later.

---

# README Improvements

The README now documents:

- shared virtual environment
- dependency installation
- requirements.txt
- BOUKENSHA_DIR
- .env
- settings.yaml
- prompt overrides
- launcher execution
- direct example execution

Earlier revisions omitted several of these items.

---

# Git Hygiene

Updated:

```text
.gitignore
```

to ignore:

- .venv/
- __pycache__/
- *.py[cod]
- .env
- .boukensha/
- vendor/
- .bundle/
- .vscode/

This prevents generated files and secrets from entering the repository.

---

# AI Engineering Workflow

One of the most valuable lessons from this exercise was learning how to use AI
as an engineering partner rather than as an automatic code generator.

Instead of accepting the first generated implementation, the workflow became:

1. Define the specification.
2. Review the generated plan.
3. Improve the plan.
4. Execute the plan.
5. Review generated code.
6. Compare implementation against specification.
7. Correct deviations.
8. Verify with smoke tests.
9. Publish only after review.

This process produced a much higher-quality implementation.

---

# Smoke Testing

Verified:

✓ Ruby launcher from repository root

✓ Ruby launcher from /tmp

✓ Python launcher from repository root

✓ Python launcher from /tmp

✓ Shared virtual environment

✓ requirements.txt installation

✓ README workflow

✓ Prompt loading

✓ YAML validation

✓ OpenAI environment variable loading

✓ Launcher portability

---

# Final Repository State

Completed:

- Ruby Step 0
- Python Step 0
- Shared launcher structure
- Shared Python virtual environment
- Updated documentation
- Updated implementation plan

Removed:

- pyproject.toml
- formal test suite for this step

---

# Personal Reflection

This exercise taught me that successful software engineering is much more than
writing code.

The most important work happened before and after code generation:

- understanding the existing architecture
- writing a clear implementation plan
- reviewing generated code
- comparing it against the specification
- correcting deviations
- verifying behavior

The implementation itself became the final step rather than the first.

This workflow gave me much greater confidence in the final Python port than I
would have had if I had simply accepted the first AI-generated solution.

Going forward, I want to continue treating AI as a capable engineering
assistant whose work is reviewed and verified, rather than as an infallible
code generator.