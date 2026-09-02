from __future__ import annotations

import json

from ui.supervisor_service import SupervisorScenarioService


def test_missing_capability_is_developed_and_recorded(tmp_path):
    registry_path = tmp_path / "registry.json"
    service = SupervisorScenarioService(
        trace_history_path=tmp_path / "evolution_history.json",
        trace_stage_path=tmp_path / "stage_state.json",
        registry_path=str(registry_path),
        seeds_dir="capabilities/seeds",
        generated_dir=str(tmp_path / "generated"),
    )

    result = service.analyze_submission(
        user_request="Parameterize SQL queries",
        code='cursor.execute(f"select * from users where id={user_id}")',
        language="python",
    )

    assert result.capability_generation["required"] is True
    assert result.capability_generation["developed"] is True
    assert result.capability_generation["implemented"] is True
    assert result.capability_generation["capability_id"].startswith("CAP-")
    assert "test_result" in result.capability_generation

    records = service.trace_store.list_records()
    assert len(records) == 1
    record = records[0]
    assert record["status"] in {"capability_developed", "capability_development_failed"}
    assert record["capability_generation"]["developed"] is True
    assert record["events"][-1]["event"] in {
        "capability_developed",
        "capability_development_failed",
    }

    if result.capability_generation["registered"]:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        assert result.capability_generation["capability_id"] in registry
