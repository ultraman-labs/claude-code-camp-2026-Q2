from __future__ import annotations

from typing import Any

from .base import Base


class Ollama(Base):
    MODELS = {
        "gemma4": {"context_window": 128_000, "cost_per_million": {"input": 0.0, "output": 0.0}, "usage_unit": "local_compute"},
        "gemma4:e2b": {"context_window": 128_000, "cost_per_million": {"input": 0.0, "output": 0.0}, "usage_unit": "local_compute"},
        "gemma4:e4b": {"context_window": 128_000, "cost_per_million": {"input": 0.0, "output": 0.0}, "usage_unit": "local_compute"},
        "gemma4:12b": {"context_window": 256_000, "cost_per_million": {"input": 0.0, "output": 0.0}, "usage_unit": "local_compute"},
        "gemma4:26b": {"context_window": 256_000, "cost_per_million": {"input": 0.0, "output": 0.0}, "usage_unit": "local_compute"},
        "gemma4:31b": {"context_window": 256_000, "cost_per_million": {"input": 0.0, "output": 0.0}, "usage_unit": "local_compute"},
        "qwen3:30b": {"context_window": 256_000, "cost_per_million": {"input": 0.0, "output": 0.0}, "usage_unit": "local_compute"},
        "qwen3:8b": {"context_window": 40_000, "cost_per_million": {"input": 0.0, "output": 0.0}, "usage_unit": "local_compute"},
        "deepseek-r1:8b": {"context_window": 128_000, "cost_per_million": {"input": 0.0, "output": 0.0}, "usage_unit": "local_compute"},
    }

    def __init__(self, *, host: str = "http://localhost:11434", model: object) -> None:
        self._host = host
        super().__init__(model)

    def to_messages(self, context: Any) -> list[dict[str, Any]]:
        messages = [{"role": "system", "content": context.system}]
        for msg in context.messages:
            if msg.role == "tool_result":
                messages.append({"role": "tool", "tool_name": msg.tool_use_id, "content": msg.content})
            else:
                messages.append({"role": str(msg.role), "content": msg.content})
        return messages

    def to_tools(self, tools: dict[str, Any]) -> list[dict[str, Any]]:
        return [{"type": "function", "function": {"name": t.name, "description": t.description, "parameters": {"type": "object", "properties": t.parameters, "required": [str(k) for k in t.parameters]}}} for t in tools.values()]

    def to_payload(self, context: Any, max_output_tokens: int = 1024) -> dict[str, Any]:
        return {"model": self.model, "stream": False, "messages": self.to_messages(context), "tools": self.to_tools(context.tools)}

    def headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json"}

    def url(self) -> str:
        return f"{self._host}/api/chat"
