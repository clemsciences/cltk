"""Anthropic (Claude) integration for CLTK.

Based on https://platform.claude.com/docs/en/api/messages.

# Internal; no stability guarantees

This module provides a small wrapper class (:class:`AnthropicConnection`) around
the Anthropic client and high‑level helpers to generate linguistic annotations
from LLMs for a given language (resolved by Glottolog ID).
"""

__license__ = "MIT License. See LICENSE."

# NOTE: Keep Anthropic/LLM behavior aligned with LLM_DEV_GUIDE.md (prompts,
# logging, retries, and safety).

import os
import re
from typing import Any, Optional, cast

from cltk.core.cltk_logger import bind_context
from cltk.core.data_types import AVAILABLE_ANTHROPIC_MODELS, CLTKGenAIResponse
from cltk.core.exceptions import AnthropicInferenceError, CLTKException
from cltk.text.utils import cltk_normalize
from cltk.utils.utils import load_env_file

# Claude Opus 4.7 and later reject sampling parameters (``temperature``) and
# use adaptive thinking; older model families (Sonnet 4.6, Haiku 4.5) still
# accept ``temperature``.
_MODELS_WITHOUT_SAMPLING_PREFIXES: tuple[str, ...] = (
    "claude-opus-4-7",
    "claude-opus-4-8",
    "claude-fable",
    "claude-mythos",
)


class _AnthropicErrorFallback(Exception):
    """Fallback error raised when the Anthropic SDK is unavailable."""


def _resolve_anthropic_classes() -> (
    tuple[Optional[type[Any]], Optional[type[Any]], type[BaseException]]
):
    """Import Anthropic client classes lazily, tolerating missing optional deps."""
    sync_cls: Optional[type[Any]]
    async_cls: Optional[type[Any]]
    error_cls: type[BaseException]

    try:
        from anthropic import Anthropic as imported_sync
    except Exception:  # pragma: no cover - optional dependency
        sync_cls = None
    else:
        sync_cls = imported_sync

    try:
        from anthropic import AsyncAnthropic as imported_async
    except Exception:  # pragma: no cover - optional dependency
        async_cls = None
    else:
        async_cls = imported_async

    try:
        from anthropic import APIError as imported_error
    except Exception:  # pragma: no cover - optional dependency
        error_cls = _AnthropicErrorFallback
    else:
        error_cls = imported_error

    return sync_cls, async_cls, error_cls


Anthropic, AsyncAnthropic, AnthropicAPIError = _resolve_anthropic_classes()


def _build_message_params(
    model: str, prompt: str, max_tokens: int, temperature: float
) -> dict[str, Any]:
    """Build keyword arguments for ``client.messages.create()``.

    Claude Opus 4.7+ rejects ``temperature`` (HTTP 400); for those models
    adaptive thinking is requested instead. Older models receive the explicit
    ``temperature`` and no ``thinking`` configuration.
    """
    params: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if model.startswith(_MODELS_WITHOUT_SAMPLING_PREFIXES):
        params["thinking"] = {"type": "adaptive"}
    else:
        params["temperature"] = temperature
    return params


def _anthropic_response_text(response: Any) -> str:
    """Concatenate the text blocks of an Anthropic Messages API response."""
    parts: list[str] = []
    for block in getattr(response, "content", None) or []:
        if getattr(block, "type", None) == "text":
            parts.append(getattr(block, "text", "") or "")
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(str(block.get("text") or ""))
    return "".join(parts)


