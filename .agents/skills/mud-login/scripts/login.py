#!/usr/bin/env python3

"""Narrowly scoped tbaMUD login helper with staged validation."""

from __future__ import annotations

import argparse
import os
import re
import socket
import sys
import time
from dataclasses import dataclass
from typing import Pattern, Sequence


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 4000
DEFAULT_CHARACTER = "UltraMan"
DEFAULT_TIMEOUT = 10.0
ENTER_GAME_CHOICE = "1"

IAC = 255
DO = 253
DONT = 254
WILL = 251
WONT = 252

ANSI_ESCAPE_RE = re.compile(
    rb"""
    \x1B
    (?:
        [@-Z\\-_]
        |
        \[
        [0-?]*
        [ -/]*
        [@-~]
    )
    """,
    re.VERBOSE,
)

NAME_PROMPTS: tuple[Pattern[str], ...] = (
    re.compile(r"by\s+what\s+name", re.IGNORECASE),
    re.compile(r"what\s+is\s+your\s+name", re.IGNORECASE),
    re.compile(r"character(?:\s+name)?\s*[:>]", re.IGNORECASE),
    re.compile(r"(?:^|\n)\s*name\s*[:>]\s*$", re.IGNORECASE),
)

PASSWORD_PROMPTS: tuple[Pattern[str], ...] = (
    re.compile(r"(?:^|\n).*password\s*[:>]\s*$", re.IGNORECASE),
    re.compile(r"enter\s+your\s+password", re.IGNORECASE),
)

PRESS_ENTER_PROMPTS: tuple[Pattern[str], ...] = (
    re.compile(r"press\s+(?:return|enter)", re.IGNORECASE),
)

CHARACTER_MENU_PROMPTS: tuple[Pattern[str], ...] = (
    re.compile(r"make\s+your\s+choice\s*:", re.IGNORECASE),
)

GAME_PROMPTS: tuple[Pattern[str], ...] = (
    re.compile(r"(?:^|\n)[^\n]*>\s*$"),
)

LOGOUT_CONFIRM_PROMPTS: tuple[Pattern[str], ...] = (
    re.compile(r"are\s+you\s+sure", re.IGNORECASE),
    re.compile(r"really\s+quit", re.IGNORECASE),
    re.compile(r"confirm", re.IGNORECASE),
)


class MudSessionError(RuntimeError):
    """Raised when the expected MUD interaction cannot be completed safely."""


@dataclass(frozen=True)
class ReadResult:
    text: str
    matched_pattern: str


class TelnetFilter:
    """Strip basic Telnet negotiation bytes and refuse requested options."""

    def __init__(self) -> None:
        self._pending = bytearray()

    def process(self, sock: socket.socket, data: bytes) -> bytes:
        self._pending.extend(data)
        output = bytearray()
        index = 0

        while index < len(self._pending):
            byte = self._pending[index]

            if byte != IAC:
                output.append(byte)
                index += 1
                continue

            if index + 1 >= len(self._pending):
                break

            command = self._pending[index + 1]

            if command == IAC:
                output.append(IAC)
                index += 2
                continue

            if command in (DO, DONT, WILL, WONT):
                if index + 2 >= len(self._pending):
                    break

                option = self._pending[index + 2]
                response = (
                    bytes((IAC, WONT, option))
                    if command in (DO, DONT)
                    else bytes((IAC, DONT, option))
                )
                sock.sendall(response)
                index += 3
                continue

            index += 2

        del self._pending[:index]
        return bytes(output)


def clean_text(data: bytes) -> str:
    without_ansi = ANSI_ESCAPE_RE.sub(b"", data)
    return without_ansi.decode("utf-8", errors="replace").replace("\r", "")


def send_line(sock: socket.socket, value: str) -> None:
    sock.sendall(value.encode("utf-8") + b"\r\n")


def matches_any(text: str, patterns: Sequence[Pattern[str]]) -> bool:
    return any(pattern.search(text) for pattern in patterns)


