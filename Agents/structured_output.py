"""Structured output strategies compatible with Groq tool calling.

Groq's API rejects requests that combine native structured output
(`response_format`) with tool/function calling, so the agents use
`ToolStrategy` (structured output expressed as a tool call).

Two Groq-specific quirks are handled here:

1. Some Groq models emit tool names in lowercase (e.g. ``codingstate``) while
   the structured output tool is registered with the class name (e.g.
   ``CodingState``), which makes Groq reject the call. ``GroqToolStrategy``
   lowercases the structured output tool names so the calls are accepted.
2. LangChain's agent factory forces ``tool_choice="any"`` whenever a
   ``ToolStrategy`` is configured. Groq maps that to ``required`` and then
   rejects answers that contain no tool call, or that call the structured
   output tool with arguments that do not match its schema. ``GroqChatModel``
   drops that forced choice so the model can still call the structured tool
   (the schema stays bound and visible) or answer with JSON text, which
   ``WorkflowGraph._run_agent`` parses as a fallback.
"""

from __future__ import annotations

import re
import time
from typing import Any

from langchain.agents.middleware import AgentMiddleware
from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq


class GroqChatModel(ChatGroq):
    """`ChatGroq` that never forces the model to call a tool.

    LangChain's agent factory sets ``tool_choice="any"`` for agents created with
    a ``ToolStrategy``. Groq maps that to ``tool_choice="required"`` and then
    returns a 400 when the model answers with text or calls the structured
    output tool with arguments Groq considers invalid.

    Dropping the forced choice keeps every tool (including the structured
    output tool) bound, so the model still sees the JSON schema, but lets it
    answer with plain JSON when it prefers not to call a tool.
    """

    def bind_tools(
        self,
        tools: Any,
        *,
        tool_choice: Any = None,
        **kwargs: Any,
    ) -> Any:
        if tool_choice in ("any", "required", True):
            tool_choice = None
        return super().bind_tools(tools, tool_choice=tool_choice, **kwargs)


def _is_groq_structured_output_rejection(exc: Exception) -> bool:
    """Whether Groq rejected the structured-output tool usage itself.

    Covers both cases where the model answers with plain text while a tool call
    is required, and where the model calls the structured output tool with
    arguments that do not match the schema (including a call to a tool that was
    not bound in the request).
    """
    msg = str(exc)
    return (
        "Tool choice is required, but model did not call a tool" in msg
        or "Tool call validation failed" in msg
        or "which was not in request.tools" in msg
    )


_RATE_LIMIT_MARKERS = (
    "rate_limit_exceeded",
    "tokens per minute",
    "tokens per day",
    "Request too large",
)

_RETRY_AFTER_RE = re.compile(r"try again in (?:(\d+)m)?([\d.]+)s")
_LIMIT_DETAIL_RE = re.compile(r"Limit (\d+), (?:Used \d+, )?Requested (\d+)")


def _is_rate_limit_error(exc: Exception) -> bool:
    """Whether the exception is a Groq token limit."""
    msg = str(exc)
    return any(marker in msg for marker in _RATE_LIMIT_MARKERS)


def _is_daily_limit(exc: Exception) -> bool:
    msg = str(exc)
    return "tokens per day" in msg or "(TPD)" in msg


def _retry_after_seconds(exc: Exception) -> float:
    """Seconds Groq asked us to wait, or a conservative default."""
    match = _RETRY_AFTER_RE.search(str(exc))
    if match:
        minutes = int(match.group(1) or 0)
        seconds = float(match.group(2))
        # Add a small buffer so we do not race the rolling window.
        return minutes * 60 + seconds + 1.0
    return 20.0


