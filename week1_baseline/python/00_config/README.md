# 00 · Configuration (Python)

This is the Python Step 0 implementation of the configuration slice originally
defined in `week1_baseline/ruby/00_config`. It loads configuration from an
external `.boukensha` directory and provides the stateless `Player` task API.
Later agent-loop iterations, per-turn limits, LLM calls, and MUD interaction
are out of scope for this step.

## Shared virtual environment

One shared virtual environment is used for all Week 1 Python iterations. From
the repository root, create and activate it, then install the dependencies:

```bash
python3 -m venv week1_baseline/python/.venv
source week1_baseline/python/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r week1_baseline/python/00_config/requirements.txt
```

The launcher assumes this virtual environment has already been activated. It
does not create or activate the environment itself; it only uses the active
environment's `python` command.

The requirements file can also be installed separately with:

```bash
python -m pip install -r week1_baseline/python/00_config/requirements.txt
```

The requirements are:

- `PyYAML` for `settings.yaml`
- `python-dotenv` for `.env`

## Configuration directory

`BOUKENSHA_DIR` selects the configuration directory. If it is unset, the
implementation uses `~/.boukensha`.

```bash
export BOUKENSHA_DIR="$PWD/week1_baseline/.boukensha"
```

The directory may contain:

```text
.boukensha/
  .env                 # credentials and other environment values
  settings.yaml        # non-secret settings
  prompts/
    player/
      system.md        # optional task-specific system prompt override
```

`.env` is loaded before `settings.yaml` and does not overwrite environment
variables that are already set. Do not commit credentials.

## Settings schema

The current schema is organized by task:

```yaml
tasks:
  player:
    provider: OpenAI
    model: gpt-5.6-luna
    prompt_override:
      system: true
mud:
  host: localhost
  port: 4000
  username: UltraMan
  password: secret
```

`Config` supplies `localhost` and `4000` when the MUD host or port is absent.
When `tasks.player.prompt_override.system` is `true` and the user prompt file
exists, `prompts/player/system.md` overrides the packaged
`prompts/system.md`. Otherwise the packaged prompt is used.

## Running Step 0

Directly from the implementation directory:

```bash
cd week1_baseline/python/00_config
python examples/example.py
```

Or from the repository root through the launcher:

```bash
./week1_baseline/bin/python/00_config
```

The example prints the resolved directory, task provider/model, prompt status,
MUD host/user, and whether `OPENAI_API_KEY` is set. It does not print secret
values.