class MudClient:
    def __init__(self, host: str, port: int, character: str, timeout: float) -> None:
        self.host = host
        self.port = port
        self.character = character
        self.timeout = timeout
        self.sock: socket.socket | None = None
        self.telnet = TelnetFilter()

    def __enter__(self) -> "MudClient":
        self.connect()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def connect(self) -> None:
        if self.sock is not None:
            raise MudSessionError("A MUD connection is already open.")
        self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self.sock.settimeout(min(1.0, self.timeout))

    def close(self) -> None:
        if self.sock is None:
            return
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()
        self.sock = None

    def require_socket(self) -> socket.socket:
        if self.sock is None:
            raise MudSessionError("No MUD connection is open.")
        return self.sock

    def receive_until(
        self,
        patterns: Sequence[Pattern[str]],
        *,
        timeout: float | None = None,
    ) -> ReadResult:
        sock = self.require_socket()
        effective_timeout = self.timeout if timeout is None else timeout
        deadline = time.monotonic() + effective_timeout
        collected = bytearray()

        while time.monotonic() < deadline:
            remaining = max(0.1, deadline - time.monotonic())
            sock.settimeout(min(1.0, remaining))

            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                continue

            if not chunk:
                text = clean_text(bytes(collected))
                raise MudSessionError(
                    "The MUD closed the connection before the expected prompt. "
                    f"Last received text:\n{text}"
                )

            collected.extend(self.telnet.process(sock, chunk))
            text = clean_text(bytes(collected))

            for pattern in patterns:
                if pattern.search(text):
                    return ReadResult(text=text, matched_pattern=pattern.pattern)

        text = clean_text(bytes(collected))
        raise MudSessionError(
            f"Timed out after {effective_timeout:.1f} seconds waiting for an "
            f"expected prompt. Last received text:\n{text}"
        )

    def wait_for_name_prompt(self) -> ReadResult:
        return self.receive_until(NAME_PROMPTS)

    def send_character(self) -> None:
        send_line(self.require_socket(), self.character)

    def wait_for_password_prompt(self) -> ReadResult:
        return self.receive_until(PASSWORD_PROMPTS)

    def send_password(self, password: str) -> None:
        send_line(self.require_socket(), password)

    def wait_for_post_authentication(self) -> ReadResult:
        return self.receive_until(
            (*PRESS_ENTER_PROMPTS, *CHARACTER_MENU_PROMPTS, *GAME_PROMPTS)
        )

    def reach_character_menu(self, initial: ReadResult) -> ReadResult:
        result = initial
        if matches_any(result.text, PRESS_ENTER_PROMPTS):
            print("Post-authentication PRESS RETURN prompt received.")
            print("Sending exactly one empty Return.")
            send_line(self.require_socket(), "")
            result = self.receive_until((*CHARACTER_MENU_PROMPTS, *GAME_PROMPTS))
        return result

    def enter_game(self, menu_result: ReadResult) -> ReadResult:
        if not matches_any(menu_result.text, CHARACTER_MENU_PROMPTS):
            if matches_any(menu_result.text, GAME_PROMPTS):
                return menu_result
            raise MudSessionError(
                "Expected the character menu before entering the game, "
                "but no recognized menu or in-game prompt was received."
            )

        print("Verified character menu received.")
        print(f"Sending verified Enter-the-game choice: {ENTER_GAME_CHOICE}")
        send_line(self.require_socket(), ENTER_GAME_CHOICE)
        return self.receive_until(GAME_PROMPTS)

    def look(self) -> ReadResult:
        send_line(self.require_socket(), "look")
        return self.receive_until(GAME_PROMPTS)

    def logout(self) -> str:
        sock = self.require_socket()
        send_line(sock, "quit")
        deadline = time.monotonic() + 3.0
        collected = bytearray()
        confirmation_sent = False

        while time.monotonic() < deadline:
            remaining = max(0.1, deadline - time.monotonic())
            sock.settimeout(min(0.5, remaining))

            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                continue

            if not chunk:
                break

            collected.extend(self.telnet.process(sock, chunk))
            text = clean_text(bytes(collected))

            if not confirmation_sent and matches_any(text, LOGOUT_CONFIRM_PROMPTS):
                send_line(sock, "yes")
                confirmation_sent = True

        return clean_text(bytes(collected)).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safely test or run the local tbaMUD login workflow."
    )
    parser.add_argument(
        "--stage",
        choices=("prompt", "username", "menu", "enter", "full"),
        default="full",
        help=(
            "prompt: stop after receiving the name prompt; "
            "username: stop after receiving the password prompt; "
            "menu: authenticate, capture the menu, then disconnect; "
            "enter: select verified menu choice 1, reach the game prompt, "
            "then disconnect without sending game commands; "
            "full: enter the game, run one look command, and quit"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    host = os.environ.get("MUD_HOST", DEFAULT_HOST)
    character = os.environ.get("MUD_CHARACTER", DEFAULT_CHARACTER)
    password = os.environ.get("MUD_PASSWORD")

    try:
        port = int(os.environ.get("MUD_PORT", str(DEFAULT_PORT)))
        timeout = float(os.environ.get("MUD_TIMEOUT", str(DEFAULT_TIMEOUT)))
    except ValueError as exc:
        print(f"CONFIGURATION_ERROR: Invalid port or timeout: {exc}", file=sys.stderr)
        return 6

    if args.stage in ("menu", "enter", "full") and not password:
        print(
            "ERROR: MUD_PASSWORD is not set. Set it in the shell before starting Codex.",
            file=sys.stderr,
        )
        return 2

    try:
        print(f"Connecting to {host}:{port}...")

        with MudClient(host=host, port=port, character=character, timeout=timeout) as client:
            print("TCP connection established.")
            client.wait_for_name_prompt()
            print("Character-name prompt received.")

            if args.stage == "prompt":
                print("Prompt-stage test completed; disconnecting.")
                return 0

            print(f"Sending character name: {character}")
            client.send_character()
            client.wait_for_password_prompt()
            print("Password prompt received.")

            if args.stage == "username":
                print("Username-stage test completed; disconnecting.")
                return 0

            assert password is not None
            print("Sending configured password.")
            client.send_password(password)

            post_auth = client.wait_for_post_authentication()
            menu_or_game = client.reach_character_menu(post_auth)

            if args.stage == "menu":
                print("\n--- POST-AUTHENTICATION OUTPUT ---")
                print(post_auth.text.strip())
                print("--- END POST-AUTHENTICATION OUTPUT ---\n")

                if menu_or_game.text != post_auth.text:
                    print("--- AFTER RETURN ---")
                    print(menu_or_game.text.strip())
                    print("--- END AFTER RETURN ---")

                if matches_any(menu_or_game.text, CHARACTER_MENU_PROMPTS):
                    print("Character menu received; no menu choice was sent.")
                else:
                    print("No character menu was detected.")

                print("Menu-stage test completed; disconnecting.")
                return 0

            game_result = client.enter_game(menu_or_game)

            if args.stage == "enter":
                print("\n--- IN-GAME ENTRY OUTPUT ---")
                print(game_result.text.strip())
                print("--- END IN-GAME ENTRY OUTPUT ---\n")
                print(
                    "Enter-stage test completed; no look, quit, movement, "
                    "or other game command was sent. Disconnecting."
                )
                return 0

            print("Login and game entry succeeded.")
            print("Sending exactly one `look` command.")
            look_result = client.look()

            print("\n--- CURRENT ROOM ---")
            print(look_result.text.strip())
            print("--- END CURRENT ROOM ---\n")

            print("Sending `quit`.")
            logout_text = client.logout()

            if logout_text:
                print("--- LOGOUT RESPONSE ---")
                print(logout_text)
                print("--- END LOGOUT RESPONSE ---")

            print("Logout completed; connection closed.")
            return 0

    except PermissionError as exc:
        print(
            "NETWORK_PERMISSION_REQUIRED: The execution sandbox blocked the "
            f"connection to {host}:{port}: {exc}",
            file=sys.stderr,
        )
        return 3
    except (ConnectionRefusedError, TimeoutError, socket.timeout) as exc:
        print(
            f"CONNECTION_ERROR: Could not connect to {host}:{port}: {exc}",
            file=sys.stderr,
        )
        return 4
    except MudSessionError as exc:
        print(f"SESSION_ERROR: {exc}", file=sys.stderr)
        return 5
    except OSError as exc:
        print(f"SOCKET_ERROR: {exc}", file=sys.stderr)
        return 7


if __name__ == "__main__":
    raise SystemExit(main())
