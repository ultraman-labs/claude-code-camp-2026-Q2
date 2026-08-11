from __future__ import annotations

import json
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
            elif msg.role == "assistant":
                messages.append(self._assistant_message(msg.content))
            else:
                content = self._require_text(msg.content, str(msg.role))
                messages.append({"role": str(msg.role), "content": content})
        return messages

    def to_tools(self, tools: dict[str, Any]) -> list[dict[str, Any]]:
        return [{"type": "function", "function": {"name": t.name, "description": t.description, "parameters": {"type": "object", "properties": t.parameters, "required": [str(k) for k in t.parameters]}}} for t in tools.values()]

    def to_payload(
        self,
        context: Any,
        max_output_tokens: int = 1024,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": self.to_messages(context),
            "tools": self.to_tools(context.tools) if tools is None else tools,
            "max_completion_tokens": max_output_tokens,
            "reasoning_effort": "none",
        }

    def parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        choices = response.get("choices") or []
        message = choices[0].get("message", {}) if choices else {}
        tool_calls = message.get("tool_calls") or []

        content: list[dict[str, Any]] = []
        if message.get("content") is not None:
            content.append({"type": "text", "text": message["content"]})

        for tool_call in tool_calls:
            function = tool_call.get("function") or {}
            arguments = function.get("arguments") or "{}"
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            content.append(
                {
                    "type": "tool_use",
                    "id": tool_call.get("id"),
                    "name": function.get("name"),
                    "input": arguments,
                }
            )

        return {
            "stop_reason": "tool_use" if tool_calls else "end_turn",
            "content": content,
        }

    @staticmethod
    def _assistant_message(content: object) -> dict[str, Any]:
        blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content
        blocks = blocks or []
        text_blocks = [block for block in blocks if block.get("type") == "text"]
        tool_blocks = [block for block in blocks if block.get("type") == "tool_use"]

        message: dict[str, Any] = {
            "role": "assistant",
            "content": "".join(block["text"] for block in text_blocks),
        }
        if tool_blocks:
            message["tool_calls"] = [
                {
                    "id": block["id"],
                    "type": "function",
                    "function": {
                        "name": block["name"],
                        "arguments": json.dumps(block["input"]),
                    },
                }
                for block in tool_blocks
            ]
        return message

    def headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self._api_key}"}

    def url(self) -> str:
        return self.BASE_URL
