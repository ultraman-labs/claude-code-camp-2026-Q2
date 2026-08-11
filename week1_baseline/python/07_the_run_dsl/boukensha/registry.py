from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Callable

from .context import Context
from .errors import UnknownToolError
from .tool import Tool


class Registry:
    def __init__(self, context: Context) -> None:
        self._context = context

    def tool(
        self,
        name: object,
        *,
        description: object,
        parameters: Mapping[str, Any] | None = None,
        block: Callable[..., Any],
    ) -> Tool:
        tool = Tool(str(name), description, {} if parameters is None else parameters, block)
        self._context.register_tool(tool)
        return tool

    def dispatch(self, name: object, args: Mapping[object, Any] | None = None) -> Any:
        tool = self._context.tools.get(str(name))
        if tool is None:
            raise UnknownToolError(f"No tool registered as '{name}'")
        normalized_args = {str(key): value for key, value in (args or {}).items()}
        return tool.block(**normalized_args)
