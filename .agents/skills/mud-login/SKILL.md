---
name: mud-login
description: Use the bundled Python helper to connect to the local tbaMUD server, authenticate as UltraMan, validate login stages, enter the game, run exactly one look command when authorized, report the current room, send quit, and disconnect safely. Use this skill when the user asks Codex to verify the local MUD connection, test the login flow, enter the game, or identify the player's current room.
---

# MUD Login

Use the bundled deterministic Python helper:

```bash
python3 .agents/skills/mud-login/scripts/login.py --stage <stage>
```

Do **not** attempt to control an interactive `nc localhost 4000` session directly. The helper owns the TCP/Telnet session and protocol handling.

## Server

- Host: `localhost`
- Port: `4000`
- Character: `UltraMan`

The password is supplied through the `MUD_PASSWORD` environment variable.

Never display or reveal the password.

## Available stages

### Prompt

```bash
python3 .agents/skills/mud-login/scripts/login.py --stage prompt
```

Connect, wait for the character-name prompt, then disconnect.

### Username

```bash
python3 .agents/skills/mud-login/scripts/login.py --stage username
```

Connect, send `UltraMan`, wait for the password prompt, then disconnect.

### Menu

```bash
python3 .agents/skills/mud-login/scripts/login.py --stage menu
```

Authenticate, send one empty Return if requested, capture the post-authentication menu, send no menu choice, then disconnect.

### Enter

```bash
python3 .agents/skills/mud-login/scripts/login.py --stage enter
```

Authenticate, enter the game using verified menu choice `1`, capture the in-game prompt, send no game commands, then disconnect.

### Full

```bash
python3 .agents/skills/mud-login/scripts/login.py --stage full
```

Authenticate, enter the game, execute exactly one `look`, capture the room output, send `quit`, capture the logout response, then disconnect.

## Preflight

Before running `menu`, `enter`, or `full`:

```bash
python3 --version
test -f .agents/skills/mud-login/scripts/login.py
test -n "$MUD_PASSWORD"
```

Do not display the password.

## Network approval

If the sandbox blocks localhost access:

1. Request approval limited to the helper command and `localhost:4000`.
2. Retry only once after approval.
3. Do not request danger-full-access.
4. Stop and report the exact error and exit code if it still fails.

## Reporting

Report in the terminal conversation:

- stage executed;
- connection status;
- login status;
- room output (when applicable);
- exits;
- visible characters or objects (when applicable);
- logout response;
- exit code;
- unexpected prompts or errors.

Do not create report files.

## Safety

- Do not create a new character.
- Do not move unless explicitly authorized.
- Do not enter combat.
- Do not use administrator commands.
- Do not modify repository files during a login run.
- Do not retry authentication more than once.
- Stop immediately if the protocol reaches an unexpected state.
