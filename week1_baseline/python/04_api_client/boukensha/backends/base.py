from __future__ import annotations

from typing import Any, ClassVar

from ..errors import UnsupportedModelError


class Base:
    MODELS: ClassVar[dict[str, dict[str, Any]]] = {}

    def __init__(self, model: object) -> None:
        self.model = self.validate_model(model)
        self._model_info = self.MODELS[self.model]

    @classmethod
    def models(cls) -> dict[str, dict[str, Any]]:
        return cls.MODELS

    @classmethod
    def model_info(cls, model: object) -> dict[str, Any] | None:
        return cls.models().get(str(model))

    @classmethod
    def validate_model(cls, model: object) -> str:
        normalized = str(model)
        if normalized in cls.models():
            return normalized
        supported = ", ".join(sorted(cls.models()))
        raise UnsupportedModelError(
            f"{cls.__name__} does not support model {normalized!r}. "
            f"Supported models: {supported}"
        )

    @property
    def model_metadata(self) -> dict[str, Any]:
        return self._model_info

    @property
    def context_window(self) -> int:
        return self._model_info["context_window"]

    @property
    def input_token_cost_per_million(self) -> float | None:
        return self._model_info["cost_per_million"]["input"]

    @property
    def output_token_cost_per_million(self) -> float | None:
        return self._model_info["cost_per_million"]["output"]

    @property
    def usage_unit(self) -> str:
        return self._model_info["usage_unit"]

    @property
    def usage_level(self) -> str | None:
        return self._model_info.get("usage_level")

    @property
    def advertised_context_window(self) -> int | None:
        return self._model_info.get("advertised_context_window")

    def estimate_cost(self, *, input_tokens: int, output_tokens: int) -> float | None:
        input_cost = self.input_token_cost_per_million
        output_cost = self.output_token_cost_per_million
        if input_cost is None or output_cost is None:
            return None
        return ((input_tokens * input_cost) + (output_tokens * output_cost)) / 1_000_000.0
