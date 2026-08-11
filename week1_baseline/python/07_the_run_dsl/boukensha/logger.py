from __future__ import annotations

import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Logger:
    DEFAULT_SESSION_DIR = "sessions"

    def __init__(
        self,
        session_id: str | None = None,
        dir: str | Path | None = None,
        log: str | Path | None = None,
        snapshot: dict[str, Any] | None = None,
    ) -> None:
        self.session_id = session_id or self._generate_session_id()
        self.path = Path(log) if log is not None else self._default_path(dir)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._log_io = self.path.open("a", encoding="utf-8")
        self._write_log({"phase": "session_start", **(snapshot or {})})

    def iteration(self, n: int, max: int) -> None:
        self._write_log({"phase": "iteration", "n": n, "max": max})

    def limit_reached(self, kind: Any, n: int, max: int) -> None:
        self._write_log({"phase": "limit_reached", "kind": kind, "n": n, "max": max})

    def turn_end(self, reason: Any, iterations: int, tokens: Any = None) -> None:
        self._write_log({"phase": "turn_end", "reason": reason, "iterations": iterations, "tokens": tokens})

    def prompt(self, messages: list[Any], tools: dict[str, Any]) -> None:
        self._write_log({
            "phase": "prompt",
            "message_count": len(messages),
            "messages": [self._serialize_message(message) for message in messages],
            "tool_count": len(tools),
            "tools": list(tools.keys()),
        })

    def tool_call(self, name: Any, args: Any) -> None:
        self._write_log({"phase": "tool_call", "name": name, "args": args})

    def tool_result(self, name: Any, result: Any, ok: bool = True, error: Any = None) -> None:
        self._write_log({"phase": "tool_result", "name": name, "result": self._ruby_string(result), "ok": ok, "error": error})

    def response(
        self,
        text: Any,
        usage: dict[str, Any] | None = None,
        stop_reason: Any = None,
        task: Any = None,
        backend: Any = None,
    ) -> None:
        event = {
            "phase": "response",
            "text": self._ruby_string(text).strip(),
            "usage": usage,
            "stop_reason": stop_reason,
        }
        event.update(self._execution_metadata(task, backend, usage))
        self._write_log(event)

    def raw(self, data: Any) -> None:
        if not self._debug_enabled():
            return
        self._write_log({"phase": "raw", "data": data})

    def close(self) -> None:
        self._log_io.close()

    def _default_path(self, directory: str | Path | None) -> Path:
        if directory is None:
            from .config import Config

            directory = Path(Config().dir) / self.DEFAULT_SESSION_DIR
        return Path(directory) / f"{self.session_id}.jsonl"

    def _write_log(self, event: dict[str, Any]) -> None:
        record = {**event, "session_id": self.session_id, "at": datetime.now().astimezone().isoformat()}
        self._log_io.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        self._log_io.flush()

    @staticmethod
    def _generate_session_id() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"{timestamp}-{secrets.token_hex(4)}"

    @staticmethod
    def _serialize_message(message: Any) -> dict[str, Any]:
        if isinstance(message, dict):
            return {"role": message.get("role"), "content": message.get("content")}
        return {"role": message.role, "content": message.content}

    def _execution_metadata(self, task: Any, backend: Any, usage: dict[str, Any] | None) -> dict[str, Any]:
        if task is None and backend is None and usage is None:
            return {}
        tokens = self._usage_tokens(usage)
        metadata = {
            "task": self._task_name(task),
            "provider": self._provider_name(backend),
            "model": getattr(backend, "model", None),
            "usage_unit": getattr(backend, "usage_unit", None),
            "usage_level": getattr(backend, "usage_level", None),
            "input_tokens": tokens["input"],
            "output_tokens": tokens["output"],
            "cost_usd": self._estimate_cost(backend, tokens),
        }
        return {key: value for key, value in metadata.items() if value is not None}

    @staticmethod
    def _task_name(task: Any) -> Any:
        return getattr(task, "task_name", str(task) if task is not None else None)

    @staticmethod
    def _provider_name(backend: Any) -> str | None:
        if backend is None:
            return None
        name = backend.__class__.__name__
        return re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name).lower()

    def _usage_tokens(self, usage: dict[str, Any] | None) -> dict[str, int | None]:
        usage = usage or {}
        return {
            "input": self._first_integer(usage, "input_tokens", "prompt_tokens", "promptTokenCount", "prompt_eval_count"),
            "output": self._first_integer(usage, "output_tokens", "completion_tokens", "candidatesTokenCount", "eval_count"),
        }

    @staticmethod
    def _first_integer(values: dict[str, Any], *keys: str) -> int | None:
        for key in keys:
            value = values.get(key)
            if value is not None:
                try:
                    return int(value)
                except (TypeError, ValueError):
                    return None
        return None

    @staticmethod
    def _estimate_cost(backend: Any, tokens: dict[str, int | None]) -> Any:
        if backend is None or not callable(getattr(backend, "estimate_cost", None)):
            return None
        if tokens["input"] is None or tokens["output"] is None:
            return None
        return backend.estimate_cost(input_tokens=tokens["input"], output_tokens=tokens["output"])

    @staticmethod
    def _ruby_string(value: Any) -> str:
        return "" if value is None else str(value)

    @staticmethod
    def _debug_enabled() -> bool:
        import sys

        package = sys.modules.get("boukensha")
        debug = getattr(package, "debug", None)
        return bool(debug() if callable(debug) else debug) if debug is not None else False
