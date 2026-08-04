from __future__ import annotations

from typing import Any


class PromptBuilder:
    def __init__(self, context: Any, backend: Any) -> None:
        self.context = context
        self.backend = backend

    def to_messages(self) -> list[dict[str, Any]]:
        return self.backend.to_messages(self.context)

    def to_tools(self) -> list[dict[str, Any]]:
        return self.backend.to_tools(self.context.tools)

    def to_api_payload(self, max_output_tokens: int = 1024) -> dict[str, Any]:
        return self.backend.to_payload(self.context, max_output_tokens=max_output_tokens)

    def headers(self) -> dict[str, str]:
        return self.backend.headers()

    def url(self) -> str:
        return self.backend.url()

    def estimate_cost(self, *, input_tokens: int, output_tokens: int) -> float | None:
        return self.backend.estimate_cost(input_tokens=input_tokens, output_tokens=output_tokens)
