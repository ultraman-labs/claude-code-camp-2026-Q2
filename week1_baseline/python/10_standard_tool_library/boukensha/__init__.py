import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .config import Config
from .context import Context
from .client import Client
from .agent import Agent
from .logger import Logger
from .errors import ApiError, UnknownToolError, UnsupportedModelError
from .message import Message
from .prompt_builder import PromptBuilder
from .registry import Registry
from .run_dsl import RunDSL
from .repl import Repl
from .version import VERSION
from .tasks.player import Player
from .tool import Tool
from .backends import Anthropic, Gemini, Ollama, OllamaCloud, OpenAI
from .tools import file_system, shell, mud as mud_tools


_quiet = False
_debug = False


def quiet() -> None:
    global _quiet
    _quiet = True


def loud() -> None:
    global _quiet
    _quiet = False


def is_quiet() -> bool:
    return _quiet


def debug_on() -> None:
    global _debug
    _debug = True


def debug() -> bool:
    return _debug


def run(
    *,
    task: str,
    system: str | None = None,
    model: object | None = None,
    backend: str | None = None,
    api_key: str | None = None,
    ollama_host: str = "http://localhost:11434",
    log: str | Path | None = None,
    max_output_tokens: int | None = None,
    configure: Callable[[RunDSL], Any] | None = None,
    working_dir: str | Path | bool = Path.cwd(),
    allowed_commands: list[str] | None = None,
    shell_timeout: float = 30,
    mud: dict[str, Any] | bool | None = None,
) -> str:
    cfg = Config()
    task_class = Player
    task_name = task_class.task_name()
    task_settings = cfg.tasks(task_name) or {}

    if system is None:
        system = task_class.system_prompt(
            task_settings,
            user_prompts_dir=cfg.user_prompts_dir,
            default_prompts_dir=Config.PROMPTS_DIR,
        )

    if model is None:
        model = task_class.model(task_settings)

    if backend is None:
        backend = str(task_class.provider(task_settings))

    if api_key is None:
        api_key = {
            "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
            "openai": os.environ.get("OPENAI_API_KEY"),
            "gemini": os.environ.get("GEMINI_API_KEY"),
            "ollama_cloud": os.environ.get("OLLAMA_API_KEY"),
        }.get(backend)

    context = Context(task=task_class, system=system, working_dir=working_dir)
    registry = Registry(context)

    if working_dir is not False:
        file_system.register(registry, working_dir=working_dir)
        shell.register(registry, working_dir=working_dir, timeout=shell_timeout, allowed_commands=allowed_commands)
    resolved_mud = None if mud is False else (mud or _mud_from_config(cfg))
    if resolved_mud:
        mud_tools.register(registry, **resolved_mud)

    if configure is not None:
        configure(RunDSL(registry))

    backend_classes = {
        "anthropic": Anthropic,
        "openai": OpenAI,
        "gemini": Gemini,
        "ollama": Ollama,
        "ollama_cloud": OllamaCloud,
    }

    try:
        backend_class = backend_classes[backend]
    except KeyError as exc:
        raise ValueError(
            f"Unknown backend {backend!r}. Use: "
            "anthropic, openai, gemini, ollama, or ollama_cloud."
        ) from exc

    if backend == "ollama":
        provider_backend = backend_class(host=ollama_host, model=model)
    elif backend == "ollama_cloud":
        provider_backend = backend_class(api_key=api_key, model=model)
    else:
        provider_backend = backend_class(api_key=api_key, model=model)

    builder = PromptBuilder(context, provider_backend)
    client = Client(builder)

    effective_max_iterations = task_class.max_iterations(task_settings)
    effective_max_output_tokens = (
        max_output_tokens
        if max_output_tokens is not None
        else task_class.max_output_tokens(task_settings)
    )

    logger = None
    try:
        logger = Logger(
            log=log,
            snapshot={
                "task": task_name,
                "max_iterations": effective_max_iterations,
                "max_output_tokens": effective_max_output_tokens,
                "model": model,
                "provider": backend,
            },
        )

        agent = Agent(
            context=context,
            registry=registry,
            builder=builder,
            client=client,
            logger=logger,
            task_settings=task_settings,
            max_iterations=effective_max_iterations,
            max_output_tokens=effective_max_output_tokens,
        )

        context.add_message("user", task)
        return agent.run()
    finally:
        if logger is not None:
            logger.close()


