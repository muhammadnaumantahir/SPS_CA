"""Provider-neutral model interface.

Per architecture v2 section 4: "SPS-CA talks to a model interface, not
directly to Qwen or a cloud provider." Every provider adapter (Ollama
today; OpenAI/Anthropic adapters are future boundaries under
``models/openai`` and ``models/anthropic``) implements :class:`LLMProvider`.
Nothing in ``layers/`` should import a concrete provider directly -- only
this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


class LLMError(Exception):
    """Base class for provider-facing errors."""


class LLMTimeoutError(LLMError):
    """Raised when a provider does not respond within the configured timeout."""


class LLMUnavailableError(LLMError):
    """Raised when a provider cannot be reached at all (connection refused, etc.)."""


@dataclass
class LLMRequest:
    """A single query to a model.

    Attributes:
        prompt: The user/task content (typically code + instructions).
        system: Optional system-level instruction.
        model: Provider-specific model identifier, e.g. ``"qwen2.5-coder:7b"``.
        temperature: Sampling temperature.
        timeout_seconds: Max time to wait. Local inference (Ollama on
            modest hardware) can be slow, so this defaults high.
        metadata: Free-form extra context for logging/tracing.
    """

    prompt: str
    system: Optional[str] = None
    model: str = ""
    temperature: float = 0.2
    timeout_seconds: float = 120.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Result of a model query."""

    text: str
    model: str
    provider: str
    raw: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class every model provider adapter must implement."""

    name: str = "base"

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Send a request and return a response, or raise an LLMError subclass."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Cheap reachability check (e.g. can the provider be reached at all)."""
        raise NotImplementedError
