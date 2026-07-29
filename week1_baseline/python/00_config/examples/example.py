import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from boukensha import Config, Player


os.environ.setdefault("BOUKENSHA_DIR", str(Path(__file__).resolve().parents[3] / ".boukensha"))
config = Config()
player_settings = config.tasks("player") or {}

print("=== Boukensha Step 0: Configuration ===\n")
print(f"Config dir:     {config.dir}")
print(f"Tasks:          {', '.join(config.tasks().keys())}\n")
print("-- player task --")
print(f"Provider:       {Player.provider(player_settings)}")
print(f"Model:          {Player.model(player_settings)}")
print(f"Prompt override?{Player.prompt_override(player_settings)}")
prompt = Player.system_prompt(player_settings, user_prompts_dir=config.user_prompts_dir,
                              default_prompts_dir=Config.PROMPTS_DIR)
print(f"System prompt:  {prompt[:60] if prompt else prompt}...\n")
print(f"MUD host:       {config.mud_host}:{config.mud_port}")
print(f"MUD user:       {config.mud_username}\n")
print(f"API key set?    {os.environ.get('OPENAI_API_KEY') is not None}\n")
print(config)
