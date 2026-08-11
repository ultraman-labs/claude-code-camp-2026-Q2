from __future__ import annotations

from typing import Any, Mapping

from .errors import ApiError
from .logger import Logger


class Agent:
    """Run one bounded model/tool turn."""

    MAX_ITERATIONS = 25
    WRAP_UP_OUTPUT_TOKENS = 400
    WRAP_UP_DIRECTIVE = (
        "You have reached your action limit for this turn. Do not call any more tools.\n"
        "Briefly summarize what you accomplished, what is still unfinished, and the\n"
        "single next action you would take."
    )

    def __init__(
        self,
        context: Any,
        registry: Any,
        builder: Any,
        client: Any,
        logger: Any = None,
        task_settings: Any = None,
        max_iterations: Any = None,
        max_output_tokens: Any = None,
    ) -> None:
        self._context = context
        self._registry = registry
        self._builder = builder
        self._client = client
        self._logger = Logger() if logger is None else logger
        self._max_iterations = self._resolve_max_iterations(task_settings, max_iterations)
        self._max_output_tokens = self._resolve_max_output_tokens(task_settings, max_output_tokens)
        self._iteration = 0

    def run(self) -> str:
        while True:
            if self._iteration_limit_reached():
                self._logger.limit_reached(
                    kind="max_iterations",
                    n=self._iteration,
                    max=self._max_iterations,
                )
                return self._wrap_up("max_iterations")

            self._iteration += 1
            print(f"[iteration {self._iteration}/{self._max_iterations}]")

            self._logger.iteration(n=self._iteration, max=self._max_iterations)
            self._logger.prompt(
                messages=self._context.messages,
                tools=self._context.tools,
            )
            response = self._client.call(**self._call_options())
            self._logger.raw(data=response)
            parsed = self._builder.parse_response(response)

            if parsed["stop_reason"] == "tool_use":
                self._handle_tool_calls(parsed["content"], response)
            else:
                text = self._extract_text(parsed["content"])
                self._log_response(text, response)
                self._logger.turn_end(reason="completed", iterations=self._iteration)
                return text

    def _resolve_max_iterations(self, task_settings: Any, explicit: Any) -> int:
        if explicit is not None:
            return int(explicit)

        task = getattr(self._context, "task", None)
        resolver = getattr(task, "max_iterations", None)
        if task_settings is not None and callable(resolver):
            return int(resolver(task_settings))

        return self.MAX_ITERATIONS

    def _resolve_max_output_tokens(self, task_settings: Any, explicit: Any) -> Any:
        if explicit is not None:
            return explicit

        task = getattr(self._context, "task", None)
        resolver = getattr(task, "max_output_tokens", None)
        if task_settings is not None and callable(resolver):
            return resolver(task_settings)

        return None

    def _iteration_limit_reached(self) -> bool:
        return self._max_iterations > 0 and self._iteration >= self._max_iterations

    def _call_options(self) -> dict[str, Any]:
        if self._max_output_tokens:
            return {"max_output_tokens": self._max_output_tokens}
        return {}

    def _wrap_up(self, reason: str) -> str:
        self._context.add_message("user", self.WRAP_UP_DIRECTIVE)
        try:
            response = self._client.call(
                tools=[],
                max_output_tokens=self.WRAP_UP_OUTPUT_TOKENS,
            )
            parsed = self._builder.parse_response(response)
            text = self._extract_text(parsed["content"])
            text = text if text.strip() else self._fallback_message(reason)
            self._log_response(text, response)
            self._logger.turn_end(reason=reason, iterations=self._iteration)
            return text
        except ApiError:
            text = self._fallback_message(reason)
            self._logger.turn_end(reason=reason, iterations=self._iteration)
            return text

    def _fallback_message(self, reason: str) -> str:
        return (
            f"I reached my {self._max_iterations}-action limit for this turn before "
            f"finishing ({reason}). Ask me to continue and I'll pick up from here."
        )

    @staticmethod
    def _extract_text(content: list[Mapping[str, Any]]) -> str:
        return "".join(
            block["text"]
            for block in content
            if block.get("type") == "text"
        )

    def _handle_tool_calls(
        self,
        content: list[Mapping[str, Any]],
        response: Any,
    ) -> None:
        tool_calls = [
            block for block in content if block.get("type") == "tool_use"
        ]
        reasoning = self._extract_text(content)
        text = reasoning.strip()
        if not text:
            count = len(tool_calls)
            suffix = "" if count == 1 else "s"
            text = f"(tool use — {count} call{suffix})"
        self._log_response(text, response)

        self._context.add_message("assistant", content)

        for block in tool_calls:
            name = block["name"]
            args = block.get("input", {})
            tool_use_id = block.get("id")

            print(f"  tool call → {name}({args})")
            self._logger.tool_call(name=name, args=args)
            try:
                result = self._registry.dispatch(name, args)
                self._logger.tool_result(name=name, result=result, ok=True)
            except Exception as error:
                result = f"ERROR: {type(error).__name__}: {error}"
                self._logger.tool_result(
                    name=name,
                    result=result,
                    ok=False,
                    error=str(error),
                )
            print(f"  tool result → {str(result)[:61]}")
            self._context.add_message("tool_result", str(result), tool_use_id=tool_use_id)

    def _log_response(self, text: str, response: Any) -> None:
        self._logger.response(
            text=text,
            usage=self._normalized_usage(response),
            stop_reason=response.get("stop_reason"),
            task=self._context.task.task_name(),
            backend=self._builder.backend,
        )

    @staticmethod
    def _normalized_usage(response: Mapping[str, Any]) -> Any:
        if response.get("usage"):
            return response["usage"]
        if response.get("usageMetadata"):
            return response["usageMetadata"]

        usage = {
            key: response[key]
            for key in ("prompt_eval_count", "eval_count")
            if key in response
        }
        return usage or None
