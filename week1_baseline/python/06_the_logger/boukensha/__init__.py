from .config import Config
from .context import Context
from .client import Client
from .agent import Agent
from .logger import Logger
from .errors import ApiError, UnknownToolError, UnsupportedModelError
from .message import Message
from .prompt_builder import PromptBuilder
from .registry import Registry
from .tasks.player import Player
from .tool import Tool

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
    "Tool",
    "UnknownToolError",
    "UnsupportedModelError",
    "debug",
    "debug_on",
    "is_quiet",
    "loud",
    "quiet",
]
