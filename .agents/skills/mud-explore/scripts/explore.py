#!/usr/bin/env python3
"""One-command, read-only tbaMUD exploration client."""
from __future__ import annotations

import argparse
import os
import re
import socket
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../mud-login/scripts")))
from login import (  # noqa: E402
    CHARACTER_MENU_PROMPTS, GAME_PROMPTS, LOGOUT_CONFIRM_PROMPTS,
    MudClient, MudSessionError, PRESS_ENTER_PROMPTS, matches_any, send_line,
)

READ_ONLY = {"look", "examine", "help", "commands", "who", "users", "score",
             "exits", "inventory", "equipment", "gold", "time", "weather",
             "levels", "where", "version", "credits", "news", "info", "motd",
             "policies", "whoami"}
MOVEMENT = {"north", "east", "south", "west", "up", "down"}
FORBIDDEN = {"attack", "kill", "hit", "murder", "bash", "kick", "backstab",
             "rescue", "assist", "flee", "buy", "sell", "value", "offer", "get",
             "take", "drop", "give", "put", "wear", "wield", "hold", "grab",
             "remove", "eat", "drink", "taste", "sip", "cast", "practice", "save",
             "title", "display", "wimpy", "toggle", "wizlist", "immlist", "shutdown",
             "delete", "set", "snoop", "force", "load", "restore", "purge"}
COMBAT = re.compile(r"you are fighting|killing blow|you flee|attacks you|hits you", re.I)
PAGER = re.compile(r"\[ Return to continue.*?\]", re.I | re.S)

def validate(command: str) -> str:
    parts = command.strip().split()
    if not parts or len(command) > 120:
        raise ValueError("exactly one non-empty command is required")
    verb = parts[0].lower()
    if verb in FORBIDDEN or verb not in READ_ONLY | MOVEMENT:
        raise ValueError(f"command is not permitted in exploration mode: {verb}")
    if verb in MOVEMENT and len(parts) != 1:
        raise ValueError("movement commands take no arguments")
    if verb in {"score", "exits", "inventory", "equipment", "gold", "time", "weather",
                "levels", "where", "who", "users", "version", "credits", "news",
                "info", "motd", "policies", "whoami", "commands"} and len(parts) > 2:
        raise ValueError("this informational command accepts at most one argument")
    return " ".join(parts)

def receive_command(client: MudClient) -> str:
    """Collect a command response, advancing only the server's pager."""
    chunks = []
    while True:
        result = client.receive_until((*GAME_PROMPTS, PAGER))
        chunks.append(result.text)
        if not PAGER.search(result.text):
            return "".join(chunks)
        send_line(client.require_socket(), "")

def main() -> int:
    parser = argparse.ArgumentParser(description="Send one safe, model-selected tbaMUD command.")
    parser.add_argument("--command", required=True)
    args = parser.parse_args()
    command = validate(args.command)
    password = os.environ.get("MUD_PASSWORD")
    if not password:
        print("ERROR: MUD_PASSWORD is not set.", file=sys.stderr); return 2
    host = os.environ.get("MUD_HOST", "localhost")
    port = int(os.environ.get("MUD_PORT", "4000"))
    timeout = float(os.environ.get("MUD_TIMEOUT", "10"))
    try:
        with MudClient(host, port, "UltraMan", timeout) as client:
            client.wait_for_name_prompt(); client.send_character()
            client.wait_for_password_prompt(); client.send_password(password)
            post = client.wait_for_post_authentication()
            menu = post
            if matches_any(menu.text, PRESS_ENTER_PROMPTS):
                send_line(client.require_socket(), "")
                menu = client.receive_until((*CHARACTER_MENU_PROMPTS, *GAME_PROMPTS))
            if matches_any(menu.text, CHARACTER_MENU_PROMPTS):
                send_line(client.require_socket(), "1")
                client.receive_until(GAME_PROMPTS)
            elif not matches_any(menu.text, GAME_PROMPTS):
                raise MudSessionError("unexpected post-authentication state")
            send_line(client.require_socket(), command)
            result = receive_command(client)
            if COMBAT.search(result):
                raise MudSessionError("combat-like output detected; exploration stopped")
            print(result.strip())
            client.logout()
        return 0
    except (ValueError, OSError, socket.timeout, MudSessionError) as exc:
        print(f"EXPLORATION_ERROR: {exc}", file=sys.stderr); return 1

if __name__ == "__main__":
    raise SystemExit(main())
