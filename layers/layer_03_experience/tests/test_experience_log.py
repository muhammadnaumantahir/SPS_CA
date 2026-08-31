"""Tests for ExperienceLog (Layer 3)."""

from __future__ import annotations

import json

import pytest

from layers.layer_03_experience.experience_log import ExperienceLog
from layers.layer_03_experience.models import Task


def _task(id_, status="success", capability="CAP-001", failure_category=None):
    return Task(
        id=id_,
        user_request=f"request for {id_}",
        selected_capability=capability,
        status=status,
        failure_category=failure_category,
        time_taken_seconds=10.0,
    )


def test_add_task_appends_and_updates_metrics():
    log = ExperienceLog()
    log.add_task(_task("task_001"))
    assert len(log.tasks) == 1
    assert log.metrics["total_tasks"] == 1
    assert log.metrics["overall_success_rate"] == 1.0


def test_get_failure_patterns_counts_by_category():
    log = ExperienceLog()
    log.add_task(
        _task("task_001", status="failure", failure_category="Pattern mismatch")
    )
    log.add_task(
        _task("task_002", status="failure", failure_category="Pattern mismatch")
    )
    log.add_task(_task("task_003", status="failure", failure_category="Timeout"))
    log.add_task(_task("task_004", status="success"))

    patterns = log.get_failure_patterns()
    assert patterns == {"Pattern mismatch": 2, "Timeout": 1}


def test_get_capability_success_rate():
    log = ExperienceLog()
    log.add_task(_task("task_001", status="success", capability="CAP-002"))
    log.add_task(_task("task_002", status="failure", capability="CAP-002"))
    log.add_task(_task("task_003", status="success", capability="CAP-002"))

    assert log.get_capability_success_rate("CAP-002") == pytest.approx(2 / 3)


def test_get_capability_success_rate_unused_capability_is_zero():
    log = ExperienceLog()
    log.add_task(_task("task_001", capability="CAP-001"))
    assert log.get_capability_success_rate("CAP-999") == 0.0
    assert log.get_capability_usage_count("CAP-999") == 0


def test_overall_success_rate_empty_log():
    log = ExperienceLog()
    assert log.get_overall_success_rate() == 0.0


def test_save_and_load_round_trip(tmp_path):
    log = ExperienceLog()
    log.add_task(_task("task_001", status="success"))
    log.add_task(_task("task_002", status="failure", failure_category="Timeout"))

    out_path = tmp_path / "experience_log.json"
    log.save_to_json(out_path)

    assert out_path.exists()
    raw = json.loads(out_path.read_text())
    assert len(raw["tasks"]) == 2

    reloaded = ExperienceLog.load_from_json(out_path)
    assert len(reloaded.tasks) == 2
    assert reloaded.tasks[0].id == "task_001"
    assert reloaded.metrics["total_tasks"] == 2


def test_load_from_json_missing_file_returns_empty_log(tmp_path):
    log = ExperienceLog.load_from_json(tmp_path / "does_not_exist.json")
    assert log.tasks == []


def test_save_failure_patterns(tmp_path):
    log = ExperienceLog()
    log.add_task(_task("task_001", status="failure", failure_category="Timeout"))
    out_path = tmp_path / "failure_patterns.json"
    log.save_failure_patterns(out_path)

    data = json.loads(out_path.read_text())
    assert data == {"Timeout": 1}
