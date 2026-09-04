from models.ollama.provider import DEFAULT_BASE_URL, OllamaProvider


def test_ollama_defaults_to_ipv4_loopback_for_colab_compatibility():
    """Colab's local Ollama daemon must be reachable without IPv6 localhost resolution."""
    assert DEFAULT_BASE_URL == "http://127.0.0.1:11434"
    assert OllamaProvider().base_url == "http://127.0.0.1:11434"