class GroqRateLimitRetry(AgentMiddleware):
    """Retry Groq token limits instead of failing the agent immediately.

    Groq's on-demand tier has a small tokens-per-minute (TPM) budget and counts
    the requested ``max_tokens`` towards each request. Cases handled:

    - 429 TPM: wait for the delay Groq reports, then retry.
    - 413 "Request too large": shrink ``max_tokens`` by the reported excess and
      retry, so the prompt still fits under the limit.
    - 429 TPD (daily limit): fail fast with a clear message instead of sleeping
      for many minutes.

    The workflow runs several agents back to back, so transient TPM 429s are
    expected even when each individual request is small.
    """

    max_attempts = 6
    min_max_tokens = 512
    max_daily_wait_seconds = 120.0

    def wrap_model_call(self, request, handler):
        for attempt in range(self.max_attempts):
            try:
                return handler(request)
            except Exception as exc:  # noqa: BLE001
                if not _is_rate_limit_error(exc):
                    raise

                if "Request too large" in str(exc):
                    settings = dict(request.model_settings)
                    current = settings.get("max_tokens")
                    if current is None:
                        current = getattr(request.model, "max_tokens", None) or 2048
                    current = int(current)
                    if current <= self.min_max_tokens:
                        raise

                    detail = _LIMIT_DETAIL_RE.search(str(exc))
                    if detail:
                        limit = int(detail.group(1))
                        requested = int(detail.group(2))
                        excess = max(0, requested - limit)
                        new_max = current - excess - 64
                    else:
                        new_max = current // 2
                    new_max = max(self.min_max_tokens, new_max)
                    if new_max >= current:
                        raise

                    settings["max_tokens"] = new_max
                    request = request.override(model_settings=settings)
                    print(
                        "[DevFlow] Groq request too large "
                        f"({str(exc)[:200]}); retrying with "
                        f"max_tokens={new_max}",
                        flush=True,
                    )
                    continue

                delay = _retry_after_seconds(exc)
                if _is_daily_limit(exc) and delay > self.max_daily_wait_seconds:
                    raise RuntimeError(
                        "Groq daily token limit reached. "
                        f"Retry in about {delay / 60:.0f} minutes or upgrade "
                        f"the Groq tier. Details: {str(exc)[:300]}"
                    ) from exc

                if attempt == self.max_attempts - 1:
                    raise
                print(
                    f"[DevFlow] Groq rate limit; retrying in {delay:.1f}s "
                    f"(attempt {attempt + 1}/{self.max_attempts})",
                    flush=True,
                )
                time.sleep(delay)

        raise RuntimeError("Groq rate limit retry loop exhausted")


_FALLBACK_INSTRUCTION = (
    "Do not call any tool. Return the final answer as a single valid JSON "
    "object and nothing else. Do not wrap the JSON in markdown code fences."
)


class GroqToolChoiceFallback(AgentMiddleware):
    """Retry as plain JSON when Groq rejects the structured-output tool call.

    On a structured-output rejection the middleware retries once with the
    structured output removed and the model instructed to answer with JSON
    text. The agent then ends with a text answer, which
    ``WorkflowGraph._run_agent`` parses via ``_extract_json``.

    The instruction is essential: the prompts tell the model to call the
    structured output tool, so without it the retry would keep emitting a call
    to a tool that is no longer bound.
    """

    def wrap_model_call(self, request, handler):
        try:
            return handler(request)
        except Exception as exc:  # noqa: BLE001
            if not _is_groq_structured_output_rejection(exc):
                raise

            system_message = request.system_message
            if system_message is not None and system_message.text:
                content = f"{system_message.text}\n\n{_FALLBACK_INSTRUCTION}"
            else:
                content = _FALLBACK_INSTRUCTION

            return handler(
                request.override(
                    response_format=None,
                    tool_choice=None,
                    tools=[],
                    system_message=SystemMessage(content=content),
                )
            )


class GroqToolStrategy(ToolStrategy):
    """`ToolStrategy` that registers structured output tools with lowercase names."""

    def __init__(self, schema: Any) -> None:
        super().__init__(schema=schema)
        for spec in self.schema_specs:
            spec.name = spec.name.lower()
