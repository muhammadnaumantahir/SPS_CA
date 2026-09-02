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


def test_help_command_contains_required_commands(tmp_path: Path):
    ui = SPS_CA_Interface(history_path=tmp_path / "history.json")
    text = ui.handle_command("help")
    assert "load <project_path>" in text
    assert "show <context>" in text
    assert "quit" in text


def test_load_project_detects_language_and_records_history(tmp_path: Path):
    project = make_project(tmp_path)
    history = tmp_path / "history.json"
    ui = SPS_CA_Interface(history_path=history)

    response = ui.handle_command(f"load {project}")

    assert "Loaded project" in response
    assert ui.project_context is not None
    assert ui.project_context["language"] == "python"
    saved = json.loads(history.read_text(encoding="utf-8"))
    assert saved["events"][0]["command"] == "load"


def test_show_registry_lists_generated_capability(tmp_path: Path):
    ui = SPS_CA_Interface(history_path=tmp_path / "history.json")
    response = ui.handle_command("show registry")
    assert "CAP-009" in response


def test_process_request_routes_through_cognitive_core(tmp_path: Path):
    project = make_project(tmp_path)
    ui = SPS_CA_Interface(history_path=tmp_path / "history.json")
    ui.load_project(str(project))

    response = ui.process_request("fix the syntax error in app.py")

    assert "CAP-002" in response
    assert "Validation" in response
    assert "Governance" in response
    assert "Execution" in response
