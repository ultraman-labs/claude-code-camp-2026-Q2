from __future__ import annotations

import json
import re
import socket
import ssl
import time
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .errors import ApiError


class Client:
    RETRYABLE_STATUS_CODES = {408, 409, 429, 500, 502, 503, 504}
    MAX_ATTEMPTS = 3
    TIMEOUT_SECONDS = 30
    MAX_WAIT_SECONDS = 5
    BASE_RETRY_DELAY = 0.5

    def __init__(self, builder: Any) -> None:
        self.builder = builder

    def call(self, max_output_tokens: int = 1024, tools: Any = None) -> Any:
        payload = json.dumps(
            self.builder.to_api_payload(
                max_output_tokens=max_output_tokens,
                tools=tools,
            )
        ).encode("utf-8")
        request_headers = dict(self.builder.headers())
        request_headers.setdefault("Content-Type", "application/json")
        request = Request(self.builder.url(), data=payload, headers=request_headers, method="POST")
        context = ssl.create_default_context()

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                with urlopen(request, timeout=self.TIMEOUT_SECONDS, context=context) as response:
                    body = response.read()
                try:
                    return json.loads(body)
                except json.JSONDecodeError as exc:
                    raise ApiError(
                        f"API response JSON was malformed on attempt {attempt}: {self._safe_detail(body)}"
                    ) from exc
            except HTTPError as exc:
                detail = self._safe_detail(exc.read())
                if exc.code == 401:
                    raise ApiError(
                        "authentication failed (401) — check your API key"
                    ) from exc
                if exc.code not in self.RETRYABLE_STATUS_CODES or attempt == self.MAX_ATTEMPTS:
                    raise ApiError(f"API request failed with HTTP {exc.code} on attempt {attempt}: {detail}") from exc
                self._wait(attempt, exc.headers.get("Retry-After"))
            except (TimeoutError, socket.timeout, ConnectionError, URLError, ssl.SSLError, EOFError) as exc:
                if attempt == self.MAX_ATTEMPTS:
                    raise ApiError(f"API request failed on attempt {attempt}: {type(exc).__name__}: {exc}") from exc
                self._wait(attempt, None)

        raise ApiError("API request failed without a response")

    def _wait(self, attempt: int, retry_after: str | None) -> None:
        delay = self.BASE_RETRY_DELAY * (2 ** (attempt - 1))
        if retry_after:
            try:
                delay = max(0.0, float(retry_after))
            except ValueError:
                try:
                    delay = max(0.0, (parsedate_to_datetime(retry_after).timestamp() - time.time()))
                except (TypeError, ValueError, OverflowError):
                    pass
        time.sleep(min(delay, self.MAX_WAIT_SECONDS))

    @staticmethod
    def _safe_detail(body: bytes | str, limit: int = 512) -> str:
        detail = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else str(body)
        detail = re.sub(r"(?i)(bearer\s+)[^\s,}\"]+", r"\1[redacted]", detail)
        detail = re.sub(r'(?i)(authorization|api[_-]?key|x-api-key|x-goog-api-key)([\"\']?\s*[=:]\s*[\"\']?)[^,}\"\'\s]+', r"\1\2[redacted]", detail)
        return detail[:limit]
