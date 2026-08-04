from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from boukensha import Client, Config, Context, Player, PromptBuilder, Registry
from boukensha.backends import Anthropic, Gemini, Ollama, OllamaCloud, OpenAI


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
os.environ.setdefault("BOUKENSHA_DIR", str(REPOSITORY_ROOT / ".boukensha"))

config = Config()
player_settings = config.tasks("player") or {}
provider = Player.provider(player_settings)
model = Player.model(player_settings)
system_prompt = Player.system_prompt(
    player_settings,
    user_prompts_dir=config.user_prompts_dir,
    default_prompts_dir=Config.PROMPTS_DIR,
)

context = Context(task=Player, system=system_prompt)
registry = Registry(context)
registry.tool(
    "read_file",
    description="Read the contents of a file from disk",
    parameters={"path": {"type": "string", "description": "The file path to read"}},
    block=lambda path: Path(path).read_text(encoding="utf-8"),
)
registry.tool(
    "list_directory",
    description="List files in a directory",
    parameters={"path": {"type": "string", "description": "The directory path to list"}},
    block=lambda path: "\n".join(item.name for item in Path(path).iterdir() if not item.name.startswith(".")),
)
context.add_message("user", "What files are in the current directory?")

backend_classes = {
    "anthropic": (Anthropic, "ANTHROPIC_API_KEY"),
    "gemini": (Gemini, "GEMINI_API_KEY"),
    "ollama": (Ollama, None),
    "ollama_cloud": (OllamaCloud, "OLLAMA_API_KEY"),
    "openai": (OpenAI, "OPENAI_API_KEY"),
}
try:
    backend_class, key_name = backend_classes[provider]
except KeyError as exc:
    raise ValueError(f"Unsupported provider for player task: {provider}") from exc
if key_name is not None:
    api_key = os.environ.get(key_name)
    if not api_key:
        raise RuntimeError(f"Missing {key_name} for hosted provider {provider}")
    backend = backend_class(api_key=api_key, model=model)
else:
    backend = backend_class(model=model)

builder = PromptBuilder(context, backend)
client = Client(builder)
redacted_headers = {
    name: "<redacted>" if name.lower() in {"authorization", "x-api-key", "x-goog-api-key"} else value
    for name, value in builder.headers().items()
}

print("=== BOUKENSHA Step 4: API Client ===")
print(f"Config: {config}")
print(f"Provider: {provider}")
print(f"Model: {model}")
print(f"URL: {builder.url()}")
print(f"Headers: {redacted_headers}")
print("Raw response:")
print(json.dumps(client.call(), indent=2))
