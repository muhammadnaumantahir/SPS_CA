"""Ollama local-model adapter.

Talks to a local Ollama server's HTTP API (``/api/generate`` and
``/api/tags``). This is the zero-cost provider used for the initial
prototype (see REQUIREMENTS.md: ``qwen2.5-coder:7b`` on the current
16GB RAM / Intel HD 620 / i7 7th Gen dev machine).
"""

from __future__ import annotations

import requests

from models.base import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    LLMTimeoutError,
    LLMUnavailableError,
)

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5-coder:7b"


class OllamaProvider(LLMProvider):
    """LLMProvider backed by a local Ollama server."""

    name = "ollama"

    def __init__(
        self, base_url: str = DEFAULT_BASE_URL, default_model: str = DEFAULT_MODEL
    ):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    def is_available(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def generate(self, request: LLMRequest) -> LLMResponse:
        model = request.model or self.default_model
        payload = {
            "model": model,
            "prompt": request.prompt,
            "stream": False,
            "options": {"temperature": request.temperature},
        }
        if request.system:
            payload["system"] = request.system

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=request.timeout_seconds,
            )
        except requests.exceptions.Timeout as exc:
            raise LLMTimeoutError(
                f"Ollama did not respond within {request.timeout_seconds}s"
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise LLMUnavailableError(
                f"Could not reach Ollama at {self.base_url}. "
                "Is 'ollama serve' running?"
            ) from exc

        if resp.status_code != 200:
            raise LLMUnavailableError(
                f"Ollama returned HTTP {resp.status_code}: {resp.text[:500]}"
            )

        data = resp.json()
        return LLMResponse(
            text=data.get("response", ""),
            model=model,
            provider=self.name,
            raw=data,
        )
