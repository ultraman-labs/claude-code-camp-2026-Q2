from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from boukensha import RunDSL, run


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
BASE_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault("BOUKENSHA_DIR", str(REPOSITORY_ROOT / ".boukensha"))


def configure_tools(dsl: RunDSL) -> None:
    dsl.tool(
        "read_file",
        description="Read the contents of a file from disk",
        parameters={"path": {"type": "string", "description": "The file path to read"}},
        block=lambda path: (BASE_DIR / path).resolve().read_text(encoding="utf-8"),
    )
    dsl.tool(
        "list_directory",
        description="List files in a directory",
        parameters={"path": {"type": "string", "description": "The directory path to list"}},
        block=lambda path: ", ".join(
            item.name
            for item in (BASE_DIR / path).resolve().iterdir()
            if not item.name.startswith(".")
        ),
    )


print("=== BOUKENSHA Step 7: The Boukensha.run DSL ===")

result = run(
    task="Read the README.md file and summarise what this MUD player assistant framework can do.",
    configure=configure_tools,
)

print()
print("=== FINAL RESPONSE ===")
print(result)
