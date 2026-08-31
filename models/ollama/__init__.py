"""Ollama local-model adapter boundary."""

from .provider import DEFAULT_BASE_URL, DEFAULT_MODEL, OllamaProvider

__all__ = ["OllamaProvider", "DEFAULT_BASE_URL", "DEFAULT_MODEL"]
