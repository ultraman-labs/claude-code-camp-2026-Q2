from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Callable

from .registry import Registry


class RunDSL:
    """The small DSL surface exposed inside a Boukensha run."""

    def __init__(self, registry: Registry) -> None:
        self._registry = registry

    def tool(
        self,
        name: object,
        *,
        description: object,
        parameters: Mapping[str, Any] | None = None,
        block: Callable[..., Any],
    ) -> Any:
        return self._registry.tool(
            name,
            description=description,
            parameters=parameters,
            block=block,
        )
