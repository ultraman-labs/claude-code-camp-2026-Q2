from __future__ import annotations

import os
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from boukensha import RunDSL, repl


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
BASE_DIR = Path(__file__).resolve().parents[2] / "07_the_run_dsl"

os.environ.setdefault(
    "BOUKENSHA_DIR",
    str(REPOSITORY_ROOT / ".boukensha"),
)


def configure_tools(dsl: RunDSL) -> None:
    dsl.tool(
        "read_file",
        description="Read the contents of a file from disk",
        parameters={
            "path": {
                "type": "string",
                "description": "File path relative to the working directory",
            }
        },
        block=lambda path: (
            BASE_DIR / path
        ).resolve().read_text(encoding="utf-8"),
    )

    dsl.tool(
        "list_directory",
        description="List the files in a directory",
        parameters={
            "path": {
                "type": "string",
                "description": (
                    "Directory path relative to the working directory, "
                    "or '.' for root"
                ),
            }
        },
        block=lambda path: ", ".join(
            sorted(
                item.name
                for item in (BASE_DIR / path).resolve().iterdir()
                if not item.name.startswith(".")
            )
        ),
    )


repl(configure=configure_tools)