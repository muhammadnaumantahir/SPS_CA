from pathlib import Path


def test_chat_uses_stream_transport_for_long_running_generation():
    """The Colab/ngrok UI must not depend on one long-lived JSON POST."""
    html = Path("ui/web/index.html").read_text(encoding="utf-8")

    assert "/api/chat/stream" in html
    assert "EventSource" not in html  # POST body is required for chat context; use fetch streaming instead.
    assert "reader.read()" in html
    assert "network error" in html.lower()
