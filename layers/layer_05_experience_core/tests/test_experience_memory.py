import json

from layers.layer_05_experience.execution_memory import ExecutionExperienceStore
from layers.layer_05_experience.models import Task


def test_execution_experience_records_source_and_run_provenance(tmp_path):
    store = ExecutionExperienceStore(tmp_path / "experience.json")

    task = store.record_execution(
        request="add validation",
        language="python",
        status="failure",
        capability_id="CAP-001",
        outcome="validation was missing",
        failure_category="capability_gap",
        source="scenario",
        scenario_id="evolution-001",
        run_id="suite-123",
        feedback="disagree",
    )

    assert isinstance(task, Task)
    assert task.source == "scenario"
    assert task.scenario_id == "evolution-001"
    assert task.run_id == "suite-123"
    assert task.feedback == "disagree"

    raw = json.loads((tmp_path / "experience.json").read_text(encoding="utf-8"))
    assert raw["tasks"][0]["status"] == "failure"
    assert raw["tasks"][0]["selected_capability"] == "CAP-001"


def test_execution_experience_survives_reload_and_finds_related_history(tmp_path):
    path = tmp_path / "experience.json"
    first = ExecutionExperienceStore(path)
    first.record_execution(
        request="parse CSV schema",
        language="python",
        status="failure",
        capability_id="CAP-001",
        outcome="capability could not infer mixed columns",
        failure_category="capability_gap",
        source="scenario",
        scenario_id="evolution-101",
        run_id="suite-1",
    )
    first.record_execution(
        request="parse CSV schema",
        language="python",
        status="success",
        capability_id="CAP-001",
        outcome="handled schema",
        source="web_ui",
        scenario_id="",
        run_id="session-2",
        feedback="agree",
    )

    second = ExecutionExperienceStore(path)
    history = second.find_relevant("parse CSV schema", capability_id="CAP-001")

    assert len(history) == 2
    assert {item.status for item in history} == {"failure", "success"}
    assert {item.source for item in history} == {"scenario", "web_ui"}


def test_task_provenance_is_backward_compatible():
    task = Task(id="legacy", user_request="legacy request")
    assert task.source == ""
    assert task.scenario_id == ""
    assert task.run_id == ""
    assert task.feedback == ""
