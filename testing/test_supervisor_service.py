from __future__ import annotations

from ui.supervisor_service import SupervisorScenarioService


def make_service(tmp_path):
    return SupervisorScenarioService(
        trace_history_path=tmp_path / "evolution_history.json",
        trace_stage_path=tmp_path / "stage.json",
        registry_path="capabilities/registry.json",
        seeds_dir="capabilities/seeds",
        generated_dir=str(tmp_path / "generated"),
    )


def test_service_analyzes_prompt_and_code(tmp_path):
    service = make_service(tmp_path)

    result = service.analyze_submission(
        user_request="Add exception handling",
        code="def divide(a, b):\n    return a / b\n",
        language="python",
        file_path="example.py",
    )

    assert result.scenario_id == "SC-001"
    assert result.analysis["user_intent"] == "Add exception handling"
    assert result.analysis["language"] == "python"
    assert result.analysis["code_present"] is True
    assert result.analysis["files_analyzed"] == 1
    assert result.analysis["parse_ok"] is True
    assert result.capability_search["found"] is True
    assert "CAP-005" in result.capability_search["capability_ids"]


def test_service_detects_gap_and_creates_layer_eight_plan(tmp_path):
    service = make_service(tmp_path)

    result = service.analyze_submission(
        user_request="Parameterize SQL queries",
        code='cursor.execute(f"select * from users where id={user_id}")',
        language="python",
    )

    assert result.capability_search["found"] is False
    assert result.capability_generation["required"] is True
    assert result.capability_generation["layer"] == "Layer 8 - Evolution"
    assert result.capability_generation["capability_id"].startswith("CAP-")
    assert result.capability_generation["provenance"]["trigger"] == "capability_gap"


def test_service_persists_complete_analysis_trace(tmp_path):
    service = make_service(tmp_path)

    service.analyze_submission(
        user_request="Add input validation before calculation",
        code="def calculate(age):\n    return age + 10\n",
        language="python",
        file_path="example.py",
    )

    record = service.trace_store.list_records()[0]
    assert record["stage_before"] == 0
    assert record["status"] == "capability_planned"
    assert record["analysis"]["code_present"] is True
    assert "capability_ids" in record["capability_search"]
    assert record["capability_generation"]["required"] is True
