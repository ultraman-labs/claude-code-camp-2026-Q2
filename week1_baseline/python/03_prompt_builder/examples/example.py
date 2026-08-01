from __future__ import annotations

import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from boukensha import Config, Context, Player, PromptBuilder, Registry
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

ctx = Context(task=Player, system=system_prompt)
registry = Registry(ctx)
registry.tool(
    "look",
    description="Look around the current room for details",
    parameters={},
    block=lambda: "A damp stone corridor stretches north. Torches flicker on the walls.",
)
registry.tool(
    "move",
    description="Move the player in a direction (north, south, east, west, up, down)",
    parameters={"direction": {"type": "string", "description": "The direction to move"}},
    block=lambda direction: f"You move {direction} into a torch-lit corridor.",
)
ctx.add_message("user", "I just arrived in the dungeon. What's around me, and can you move north?")
ctx.add_message("assistant", "Let me take a look around first.")
ctx.add_message("tool_result", "A damp stone corridor stretches north. Torches flicker on the walls.", "toolu_01X")

key_by_provider = {
    "anthropic": (Anthropic, "ANTHROPIC_API_KEY"),
    "ollama": (Ollama, None),
    "ollama_cloud": (OllamaCloud, "OLLAMA_API_KEY"),
    "openai": (OpenAI, "OPENAI_API_KEY"),
    "gemini": (Gemini, "GEMINI_API_KEY"),
}
try:
    backend_class, key_name = key_by_provider[provider]
except KeyError as error:
    raise ValueError(f"Unsupported provider for player task: {provider}") from error

backend = (
    backend_class(model=model)
    if key_name is None
    else backend_class(api_key=os.environ.get(key_name, ""), model=model)
)
builder = PromptBuilder(ctx, backend)
redacted_headers = {name: "<redacted>" if name.lower() in {"authorization", "x-api-key", "x-goog-api-key"} else value for name, value in builder.headers().items()}

print("=== BOUKENSHA Step 3: Prompt Builder (Python) ===")
print(f"Config: {config}")
print(f"Provider: {provider}")
print(f"Model: {model}")
print(f"Context window: {backend.context_window}")
print(f"Usage unit: {backend.usage_unit}")
print(f"Headers: {redacted_headers}")
print(f"URL: {builder.url()}")
print("Payload:")
print(json.dumps(builder.to_api_payload(), indent=2))
