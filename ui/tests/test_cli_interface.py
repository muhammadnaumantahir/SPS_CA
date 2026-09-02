from __future__ import annotations

import json
from pathlib import Path

from models.base import LLMResponse
from ui.cli_interface import SPS_CA_Interface


class FakeBrain:
    name = "ollama-test-double"

    def __init__(self, plan: dict):
        self.plan = plan

    def is_available(self):
        return True

    def generate(self, request):
        return LLMResponse(
            text=json.dumps(self.plan),
            model=request.model or "test-model",
            provider=self.name,
        )


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
    assert saved["events"][0]["command"] == f"load {project}"


def test_show_registry_lists_real_capabilities(tmp_path: Path):
    ui = SPS_CA_Interface(history_path=tmp_path / "history.json")
    response = ui.handle_command("show registry")
    assert "CAP-001" in response
    assert "Simple Bug Detection" in response
    assert "Prompt Processing" not in response
    assert "CAP-011" in response


def test_process_request_uses_brain_plan_without_prompt_capability(tmp_path: Path):
    project = make_project(tmp_path)
    brain = FakeBrain({
        "intent": "fix syntax",
        "reasoning": "The source has a syntax error.",
        "steps": [{"capability_id": "CAP-002", "reason": "the source has a syntax error"}],
    })
    ui = SPS_CA_Interface(history_path=tmp_path / "history.json", llm_provider=brain)
    ui.load_project(str(project))

    response = ui.process_request("fix the syntax error in app.py")

    assert "Brain:" in response
    assert "CAP-002" in response
    assert "CAP-001 Prompt Processing" not in response


def test_process_request_does_not_override_brain_with_keyword_rules(tmp_path: Path):
    project = make_project(tmp_path)
    brain = FakeBrain({
        "intent": "perform syntax repair",
        "reasoning": "Brain-selected syntax repair.",
        "steps": [{"capability_id": "CAP-002", "reason": "brain selected syntax repair"}],
    })
    ui = SPS_CA_Interface(history_path=tmp_path / "history.json", llm_provider=brain)
    ui.load_project(str(project))
    response = ui.process_request("please fix this bug")
    assert "CAP-002" in response
    assert "CAP-001 Prompt Processing" not in response
