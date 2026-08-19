from __future__ import annotations

from pathlib import Path
from typing import Any

from .agent import Agent
from .errors import ApiError
from .version import VERSION


class Repl:
    """Interactive Boukensha session loop."""

    PROMPT = "boukensha> "

    HELP = """Commands:
  /quiet   suppress logging output
  /loud    re-enable logging output
  /clear   wipe conversation history (tools stay)
  /exit    leave the REPL
  /help    show this message"""

    def __init__(
        self,
        *,
        context: Any,
        registry: Any,
        builder: Any,
        client: Any,
        logger: Any,
        task_settings: Any = None,
        max_iterations: Any = None,
        max_output_tokens: Any = None,
        config_dir: str | Path | None = None,
        provider: str | None = None,
        model: Any = None,
        version: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self._context = context
        self._registry = registry
        self._builder = builder
        self._client = client
        self._logger = logger
        self._task_settings = task_settings
        self._max_iterations = max_iterations
        self._max_output_tokens = max_output_tokens
        self._config_dir = Path(config_dir) if config_dir is not None else None
        self._provider = provider
        self._model = model
        self._version = version or VERSION
        self._turn = 0

    def start(self) -> None:
        print(self._banner())

        while True:
            try:
                user_input = input(self.PROMPT)
            except EOFError:
                break

            user_input = user_input.strip()
            if not user_input:
                continue

            if user_input in {"/exit", "/quit"}:
                print("Goodbye.")
                break

            if user_input == "/help":
                print(self.HELP)
                continue

            if user_input == "/quiet":
                self._quiet()
                print("(logging suppressed — type /loud to re-enable)")
                continue

            if user_input == "/loud":
                self._loud()
                print("(logging enabled)")
                continue

            if user_input == "/clear":
                self._context.clear_messages()
                self._turn = 0
                print("(conversation history cleared)")
                continue

            self._run_turn(user_input)

    def _banner(self) -> str:
        provider = self._provider or "default"
        model = self._model or "default"
        config_line = str(self._config_dir) if self._config_dir is not None else "(default)"

        return (
            f"BOUKENSHA MUD Assistant (v{self._version})\n"
            f"config:        {config_line}\n"
            f"provider:      {provider}\n"
            f"model:         {model}\n\n"
            "/quiet or /loud   toggle logging\n"
            "/clear            reset conversation history\n"
            "/exit or /quit    leave the REPL"
        )

    def _run_turn(self, user_input: str) -> None:
        self._turn += 1
        self._log_turn()

        self._context.add_message("user", user_input)

        agent = Agent(
            context=self._context,
            registry=self._registry,
            builder=self._builder,
            client=self._client,
            logger=self._logger,
            task_settings=self._task_settings,
            max_iterations=self._max_iterations,
            max_output_tokens=self._max_output_tokens,
        )

        try:
            result = agent.run()
            print()
            print(result)
        except ApiError as error:
            print(f"\n[error] API call failed: {error}")

    def _log_turn(self) -> None:
        turn = getattr(self._logger, "turn", None)
        if callable(turn):
            turn(n=self._turn)

    @staticmethod
    def _quiet() -> None:
        import boukensha

        boukensha.quiet()

    @staticmethod
    def _loud() -> None:
        import boukensha

        boukensha.loud()
