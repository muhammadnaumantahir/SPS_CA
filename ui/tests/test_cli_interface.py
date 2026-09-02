from __future__ import annotations

import json
from pathlib import Path

from ui.cli_interface import SPS_CA_Interface


def make_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    (project / "app.py").write_text("def f(x)\n    return x\n", encoding="utf-8")
    (project / "tests").mkdir()
    (project / "tests" / "test_app.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
    return project


def make_ui(tmp_path: Path) -> SPS_CA_Interface:
    return SPS_CA_Interface(
        history_path=tmp_path / "history.json",
        trace_history_path=tmp_path / "evolution_history.json",
        trace_stage_path=tmp_path / "stage_state.json",
    )


def test_help_command_contains_required_commands(tmp_path: Path):
    ui = make_ui(tmp_path)
    text = ui.handle_command("help")
    assert "load <project_path>" in text
    assert "submit" in text
    assert "submit_file <path>" in text
    assert "show <context>" in text
    assert "quit" in text


def test_load_project_detects_language_and_records_history(tmp_path: Path):
    project = make_project(tmp_path)
    history = tmp_path / "history.json"
    ui = SPS_CA_Interface(
        history_path=history,
        trace_history_path=tmp_path / "evolution_history.json",
        trace_stage_path=tmp_path / "stage_state.json",
    )

    response = ui.handle_command(f"load {project}")

    assert "Loaded project" in response
    assert ui.project_context is not None
    assert ui.project_context["language"] == "python"
    saved = json.loads(history.read_text(encoding="utf-8"))
    assert saved["events"][0]["command"] == "load"


def test_show_registry_lists_generated_capability(tmp_path: Path):
    ui = make_ui(tmp_path)
    response = ui.handle_command("show registry")
    assert "CAP-009" in response


def test_process_request_routes_through_cognitive_core(tmp_path: Path):
    project = make_project(tmp_path)
    ui = make_ui(tmp_path)
    ui.load_project(str(project))

    response = ui.process_request("fix the syntax error in app.py")

    assert "CAP-002" in response
    assert "Validation" in response
    assert "Governance" in response
    assert "Execution" in response


def test_submit_submission_creates_stage_zero_trace(tmp_path: Path):
    ui = make_ui(tmp_path)

    response = ui.submit_submission(
        "Add input validation",
        "def add(a, b):\n    return a + b\n",
        "python",
        file_path="example.py",
    )

    assert "Scenario captured: SC-001" in response
    assert "Stage: 0" in response

    trace = json.loads((tmp_path / "evolution_history.json").read_text(encoding="utf-8"))
    assert len(trace) == 1
    assert trace[0]["scenario_id"] == "SC-001"
    assert trace[0]["stage_before"] == 0
    assert trace[0]["input"]["file_path"] == "example.py"
    assert trace[0]["events"][0]["event"] == "submission_received"


def test_show_evolution_reads_persisted_trace(tmp_path: Path):
    ui = make_ui(tmp_path)
    ui.submit_submission("Fix parser", "x = 1", "python")

    response = ui.handle_command("show evolution")

    assert "SC-001" in response
    assert "Stage 0 -> 0" in response
    assert "Fix parser" in response
