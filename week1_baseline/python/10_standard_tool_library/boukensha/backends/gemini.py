from __future__ import annotations

from typing import Any

from .base import Base


class Gemini(Base):
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    MODELS = {
        "gemini-3.5-flash": {"context_window": 1_048_576, "cost_per_million": {"input": 1.5, "output": 9.0}, "usage_unit": "tokens"},
        "gemini-3.1-flash-lite": {"context_window": 1_048_576, "cost_per_million": {"input": 0.25, "output": 1.5}, "usage_unit": "tokens"},
        "gemini-2.5-pro": {"context_window": 1_048_576, "cost_per_million": {"input": 1.25, "output": 10.0}, "usage_unit": "tokens"},
        "gemini-2.5-flash": {"context_window": 1_048_576, "cost_per_million": {"input": 0.30, "output": 2.50}, "usage_unit": "tokens"},
        "gemini-2.5-flash-lite": {"context_window": 1_048_576, "cost_per_million": {"input": 0.10, "output": 0.40}, "usage_unit": "tokens"},
    }

    def __init__(self, *, api_key: str, model: object) -> None:
        self._api_key = api_key
        super().__init__(model)

    def to_messages(self, context: Any) -> list[dict[str, Any]]:
        result = []
        for msg in context.messages:
            if msg.role == "assistant":
                result.append({"role": "model", "parts": self._assistant_parts(msg.content)})
            elif msg.role == "tool_result":
                result.append({"role": "user", "parts": [{"functionResponse": {"name": msg.tool_use_id, "response": {"content": msg.content}}}]})
            else:
                result.append({"role": str(msg.role), "parts": [{"text": str(msg.content)}]})
        return result

    def to_tools(self, tools: dict[str, Any]) -> list[dict[str, Any]]:
        if not tools:
            return []
        return [{"functionDeclarations": [{"name": t.name, "description": t.description, "parameters": {"type": "object", "properties": t.parameters, "required": [str(k) for k in t.parameters]}} for t in tools.values()]}]

    def to_payload(
        self,
        context: Any,
        max_output_tokens: int = 1024,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return {
            "systemInstruction": {"parts": [{"text": str(context.system)}]},
            "contents": self.to_messages(context),
            "tools": self.to_tools(context.tools) if tools is None else tools,
            "generationConfig": {"maxOutputTokens": max_output_tokens},
        }

    def parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        candidates = response.get("candidates") or []
        candidate = candidates[0] if candidates else {}
        parts = (candidate.get("content") or {}).get("parts") or []

        content: list[dict[str, Any]] = []
        tool_used = False
        for part in parts:
            function_call = part.get("functionCall")
            if function_call is not None:
                name = function_call.get("name")
                content.append(
                    {
                        "type": "tool_use",
                        "id": name,
                        "name": name,
                        "input": function_call.get("args") or {},
                    }
                )
                tool_used = True
            elif part.get("text"):
                content.append({"type": "text", "text": part["text"]})

        return {
            "stop_reason": "tool_use" if tool_used else "end_turn",
            "content": content,
        }

    @staticmethod
    def _assistant_parts(content: object) -> list[dict[str, Any]]:
        blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content
        return [
            {"functionCall": {"name": block["name"], "args": block["input"]}}
            if block.get("type") == "tool_use"
            else {"text": block["text"]}
            for block in (blocks or [])
        ]

    def headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json", "x-goog-api-key": self._api_key}

    def url(self) -> str:
        return f"{self.BASE_URL}/{self.model}:generateContent"
