from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def register(registry: Any, *, working_dir: str | Path, timeout: float = 30, allowed_commands: list[str] | None = None) -> None:
    root = Path(working_dir).expanduser().resolve()

    def run_command(command: str) -> str:
        if allowed_commands is not None:
            executable = command.strip().split()[0] if command.strip().split() else ""
            allowed = [str(item) for item in allowed_commands]
            if executable not in allowed:
                return f"error: '{executable}' is not in the allowed-commands list ({', '.join(allowed)})"
        try:
            completed = subprocess.run(command, cwd=root, shell=True, capture_output=True, text=True, timeout=timeout)
        except FileNotFoundError as exc:
            return f"error: command not found: {exc}"
        except subprocess.TimeoutExpired:
            return f"error: command timed out after {timeout:g}s: {command}"
        except Exception as exc:
            return f"error: {exc}"
        output = ((completed.stdout or "") + (completed.stderr or "")).strip()
        exit_note = "" if completed.returncode == 0 else f"\n[exit {completed.returncode}]"
        return f"{output}{exit_note}" if output else f"(no output){exit_note}"

    registry.tool("run_command", description="Run a shell command inside the working directory and return combined output.", parameters={"command": {"type": "string", "description": "The shell command to execute"}}, block=run_command)
