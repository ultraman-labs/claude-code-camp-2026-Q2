from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: object
    parameters: dict[str, Any]
    block: Callable[..., Any]

    def __str__(self) -> str:
        parameter_names = list(self.parameters.keys())
        return (
            f"#<Tool name={self.name} description={str(self.description)[:41]}... "
            f"params={parameter_names}>"
        )

    __repr__ = __str__
