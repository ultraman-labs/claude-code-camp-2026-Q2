from __future__ import annotations

import re
import socket
import threading
import time
from dataclasses import dataclass


class SessionError(Exception):
    pass


class ConnectionError(SessionError):
    pass


class LoginError(SessionError):
    pass


class TimeoutError(SessionError):
    pass


IAC, DONT, DO, WONT, WILL, SB, SE = 255, 254, 253, 252, 251, 250, 240


class Session:
    PROMPT_SENTINEL = "> "

    def __init__(self, host: str = "localhost", port: int = 4000, timeout: float = 10.0, sock: object | None = None) -> None:
        self.host, self.port, self.timeout = host, int(port), timeout
        self._socket = sock
        self._closed = sock is None
        self._buffer = bytearray()
        self._condition = threading.Condition()
        self._reader: threading.Thread | None = None
        self._last_received: float | None = None

    def open(self) -> "Session":
        if self._socket is not None and not self._closed:
            raise SessionError("already open")
        try:
            self._socket = socket.create_connection((self.host, self.port), timeout=self.timeout)
        except OSError as exc:
            raise ConnectionError(f"connect {self.host}:{self.port} failed: {exc}") from exc
        self._closed = False
        self._start_reader()
        return self

    connect = open

    def open_(self) -> bool:
        return self.is_open()

    def is_open(self) -> bool:
        return self._socket is not None and not self._closed

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            if self._socket is not None:
                self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
        except OSError:
            pass
        if self._reader is not None and self._reader is not threading.current_thread():
            self._reader.join(timeout=1)
        self._socket = None
        self._reader = None
        with self._condition:
            self._condition.notify_all()

    def send_command(self, command: object) -> str:
        if not self.is_open():
            raise SessionError("session not open")
        line = "" if command in ("", "\r", "\n") else getattr(command, "raw", str(command))
        self._socket.sendall((line + "\r\n").encode())
        return line

    send = send_command

    def drain(self) -> str:
        with self._condition:
            data = bytes(self._buffer)
            self._buffer.clear()
            return data.decode(errors="replace")

    def read_until(self, pattern: str | re.Pattern[str], timeout: float | None = None) -> str:
        if not self.is_open():
            raise SessionError("session not open")
        regex = pattern if hasattr(pattern, "search") else re.compile(re.escape(str(pattern)))
        deadline = time.monotonic() + (self.timeout if timeout is None else timeout)
        with self._condition:
            while True:
                text = bytes(self._buffer).decode(errors="replace")
                match = regex.search(text)
                if match:
                    end = match.end()
                    result = text[:end]
                    del self._buffer[:len(text[:end].encode())]
                    return result
                remaining = deadline - time.monotonic()
                if self._closed:
                    raise ConnectionError("socket closed while waiting")
                if remaining <= 0:
                    raise TimeoutError(f"read_until {pattern!r} timed out")
                self._condition.wait(remaining)

    def read_until_prompt(self, timeout: float | None = None) -> str:
        try:
            return self.read_until(self.PROMPT_SENTINEL, timeout=timeout)
        except TimeoutError:
            return self.drain()

    def read_until_quiet(self, quiet_seconds: float = 1.0, timeout: float | None = None) -> str:
        if not self.is_open():
            raise SessionError("session not open")
        deadline = time.monotonic() + (self.timeout if timeout is None else timeout)
        with self._condition:
            while True:
                now = time.monotonic()
                if self._buffer and self._last_received is not None and now - self._last_received >= quiet_seconds:
                    return self._take_buffer()
                remaining = deadline - now
                if remaining <= 0:
                    return self._take_buffer()
                self._condition.wait(min(remaining, quiet_seconds))

    def login(self, username: str, password: str) -> str:
        self.read_until(re.compile(r"By what name do you wish to be known.*\?", re.I))
        self.send_command(username)
        self.read_until(re.compile(r"Password", re.I))
        self.send_command(password)
        output = self.read_until(re.compile(r"Welcome|Reconnecting|Wrong password", re.I))
        if re.search("Wrong password", output, re.I):
            raise LoginError("wrong password")
        if re.search("Welcome", output, re.I):
            self.send_command("")
            self.send_command("1")
            self.read_until_quiet()
        return output

    def _take_buffer(self) -> str:
        data = bytes(self._buffer)
        self._buffer.clear()
        return data.decode(errors="replace")

    def _start_reader(self) -> None:
        self._reader = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader.start()

    def _reader_loop(self) -> None:
        try:
            while not self._closed:
                chunk = self._socket.recv(4096)
                if not chunk:
                    break
                filtered = _strip_iac(chunk)
                if filtered:
                    with self._condition:
                        self._buffer.extend(filtered)
                        self._last_received = time.monotonic()
                        self._condition.notify_all()
        except (OSError, EOFError):
            pass
        finally:
            self._closed = True
            with self._condition:
                self._condition.notify_all()


def _strip_iac(data: bytes) -> bytes:
    out, i = bytearray(), 0
    while i < len(data):
        if data[i] != IAC:
            out.append(data[i]); i += 1; continue
        if i + 1 >= len(data): break
        command = data[i + 1]
        if command == IAC:
            out.append(IAC); i += 2
        elif command in (DO, DONT, WILL, WONT):
            i += 3
        elif command == SB:
            i += 2
            while i + 1 < len(data) and not (data[i] == IAC and data[i + 1] == SE): i += 1
            i += 2
        else:
            i += 2
    return bytes(out)