class AnthropicConnection:
    """Thin wrapper around the Anthropic client for CLTK use cases.

    Args:
      model: Small set of supported model aliases.
      api_key: Anthropic API key. Falls back to ``ANTHROPIC_API_KEY``.
      temperature: Sampling temperature (default 1.0). Only sent to models
        that still accept sampling parameters (not Claude Opus 4.7+).
      max_tokens: Maximum output tokens per request (default 16000).

    Attributes:
      client: Anthropic client instance.

    """

    def __init__(
        self,
        model: AVAILABLE_ANTHROPIC_MODELS,
        api_key: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: int = 16000,
    ):
        """Initialize the client and resolve language/dialect metadata."""
        self.api_key = api_key
        self.model: str = model
        self.temperature: float = temperature
        self.max_tokens: int = max_tokens
        if not self.api_key:
            load_env_file()
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            msg: str = "ANTHROPIC_API_KEY not found. Please set it in your environment or in a .env file."
            # Bind with model context even before self.log is available
            bind_context(model=str(model)).error(msg)
            raise ValueError(msg)
        # Use patched Anthropic if provided by tests; else import lazily
        anthropic_cls = Anthropic
        if anthropic_cls is None:  # pragma: no cover - import only if needed
            try:
                from anthropic import Anthropic as runtime_anthropic
            except Exception as e:
                raise ImportError(
                    "Anthropic client not installed. Install with: pip install 'cltk[anthropic]'"
                ) from e
            anthropic_cls = runtime_anthropic
        self.client = anthropic_cls(api_key=self.api_key)
        # Structured logger bound with model identifier
        self.log = bind_context(model=str(self.model))

    def generate(
        self,
        prompt: str,
        max_retries: int = 2,
    ) -> CLTKGenAIResponse:
        """Call the Anthropic Messages API synchronously with retries and code-block parsing."""
        # Avoid logging full prompt contents unless explicitly enabled
        import os as _os

        if _os.getenv("CLTK_LOG_CONTENT", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }:
            self.log.debug(prompt)
        code_block: Optional[str] = None
        anthropic_response: Optional[Any] = None
        attempt: Optional[int] = None
        response_text: str = ""
        # Accumulate tokens across attempts (including failed ones)
        agg_tokens: dict[str, int] = {"input": 0, "output": 0, "total": 0}
        for attempt in range(1, max_retries + 1):
            self.log.debug(f"Attempt {attempt} of {max_retries}")
            try:
                anthropic_response = self.client.messages.create(
                    **_build_message_params(
                        model=self.model,
                        prompt=prompt,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                    )
                )
            except AnthropicAPIError as anthropic_error:
                raise AnthropicInferenceError(
                    f"An error from Anthropic occurred: {anthropic_error}"
                )
            # Check stop_reason before reading content; safety classifiers can
            # decline a request with an HTTP 200 and empty/partial content.
            if getattr(anthropic_response, "stop_reason", None) == "refusal":
                raise AnthropicInferenceError(
                    "Anthropic declined the request (stop_reason='refusal')."
                )
            response_text = _anthropic_response_text(anthropic_response)
            if _os.getenv("CLTK_LOG_CONTENT", "").strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }:
                self.log.debug(f"Raw response from Anthropic: {response_text}")
            # Add usage from this attempt even if parsing fails
            try:
                tok = self._anthropic_response_tokens(anthropic_response)
                for k in ("input", "output", "total"):
                    agg_tokens[k] += tok.get(k, 0)
            except Exception:
                pass
            try:
                code_block = self._extract_code_blocks(text=response_text)
            except Exception as e:
                self.log.error(f"Error extracting code block: {e}")
                continue
            if code_block:
                break  # Success, exit retry loop
            else:
                self.log.warning(
                    f"Attempt {attempt}: No code block found in Anthropic response. Retrying..."
                )
                if attempt == max_retries:
                    final_err = (
                        "No code blocks found in Anthropic response after retries."
                    )
                    self.log.error(final_err)
                    raise CLTKException(final_err)
        assert anthropic_response
        # Use the accumulated usage across all attempts
        anthropic_usage: dict[str, int] = agg_tokens
        raw_anthropic_response_normalized: str = cltk_normalize(text=response_text)
        if _os.getenv("CLTK_LOG_CONTENT", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }:
            self.log.debug(
                f"raw_anthropic_response_normalized:\n{raw_anthropic_response_normalized}"
            )
        self.log.debug(f"Completed generation() after {attempt} attempts")
        return CLTKGenAIResponse(
            response=raw_anthropic_response_normalized, usage=anthropic_usage
        )

    def _anthropic_response_tokens(self, response: Any) -> dict[str, int]:
        """Extract token usage information from an Anthropic response.

        Args:
          response: Anthropic response object.

        Returns:
          A dict with ``input``, ``output``, and ``total`` token counts (0 if
          unavailable).

        """
        usage = getattr(response, "usage", None)
        tokens: dict[str, int] = {"input": 0, "output": 0, "total": 0}
        if not usage:
            self.log.warning(
                "No usage information found in response. Tokens used may not be available."
            )
            self.log.info(f"Anthropic usage: {tokens}")
            return tokens

        def _get(u: object, *names: str) -> int:
            """Attempt to read an integer field from a response usage object."""
            for nm in names:
                if hasattr(u, nm):
                    try:
                        return int(getattr(u, nm) or 0)
                    except Exception:
                        pass
                if isinstance(u, dict):
                    ud = cast(dict[str, Any], u)
                    if nm in ud:
                        try:
                            return int(ud.get(nm) or 0)
                        except Exception:
                            pass
            return 0

        tokens["input"] = _get(usage, "input_tokens", "prompt_tokens")
        tokens["output"] = _get(usage, "output_tokens", "completion_tokens")
        # The Anthropic API does not report a total; derive it
        tokens["total"] = _get(usage, "total_tokens") or (
            tokens["input"] + tokens["output"]
        )

        if tokens["total"] == 0:
            self.log.warning(
                "No tokens used reported in response. This may indicate an issue with the API call."
            )
        self.log.info(f"Anthropic usage: {tokens}")
        return tokens

    def _extract_code_blocks(self, text: str) -> str:
        """Return the first fenced code block from an Anthropic response string."""
        # This regex finds all text between triple backticks
        code_blocks: list[str] = re.findall(
            r"```(?:[a-zA-Z]*\n)?(.*?)```", text, re.DOTALL
        )
        if not code_blocks:
            return ""
        code_block: str = code_blocks[0].strip()
        import os as _os

        if _os.getenv("CLTK_LOG_CONTENT", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }:
            self.log.debug(f"Extracted code block:\n{code_block}")
        return code_block


