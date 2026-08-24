"""Console entry point for the installed Boukensha command."""

import os

from . import repl


def main() -> None:
    """Launch the packaged Step 9 interactive REPL."""

    options = {}
    if os.environ.get("MUD_NAME"):
        password = os.environ.get("MUD_PASSWORD")
        if password is None:
            raise SystemExit("boukensha: MUD_NAME is set but MUD_PASSWORD is missing.")
        options = {
            "working_dir": False,
            "mud": {
                "host": os.environ.get("MUD_HOST", "localhost"),
                "port": int(os.environ.get("MUD_PORT", "4000")),
                "name": os.environ["MUD_NAME"],
                "password": password,
            },
        }
    repl(**options)


if __name__ == "__main__":
    main()
