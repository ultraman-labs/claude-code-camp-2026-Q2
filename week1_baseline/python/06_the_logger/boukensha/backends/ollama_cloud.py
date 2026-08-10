from __future__ import annotations

from typing import Any

from .ollama import Ollama


class OllamaCloud(Ollama):
    BASE_URL = "https://ollama.com"
    MODELS = {
        "gemma4:31b-cloud": {"context_window": 256_000, "cost_per_million": {"input": None, "output": None}, "usage_unit": "ollama_cloud_usage", "usage_level": "medium"},
        "minimax-m3:cloud": {"context_window": 512_000, "advertised_context_window": 1_000_000, "cost_per_million": {"input": None, "output": None}, "usage_unit": "ollama_cloud_usage", "usage_level": "high"},
        "kimi-k2.5:cloud": {"context_window": 256_000, "cost_per_million": {"input": None, "output": None}, "usage_unit": "ollama_cloud_usage", "usage_level": "high"},
    }

    def __init__(self, *, api_key: str, model: object) -> None:
        self._api_key = api_key
        super().__init__(host=self.BASE_URL, model=model)

    def headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self._api_key}"}
