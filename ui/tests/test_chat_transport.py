from pathlib import Path


def test_chat_uses_stream_transport_for_long_running_generation():
    """The Colab/ngrok UI must not depend on one long-lived JSON POST."""
    html = Path("ui/web/index.html").read_text(encoding="utf-8")

    assert "/api/chat/stream" in html
    assert "reader.read()" in html
    assert "Chat stream ended without a result." in html
    assert "I could not complete this turn." in html
