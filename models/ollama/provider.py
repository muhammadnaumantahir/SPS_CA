"""Ollama provider with live model discovery.

SPS-CA must not depend on a model name from a developer machine. Ollama's
/api/tags endpoint is the source of truth for models currently installed on
the server (including an Ollama server exposed from Google Colab).
"""

from __future__ import annotations

import os
from typing import Any

import requests

from models.base import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    LLMTimeoutError,
    LLMUnavailableError,
)

# Use an IPv4 loopback default. In Colab/runtime environments, "localhost"
# can resolve to IPv6 (::1) while Ollama is listening on IPv4 (127.0.0.1).
# Explicit custom URLs remain supported for remote Ollama servers.
DEFAULT_BASE_URL = "http://127.0.0.1:11434"
# Legacy preference only. It is never trusted when the model is not installed.
DEFAULT_MODEL = "qwen2.5-coder:7b"


class OllamaProvider(LLMProvider):
    """LLMProvider backed by Ollama with runtime model discovery."""

    name = "ollama"

    def __init__(self, base_url: str = DEFAULT_BASE_URL, default_model: str = DEFAULT_MODEL) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self._active_model = ""
        self._last_models: list[str] = []

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def list_models(self) -> list[str]:
        """Discover models installed on the currently connected Ollama server."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
        except requests.exceptions.Timeout as exc:
            raise LLMTimeoutError("Timed out while discovering Ollama models") from exc
        except requests.RequestException as exc:
            raise LLMUnavailableError(
                f"Could not discover Ollama models at {self.base_url}. Make sure the Ollama server is running and reachable."
            ) from exc
        except ValueError as exc:
            raise LLMUnavailableError("Ollama returned invalid /api/tags JSON") from exc

        models: list[str] = []
        for item in data.get("models", []):
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or item.get("model") or "").strip()
            if name and name not in models:
                models.append(name)
        self._last_models = models
        return models

    def resolve_model(self, requested_model: str = "") -> str:
        """Select a model that actually exists on Ollama right now."""
        models = self.list_models()
        if not models:
            raise LLMUnavailableError(
                "Ollama is reachable but has no installed models. Pull a model first with `ollama pull <model>`."
            )

        env_model = os.getenv("SPS_CA_MODEL", "").strip()
        for candidate in (requested_model.strip(), env_model, self.default_model):
            if candidate and candidate in models:
                self._active_model = candidate
                return candidate

        self._active_model = models[0]
        return self._active_model

    @property
    def active_model(self) -> str:
        return self._active_model

    def generate(self, request: LLMRequest) -> LLMResponse:
        # Resolve against the live server on EVERY request. A stale browser/session
        # model cannot force SPS-CA to use a model that no longer exists.
        model = self.resolve_model(request.model or "")
        payload: dict[str, Any] = {
            "model": model,
            "prompt": request.prompt,
            "stream": False,
            "options": {"temperature": request.temperature},
        }
        if request.system:
            payload["system"] = request.system

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=request.timeout_seconds,
            )
        except requests.exceptions.Timeout as exc:
            raise LLMTimeoutError(f"Ollama did not respond within {request.timeout_seconds}s") from exc
        except requests.exceptions.ConnectionError as exc:
            raise LLMUnavailableError(
                f"Could not reach Ollama at {self.base_url}. Make sure the Ollama server is running and reachable."
            ) from exc
        except requests.RequestException as exc:
            raise LLMUnavailableError(f"Ollama request failed: {exc}") from exc

        # Colab can restart/change its model between discovery and generation.
        if response.status_code == 404:
            current_models = self.list_models()
            if current_models and model not in current_models:
                model = self.resolve_model("")
                payload["model"] = model
                try:
                    response = requests.post(
                        f"{self.base_url}/api/generate",
                        json=payload,
                        timeout=request.timeout_seconds,
                    )
                except requests.RequestException as exc:
                    raise LLMUnavailableError(f"Ollama retry failed: {exc}") from exc

        if response.status_code != 200:
            raise LLMUnavailableError(
                f"Ollama returned HTTP {response.status_code}: {response.text[:500]}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMUnavailableError("Ollama returned invalid /api/generate JSON") from exc

        return LLMResponse(text=data.get("response", ""), model=model, provider=self.name, raw=data)
