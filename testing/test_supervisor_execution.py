from __future__ import annotations

import json
from pathlib import Path

from ui.supervisor_execution import SupervisorExecutionService


def test_supervisor_execution_grows_capability_and_modifies_submitted_code(tmp_path: Path):
    history = tmp_path / "evolution_history.json"
    stage = tmp_path / "stage_state.json"
    registry = tmp_path / "registry.json"
    generated = tmp_path / "generated"
    evolution = tmp_path / "evaluation"
    workspace = tmp_path / "workspaces"

    # Use an isolated generated-capability registry while keeping the repository
    # seed metadata as the source for initial capability numbering.
    service = SupervisorExecutionService(
        trace_history_path=history,
        trace_stage_path=stage,
        registry_path=str(registry),
        seeds_dir="capabilities/seeds",
        generated_dir=str(generated),
        evolution_dir=str(evolution),
        workspace_root=str(workspace),
    )

    result = service.run_submission(
        user_request="Add input validation to this function",
        code="def calculate(age):\n    return age + 10\n",
        language="python",
        file_path="app.py",
    )

    assert result["success"] is True
    assert result["generated"] is True
    assert result["execution"] == "success"
    assert result["validation"] == "success"
    assert result["governance"] == "auto_approved"
    assert result["stage_before"] == 0
    assert result["stage_after"] == 1
    assert result["modified_code"] != "def calculate(age):\n    return age + 10\n"

    records = json.loads(history.read_text(encoding="utf-8"))
    record = records[0]
    assert record["analysis"]["parse_ok"] is True
    assert record["capability_generation"]["required"] is True
    assert record["capability_generation"]["registered"] is True
    assert record["modification"]["changed"] is True
    assert record["validation"]["status"] == "success"
    assert record["governance"]["decision"] == "auto_approved"
    assert record["result"]["success"] is True
