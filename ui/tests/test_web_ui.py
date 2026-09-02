"""Smoke tests for the SPS-CA research dashboard presentation layer."""


def test_web_ui_import_and_build():
    from ui.web_ui import build_app

    app = build_app()
    assert app is not None


def test_dashboard_helpers_return_research_shapes():
    from ui.web_ui import _capability_table, _evolution_table, _growth_figure, _layer_html, _metrics, _reuse_figure

    metrics = _metrics()
    assert set(("stage", "capabilities", "generated", "reused", "scenarios", "success_rate", "rollbacks")) <= set(metrics)
    assert _growth_figure() is not None
    assert _reuse_figure() is not None
    assert _capability_table() is not None
    assert _evolution_table() is not None
    layer_html = _layer_html()
    assert "Software DNA" in layer_html
    assert "Execution" in layer_html
    assert "Layer" not in layer_html or "10" in layer_html
