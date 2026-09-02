"""Smoke tests for the SPS-CA Gradio presentation layer."""


def test_web_ui_import_and_build():
    from ui.web_ui import build_app

    app = build_app()
    assert app is not None
