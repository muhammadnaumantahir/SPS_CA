import pytest

from layers.layer_03_cognitive.llm_interface import LLMInterface, LLMQueryError
from models.base import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    LLMTimeoutError,
    LLMUnavailableError,
)


class FakeProvider(LLMProvider):
    name = "fake"

    def __init__(self, response_text="ok", available=True, raise_error=None):
        self.response_text = response_text
        self.available = available
        self.raise_error = raise_error
        self.last_request = None

    def is_available(self):
        return self.available

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.last_request = request
        if self.raise_error:
            raise self.raise_error
        return LLMResponse(
            text=self.response_text,
            model=request.model or "fake-model",
            provider=self.name,
        )


class TestLLMInterface:
    def test_query_returns_provider_text(self):
        provider = FakeProvider(response_text="looks fine")
        llm = LLMInterface(provider=provider)
        result = llm.query(code="def f(): pass", instruction="Review this")
        assert result == "looks fine"

    def test_query_frames_prompt_with_code_and_instruction(self):
        provider = FakeProvider()
        llm = LLMInterface(provider=provider)
        llm.query(code="x = 1", instruction="Explain this")
        assert "Explain this" in provider.last_request.prompt
        assert "x = 1" in provider.last_request.prompt
        assert provider.last_request.system is not None

    def test_query_respects_configured_timeout(self):
        provider = FakeProvider()
        llm = LLMInterface(provider=provider, timeout_seconds=5.0)
        llm.query(code="x = 1", instruction="Explain")
        assert provider.last_request.timeout_seconds == 5.0

    def test_timeout_error_wrapped(self):
        provider = FakeProvider(raise_error=LLMTimeoutError("too slow"))
        llm = LLMInterface(provider=provider)
        with pytest.raises(LLMQueryError):
            llm.query(code="x", instruction="do it")

    def test_unavailable_error_wrapped(self):
        provider = FakeProvider(raise_error=LLMUnavailableError("no server"))
        llm = LLMInterface(provider=provider)
        with pytest.raises(LLMQueryError):
            llm.query(code="x", instruction="do it")

    def test_is_available_delegates_to_provider(self):
        provider = FakeProvider(available=False)
        llm = LLMInterface(provider=provider)
        assert llm.is_available() is False

    def test_defaults_to_ollama_provider(self):
        llm = LLMInterface()
        assert llm.provider.name == "ollama"