class AsyncAnthropicConnection:
    """Asynchronous variant of :class:`AnthropicConnection`.

    Provides an ``async`` ``generate_async()`` method and uses the
    ``AsyncAnthropic`` client under the hood. Mirrors the behavior and logging
    of the synchronous client while enabling concurrent requests.

    Args:
      model: Model alias to use (see ``AVAILABLE_ANTHROPIC_MODELS``).
      api_key: Optional Anthropic API key. Falls back to ``ANTHROPIC_API_KEY``.
      temperature: Sampling temperature for generation. Only sent to models
        that still accept sampling parameters (not Claude Opus 4.7+).
      max_tokens: Maximum output tokens per request (default 16000).

    """

    def __init__(
        self,
        model: AVAILABLE_ANTHROPIC_MODELS,
        api_key: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: int = 16000,
    ) -> None:
        self.api_key = api_key
        self.model: str = model
        self.temperature: float = temperature
        self.max_tokens: int = max_tokens
        if not self.api_key:
            load_env_file()
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            msg: str = "ANTHROPIC_API_KEY not found. Please set it in your environment or in a .env file."
            bind_context(model=str(model)).error(msg)
            raise ValueError(msg)
        async_anthropic_cls = AsyncAnthropic
        if async_anthropic_cls is None:  # pragma: no cover - import only if needed
            try:
                from anthropic import AsyncAnthropic as runtime_async_anthropic
            except Exception as e:
                raise ImportError(
                    "Anthropic client not installed. Install with: pip install 'cltk[anthropic]'"
                ) from e
            async_anthropic_cls = runtime_async_anthropic
        self.client = async_anthropic_cls(api_key=self.api_key)
        # Structured logger bound with model identifier
        self.log = bind_context(model=str(self.model))

    async def generate_async(
        self,
        prompt: str,
        max_retries: int = 2,
    ) -> CLTKGenAIResponse:
        """Call the Anthropic Messages API asynchronously with retries."""
        import os as _os

        if _os.getenv("CLTK_LOG_CONTENT", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }:
            self.log.debug("[async] Prompt being sent to Anthropic:\n%s", prompt)
        code_block: Optional[str] = None
        anthropic_response: Optional[Any] = None
        response_text: str = ""
        agg_tokens: dict[str, int] = {"input": 0, "output": 0, "total": 0}
        for attempt in range(1, max_retries + 1):
            self.log.debug("[async] Attempt %s of %s", attempt, max_retries)
            try:
                anthropic_response = await self.client.messages.create(
                    **_build_message_params(
                        model=self.model,
                        prompt=prompt,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                    )
                )
            except AnthropicAPIError as anthropic_error:
                self.log.error(
                    "[async] Anthropic error on attempt %s: %s",
                    attempt,
                    anthropic_error,
                )
                if attempt == max_retries:
                    raise AnthropicInferenceError(
                        f"An error from Anthropic occurred: {anthropic_error}"
                    )
                continue
            if getattr(anthropic_response, "stop_reason", None) == "refusal":
                raise AnthropicInferenceError(
                    "Anthropic declined the request (stop_reason='refusal')."
                )
            response_text = _anthropic_response_text(anthropic_response)
            if _os.getenv("CLTK_LOG_CONTENT", "").strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }:
                self.log.debug("[async] Raw response from Anthropic: %s", response_text)
            # Track usage for this attempt (even if parsing fails)
            try:
                tok = self._anthropic_response_tokens(anthropic_response)
                for k in ("input", "output", "total"):
                    agg_tokens[k] += tok.get(k, 0)
            except Exception:
                pass
            try:
                code_block = self._extract_code_blocks(response_text)
            except Exception as e:  # pragma: no cover - defensive
                self.log.error("[async] Error extracting code block: %s", e)
                code_block = None
            if code_block:
                break
            self.log.warning(
                "[async] Attempt %s: No code block found in response. Retrying...",
                attempt,
            )
            if attempt == max_retries:
                final_err = "No code blocks found in Anthropic response after retries."
                self.log.error(final_err)
                raise CLTKException(final_err)

        assert anthropic_response is not None
        usage = agg_tokens
        raw_normalized: str = cltk_normalize(text=response_text)
        if _os.getenv("CLTK_LOG_CONTENT", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }:
            self.log.debug("[async] Normalized output text:\n%s", raw_normalized)
        return CLTKGenAIResponse(response=raw_normalized, usage=usage)

    def _anthropic_response_tokens(self, response: Any) -> dict[str, int]:
        """Extract token usage fields from an async Anthropic response."""
        usage = getattr(response, "usage", None)
        tokens: dict[str, int] = {"input": 0, "output": 0, "total": 0}
        if not usage:
            self.log.info("[async] No usage info present; returning zeros")
            return tokens

        def _get(u: object, *names: str) -> int:
            """Attempt to read an integer field from an async response usage object."""
            for nm in names:
                if hasattr(u, nm):
                    try:
                        return int(getattr(u, nm) or 0)
                    except Exception:
                        pass
                if isinstance(u, dict):
                    ud = cast(dict[str, Any], u)
                    if nm in ud:
                        try:
                            return int(ud.get(nm) or 0)
                        except Exception:
                            pass
            return 0

        tokens["input"] = _get(usage, "input_tokens", "prompt_tokens")
        tokens["output"] = _get(usage, "output_tokens", "completion_tokens")
        tokens["total"] = _get(usage, "total_tokens") or (
            tokens["input"] + tokens["output"]
        )
        self.log.info("[async] Anthropic usage: %s", tokens)
        return tokens

    def _extract_code_blocks(self, text: str) -> str:
        """Return the first fenced code block from an async Anthropic response string."""
        code_blocks: list[str] = re.findall(
            r"```(?:[a-zA-Z]*\n)?(.*?)```", text, re.DOTALL
        )
        if not code_blocks:
            return ""
        code_block: str = code_blocks[0].strip()
        import os as _os

        if _os.getenv("CLTK_LOG_CONTENT", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }:
            self.log.debug("[async] Extracted code block:\n%s", code_block)
        return code_block
