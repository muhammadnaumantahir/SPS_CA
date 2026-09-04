from models.base import LLMRequest
from models.ollama.provider import DEFAULT_BASE_URL, OllamaProvider


def test_ollama_defaults_to_ipv4_loopback_for_colab_compatibility():
    """Colab's local Ollama daemon must be reachable without IPv6 localhost resolution."""
    assert DEFAULT_BASE_URL == "http://127.0.0.1:11434"
    assert OllamaProvider().base_url == "http://127.0.0.1:11434"


def test_ollama_recovers_from_sigkill_with_installed_lighter_coder_model(monkeypatch):
    """A Colab OOM-killed large model should transparently retry with a lighter installed coder model."""
    provider = OllamaProvider()
    monkeypatch.setattr(provider, "list_models", lambda: ["qwen3-coder:30b", "qwen2.5-coder:7b"])

    class Response:
        def __init__(self, status_code, payload):
            self.status_code = status_code
            self._payload = payload
            self.text = str(payload)

        def json(self):
            return self._payload

    calls = []

    def post(url, json, timeout):
        calls.append(json["model"])
        if len(calls) == 1:
            return Response(500, {"error": "llama-server process has terminated: signal: killed"})
        return Response(200, {"response": "def add(a, b):\n    return a + b"})

    monkeypatch.setattr("models.ollama.provider.requests.post", post)
    result = provider.generate(LLMRequest(prompt="write add", model="qwen3-coder:30b"))

    assert calls == ["qwen3-coder:30b", "qwen2.5-coder:7b"]
    assert result.model == "qwen2.5-coder:7b"
    assert "return a + b" in result.text
