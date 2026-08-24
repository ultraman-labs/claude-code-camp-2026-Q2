from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from boukensha import run


os.environ.setdefault("BOUKENSHA_DIR", str(Path(__file__).resolve().parents[3] / ".boukensha"))


run(
    task=(
        "Connect to the MUD, look at your surroundings, check your score, "
        "then look at the available exits and tell me what you see."
    ),
    working_dir=False,
)
