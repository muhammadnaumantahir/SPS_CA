from __future__ import annotations

import json

from ui.cli_interface import SPS_CA_Interface


def make_ui(tmp_path):
    return SPS_CA_Interface(
        history_path=tmp_path / "history.json",
        trace_history_path=tmp_path / "evolution_history.json",
        trace_stage_path=tmp_path / "stage.json",
    )


def test_submit_runs_task_and_code_analysis(tmp_path):
    ui = make_ui(tmp_path)

    response = ui.submit_submission(
        "Add input validation before calculation",
        "def calculate(age):\n    return age + 10\n",
        "python",
        file_path="example.py",
    )

    assert "SC-001" in response
    record = ui.trace_store.list_records()[0]
    assert record["analysis"]["user_intent"] == "Add input validation before calculation"
    assert record["analysis"]["language"] == "python"
    assert record["analysis"]["code_present"] is True
    assert record["analysis"]["files_analyzed"] == 1
    assert record["analysis"]["parse_ok"] is True


def test_submit_records_capability_search(tmp_path):
    ui = make_ui(tmp_path)

    ui.submit_submission(
        "Add exception handling",
        "def divide(a, b):\n    return a / b\n",
        "python",
    )

    record = ui.trace_store.list_records()[0]
    search = record["capability_search"]
    assert "capability_ids" in search
    assert "selected" in search
    assert isinstance(search["found"], bool)
    assert "why" in search


def test_submit_plans_missing_capability_in_layer_eight(tmp_path):
    ui = make_ui(tmp_path)

    ui.submit_submission(
        "Parameterize SQL queries",
        'cursor.execute(f"select * from users where id={user_id}")',
        "python",
    )

    record = ui.trace_store.list_records()[0]
    generation = record["capability_generation"]
    assert generation["required"] is True
    assert generation["layer"] == "Layer 8 - Evolution"
    assert generation["provenance"]["trigger"] == "capability_gap"
    assert generation["provenance"]["why"]
    assert generation["capability_id"].startswith("CAP-")
