from __future__ import annotations

import json

from experience.evolution_trace import EvolutionTraceStore


def test_trace_store_starts_at_stage_zero(tmp_path):
    store = EvolutionTraceStore(
        history_path=tmp_path / "evolution_history.json",
        stage_path=tmp_path / "stage_state.json",
    )

    assert store.current_stage() == 0
    assert store.next_scenario_id() == "SC-001"
    assert store.list_records() == []


def test_scenario_records_input_and_evolution_fields(tmp_path):
    history = tmp_path / "evolution_history.json"
    stage = tmp_path / "stage_state.json"
    store = EvolutionTraceStore(history_path=history, stage_path=stage)

    started = store.start_scenario(
        user_request="Add input validation",
        code="def add(a, b): return a + b",
        language="python",
        file_path="example.py",
    )

    assert started["scenario_id"] == "SC-001"
    assert started["stage_before"] == 0
    assert started["input"]["code_sha256"]
    assert started["input"]["code_length"] > 0

    completed = store.complete_scenario(
        "SC-001",
        stage_after=1,
        analysis={"why": "user requested validation", "what": "guard inputs"},
        capability_search={"found": False, "reason": "no matching capability"},
        capability_generation={
            "required": True,
            "why": "existing registry has no input validation capability",
            "what": "input_validation",
            "how": "generated from capability specification",
        },
        modification={"files_changed": ["example.py"]},
        validation={"passed": True},
        governance={"decision": "auto_approved"},
        result={"success": True},
    )

    assert completed["status"] == "completed"
    assert completed["stage_before"] == 0
    assert completed["stage_after"] == 1
    assert store.current_stage() == 1
    assert store.next_scenario_id() == "SC-002"

    on_disk = json.loads(history.read_text(encoding="utf-8"))
    assert len(on_disk) == 1
    assert on_disk[0]["scenario_id"] == "SC-001"
    assert on_disk[0]["capability_generation"]["required"] is True


def test_events_are_timestamped_and_researchable(tmp_path):
    store = EvolutionTraceStore(
        history_path=tmp_path / "history.json",
        stage_path=tmp_path / "stage.json",
    )
    store.start_scenario(user_request="Fix parser", code="x", language="python")
    store.append_event("SC-001", "capability_search", {"matches": []})
    store.append_event("SC-001", "capability_generation", {"capability_id": "CAP-009"})

    record = store.list_records()[0]
    assert len(record["events"]) == 2
    assert record["events"][0]["event"] == "capability_search"
    assert record["events"][1]["details"]["capability_id"] == "CAP-009"
