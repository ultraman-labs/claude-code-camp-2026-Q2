from __future__ import annotations

from typing import Any

from .base import Base


class OpenAI(Base):
    BASE_URL = "https://api.openai.com/v1/chat/completions"
    MODELS = {
        "gpt-5.6-luna": {"context_window": 1_050_000, "cost_per_million": {"input": 1.0, "output": 6.0}, "usage_unit": "tokens"},
        "gpt-5.5": {"context_window": 1_000_000, "cost_per_million": {"input": 5.0, "output": 30.0}, "usage_unit": "tokens"},
        "gpt-5.4": {"context_window": 1_000_000, "cost_per_million": {"input": 2.5, "output": 15.0}, "usage_unit": "tokens"},
        "gpt-5.4-mini": {"context_window": 400_000, "cost_per_million": {"input": 0.75, "output": 4.5}, "usage_unit": "tokens"},
    }

    def __init__(self, *, api_key: str, model: object) -> None:
        self._api_key = api_key
        super().__init__(model)

    @staticmethod
    def _require_text(value: object, message_type: str) -> str:
        if not isinstance(value, str):
            raise ValueError(f"Outbound {message_type} message content must be a str")
        return value

    def to_messages(self, context: Any) -> list[dict[str, Any]]:
        messages = [{"role": "system", "content": self._require_text(context.system, "system")}]
        for msg in context.messages:
            if msg.role == "tool_result":
                content = self._require_text(msg.content, "tool-result")
                messages.append({"role": "tool", "tool_call_id": msg.tool_use_id, "content": content})
            else:
                content = self._require_text(msg.content, str(msg.role))
                messages.append({"role": str(msg.role), "content": content})
        return messages

    def to_tools(self, tools: dict[str, Any]) -> list[dict[str, Any]]:
        return [{"type": "function", "function": {"name": t.name, "description": t.description, "parameters": {"type": "object", "properties": t.parameters, "required": [str(k) for k in t.parameters]}}} for t in tools.values()]

    def to_payload(self, context: Any, max_output_tokens: int = 1024) -> dict[str, Any]:
        return {"model": self.model, "messages": self.to_messages(context), "tools": self.to_tools(context.tools), "max_completion_tokens": max_output_tokens, "reasoning_effort": "none"}

    def headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self._api_key}"}

    def url(self) -> str:
        return self.BASE_URL
