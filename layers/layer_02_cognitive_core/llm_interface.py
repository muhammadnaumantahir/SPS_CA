"""Layer 2's interface to a local LLM.

Per architecture v2 section 4, SPS layers must talk to the model
abstraction in ``models/``, never to a concrete provider directly. This
module is that call site for Layer 2: it wraps an ``LLMProvider`` (Ollama
by default, since that's the zero-cost local provider used for the
prototype) and adds the query framing (code + context in, text out) and
timeout handling called for in the Phase 1 spec ("Handle timeouts (local
inference is slow)").
"""

from __future__ import annotations

from typing import Optional

from models.base import (
    LLMError,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    LLMTimeoutError,
    LLMUnavailableError,
)
from models.ollama import OllamaProvider

DEFAULT_TIMEOUT_SECONDS = 120.0

_SYSTEM_PROMPT = (
    "You are the reasoning component of SPS-CA, a governed self-programming "
    "coding assistant. You analyze code and requests; you do not execute or "
    "apply changes yourself."
)


class LLMQueryError(Exception):
    """Raised when a query to the underlying provider fails or times out."""


class LLMInterface:
    """Cognitive Core's entry point for querying a local LLM.

    Kept deliberately thin: framing a prompt and delegating to whichever
    ``LLMProvider`` was supplied. Defaults to :class:`OllamaProvider` so
    Layer 2 works out of the box against a local ``ollama serve``.
    """

    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.provider = provider or OllamaProvider()
        self.timeout_seconds = timeout_seconds

    def is_available(self) -> bool:
        return self.provider.is_available()

    def query(
        self,
        code: str,
        instruction: str,
        model: str = "",
        temperature: float = 0.2,
    ) -> str:
        """Send code + an instruction to the LLM and return the raw text response.

        Raises:
            LLMQueryError: on timeout or provider unavailability, wrapping
                the underlying ``models.base`` error so Layer 2 callers only
                need to catch one exception type.
        """
        prompt = f"{instruction}\n\n```\n{code}\n```"
        request = LLMRequest(
            prompt=prompt,
            system=_SYSTEM_PROMPT,
            model=model,
            temperature=temperature,
            timeout_seconds=self.timeout_seconds,
        )
        try:
            response: LLMResponse = self.provider.generate(request)
        except LLMTimeoutError as exc:
            raise LLMQueryError(
                f"LLM query timed out after {self.timeout_seconds}s. "
                "Local inference can be slow; consider raising timeout_seconds "
                "or using a smaller model."
            ) from exc
        except LLMUnavailableError as exc:
            raise LLMQueryError(f"LLM provider unavailable: {exc}") from exc
        except LLMError as exc:
            raise LLMQueryError(f"LLM query failed: {exc}") from exc
        return response.text