def repl(
    *,
    system: str | None = None,
    model: object | None = None,
    backend: str | None = None,
    api_key: str | None = None,
    ollama_host: str = "http://localhost:11434",
    log: str | Path | None = None,
    max_output_tokens: int | None = None,
    configure: Callable[[RunDSL], Any] | None = None,
    working_dir: str | Path | bool = Path.cwd(),
    allowed_commands: list[str] | None = None,
    shell_timeout: float = 30,
    mud: dict[str, Any] | bool | None = None,
) -> None:
    """Start an interactive Boukensha REPL session."""

    cfg = Config()
    task_class = Player
    task_name = task_class.task_name()
    task_settings = cfg.tasks(task_name) or {}

    if system is None:
        system = task_class.system_prompt(
            task_settings,
            user_prompts_dir=cfg.user_prompts_dir,
            default_prompts_dir=Config.PROMPTS_DIR,
        )

    if model is None:
        model = task_class.model(task_settings)

    if backend is None:
        backend = str(task_class.provider(task_settings))

    if api_key is None:
        api_key = {
            "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
            "openai": os.environ.get("OPENAI_API_KEY"),
            "gemini": os.environ.get("GEMINI_API_KEY"),
            "ollama_cloud": os.environ.get("OLLAMA_API_KEY"),
        }.get(backend)

    context = Context(task=task_class, system=system, working_dir=working_dir)
    registry = Registry(context)

    if working_dir is not False:
        file_system.register(registry, working_dir=working_dir)
        shell.register(registry, working_dir=working_dir, timeout=shell_timeout, allowed_commands=allowed_commands)
    resolved_mud = None if mud is False else (mud or _mud_from_config(cfg))
    if resolved_mud:
        mud_tools.register(registry, **resolved_mud)

    if configure is not None:
        configure(RunDSL(registry))

    backend_classes = {
        "anthropic": Anthropic,
        "openai": OpenAI,
        "gemini": Gemini,
        "ollama": Ollama,
        "ollama_cloud": OllamaCloud,
    }

    try:
        backend_class = backend_classes[backend]
    except KeyError as exc:
        raise ValueError(
            f"Unknown backend {backend!r}. Use: "
            "anthropic, openai, gemini, ollama, or ollama_cloud."
        ) from exc

    if backend == "ollama":
        provider_backend = backend_class(host=ollama_host, model=model)
    elif backend == "ollama_cloud":
        provider_backend = backend_class(api_key=api_key, model=model)
    else:
        provider_backend = backend_class(api_key=api_key, model=model)

    builder = PromptBuilder(context, provider_backend)
    client = Client(builder)

    effective_max_iterations = task_class.max_iterations(task_settings)
    effective_max_output_tokens = (
        max_output_tokens
        if max_output_tokens is not None
        else task_class.max_output_tokens(task_settings)
    )

    logger = None
    try:
        logger = Logger(
            log=log,
            snapshot={
                "task": task_name,
                "max_iterations": effective_max_iterations,
                "max_output_tokens": effective_max_output_tokens,
                "model": model,
                "provider": backend,
            },
        )

        Repl(
            context=context,
            registry=registry,
            builder=builder,
            client=client,
            logger=logger,
            task_settings=task_settings,
            max_iterations=effective_max_iterations,
            max_output_tokens=effective_max_output_tokens,
            config_dir=cfg.dir,
            provider=backend,
            model=model,
            version=VERSION,
            api_key=api_key,
            mud=resolved_mud,
        ).start()

    except KeyboardInterrupt:
        print("\nInterrupted.")

    finally:
        if logger is not None:
            logger.close()


def _mud_from_config(cfg: Config) -> dict[str, Any] | None:
    if not cfg.mud_host or not cfg.mud_username:
        return None
    return {"host": cfg.mud_host, "port": cfg.mud_port, "name": cfg.mud_username, "password": cfg.mud_password}


__all__ = [
    "Agent",
    "ApiError",
    "Client",
    "Config",
    "Context",
    "Logger",
    "Message",
    "Player",
    "PromptBuilder",
    "Registry",
    "Repl",
    "RunDSL",
    "Tool",
    "UnknownToolError",
    "UnsupportedModelError",
    "VERSION",
    "debug",
    "debug_on",
    "is_quiet",
    "loud",
    "quiet",
    "repl",
    "run",
]
