"""Console entry point for the installed Boukensha command."""

from . import repl


def main() -> None:
    """Launch the packaged Step 9 interactive REPL."""

    repl()


if __name__ == "__main__":
    main()
