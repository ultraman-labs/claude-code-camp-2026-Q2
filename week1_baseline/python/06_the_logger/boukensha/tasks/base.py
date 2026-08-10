from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


class Base:
    DEFAULT_MAX_ITERATIONS = 25
    DEFAULT_MAX_OUTPUT_TOKENS = 1024

    @classmethod
    def task_name(cls) -> str:
        raise NotImplementedError(f"{cls.__name__} must define task_name")

    @classmethod
    def provider(cls, settings: Mapping[str, Any]) -> Any:
        value = cls._fetch(settings, "provider")
        if value is None:
            raise ValueError(f"tasks.{cls.task_name()}.provider is required in settings.yml")
        return value

    @classmethod
    def model(cls, settings: Mapping[str, Any]) -> Any:
        value = cls._fetch(settings, "model")
        if value is None:
            raise ValueError(f"tasks.{cls.task_name()}.model is required in settings.yml")
        return value

    @classmethod
    def prompt_override(cls, settings: Mapping[str, Any], prompt: str = "system") -> bool:
        node = cls._fetch(settings, "prompt_override")
        return isinstance(node, Mapping) and node.get(str(prompt)) is True

    @classmethod
    def prompt(cls, settings: Mapping[str, Any], name: str = "system", *,
               user_prompts_dir: Path | str | None = None,
               default_prompts_dir: Path | str | None = None) -> str | None:
        if cls.prompt_override(settings, name) and user_prompts_dir:
            text = cls._read_file(Path(user_prompts_dir) / cls.task_name() / f"{name}.md")
            if text is not None:
                return text
        if default_prompts_dir:
            return cls._read_file(Path(default_prompts_dir) / f"{name}.md")
        return None

    @classmethod
    def system_prompt(cls, settings: Mapping[str, Any], **kwargs: Any) -> str | None:
        return cls.prompt(settings, "system", **kwargs)

    @classmethod
    def max_iterations(cls, settings: Mapping[str, Any]) -> int:
        return cls._integer_setting(settings, "max_iterations", cls.DEFAULT_MAX_ITERATIONS)

    @classmethod
    def max_output_tokens(cls, settings: Mapping[str, Any]) -> int:
        return cls._integer_setting(settings, "max_output_tokens", cls.DEFAULT_MAX_OUTPUT_TOKENS)

    @staticmethod
    def _fetch(settings: Mapping[str, Any], key: str) -> Any:
        return settings.get(key)

    @classmethod
    def _integer_setting(cls, settings: Mapping[str, Any], key: str, default: int) -> int:
        value = cls._fetch(settings, key)
        if value is None:
            return default
        return int(value)

    @staticmethod
    def _read_file(path: Path) -> str | None:
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8").strip()
