from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


class Config:
    DEFAULT_DIR = Path.home() / ".boukensha"
    PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

    def __init__(self) -> None:
        self.dir = self._resolve_dir()
        self._load_env()
        self.settings = self._load_settings()

    def tasks(self, name: str | None = None) -> dict[str, Any] | None:
        all_tasks = self.dig("tasks") or {}
        if name is None:
            return all_tasks
        return all_tasks.get(str(name))

    @property
    def user_prompts_dir(self) -> Path:
        return self.dir / "prompts"

    @property
    def mud_host(self) -> Any:
        value = self.dig("mud", "host")
        return "localhost" if value is None else value

    @property
    def mud_port(self) -> Any:
        value = self.dig("mud", "port")
        return 4000 if value is None else value

    @property
    def mud_username(self) -> Any:
        return self.dig("mud", "username")

    @property
    def mud_password(self) -> Any:
        return self.dig("mud", "password")

    def dig(self, *keys: str) -> Any:
        node: Any = self.settings
        for key in keys:
            if not isinstance(node, dict):
                return None
            node = node.get(str(key))
        return node

    def __str__(self) -> str:
        task_names = ",".join(self.tasks().keys())
        return f"#<Boukensha::Config dir={self.dir} tasks={task_names}>"

    __repr__ = __str__

    def _resolve_dir(self) -> Path:
        configured_dir = os.environ.get("BOUKENSHA_DIR")
        if configured_dir:
            return Path(configured_dir).expanduser().resolve()

        return self.DEFAULT_DIR.expanduser().resolve()

    def _load_env(self) -> None:
        env_file = self.dir / ".env"
        if env_file.is_file():
            load_dotenv(env_file)

    def _load_settings(self) -> dict[str, Any]:
        settings_file = self.dir / "settings.yaml"
        if not settings_file.is_file():
            return {}
        with settings_file.open(encoding="utf-8") as stream:
            settings = yaml.safe_load(stream)
        if settings is None:
            return {}
        if not isinstance(settings, dict):
            raise ValueError(
                f"{settings_file} must contain a YAML mapping at the root; "
                f"got {type(settings).__name__}"
            )
        return settings
