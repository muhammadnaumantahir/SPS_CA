"""Smoke tests for the SPS-CA research dashboard presentation layer."""

import ast


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


def test_run_sps_dedents_indented_python_before_execution(monkeypatch):
    """Pasted snippets often carry a common leading indent (e.g. copied out of
    a guide or chat message). ast.parse rejects that on line 1 with
    "unexpected indent". _run_sps must dedent Python submissions before they
    reach SPSExecutionService, without altering the code's actual semantics."""
    import ui.web_ui as web_ui

    captured = {}

    class _FakeExecutionService:
        def run_submission(self, *, user_request, code, language, file_path, target_project):
            captured["code"] = code
            # The dedented code must itself be valid Python.
            ast.parse(code)
            return {
                "scenario_id": "SC-TEST",
                "stage_before": 0,
                "stage_after": 0,
                "capability_id": "CAP-TEST",
                "generated": False,
                "validation": "passed",
                "governance": "auto_approved",
                "execution": "applied",
                "success": True,
                "modified_code": code,
            }

    monkeypatch.setattr(web_ui, "SPSExecutionService", _FakeExecutionService)

    indented_code = "  def calculate(age):\n      return age + 10\n"
    web_ui._run_sps("Add input validation", indented_code, "python", None, "")

    assert captured["code"] == "def calculate(age):\n    return age + 10\n"


def test_run_sps_leaves_non_python_code_untouched(monkeypatch):
    import ui.web_ui as web_ui

    captured = {}

    class _FakeExecutionService:
        def run_submission(self, *, user_request, code, language, file_path, target_project):
            captured["code"] = code
            return {"scenario_id": "SC-TEST", "success": True, "modified_code": code}

    monkeypatch.setattr(web_ui, "SPSExecutionService", _FakeExecutionService)

    indented_code = "  function calc(age) {\n    return age + 10;\n  }\n"
    web_ui._run_sps("Add input validation", indented_code, "javascript", None, "")

    assert captured["code"] == indented_code
