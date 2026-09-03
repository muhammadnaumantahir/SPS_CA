"""Tests for Adaptation / AdaptationLog (Layer 5)."""

from __future__ import annotations

from layers.layer_05_experience.models import Task
from layers.layer_07_adaptation.adaptation import Adaptation, AdaptationLog
from layers.layer_07_adaptation.models import AdaptationRecord


def _task(id_, request, status="success", capability="CAP-003"):
    return Task(
        id=id_,
        user_request=request,
        status=status,
        selected_capability=capability,
    )


def test_can_reuse_capability_true_for_similar_successful_task():
    adaptation = Adaptation()
    past = _task(
        "task_030", "generate unit tests for the payment module", status="success"
    )
    current = _task(
        "task_045", "generate unit tests for the billing module", status="success"
    )
    assert adaptation.can_reuse_capability(current, past) is True


def test_can_reuse_capability_false_when_past_task_failed():
    adaptation = Adaptation()
    past = _task(
        "task_030", "generate unit tests for the payment module", status="failure"
    )
    current = _task("task_045", "generate unit tests for the billing module")
    assert adaptation.can_reuse_capability(current, past) is False


def test_can_reuse_capability_false_when_unrelated():
    adaptation = Adaptation()
    past = _task("task_030", "generate unit tests for the payment module")
    current = _task("task_045", "remove unused variables from the logging config")
    assert adaptation.can_reuse_capability(current, past) is False


def test_adjust_parameters_increases_timeout_for_slower_language():
    adaptation = Adaptation()
    params = {"timeout_seconds": 5.0, "language": "python"}
    adjusted, changes = adaptation.adjust_parameters(
        params, {"target_language": "java"}
    )
    assert adjusted["timeout_seconds"] == 15.0
    assert adjusted["language"] == "java"
    assert "timeout_seconds" in changes
    assert "language" in changes


def test_adjust_parameters_no_change_for_same_fast_language():
    adaptation = Adaptation()
    params = {"timeout_seconds": 5.0, "language": "python"}
    adjusted, changes = adaptation.adjust_parameters(
        params, {"target_language": "python"}
    )
    assert adjusted == params
    assert changes == {}


def test_adjust_parameters_sets_conservative_aggressiveness_for_complex_tasks():
    adaptation = Adaptation()
    params = {"aggressiveness": "normal"}
    adjusted, changes = adaptation.adjust_parameters(params, {"complex": True})
    assert adjusted["aggressiveness"] == "conservative"
    assert "aggressiveness" in changes


def test_test_adaptation_rejects_empty_code():
    adaptation = Adaptation()
    assert adaptation.test_adaptation({"timeout_seconds": 5.0}, "   ") is False


def test_test_adaptation_rejects_non_positive_timeout():
    adaptation = Adaptation()
    assert adaptation.test_adaptation({"timeout_seconds": 0}, "print('hi')") is False


def test_test_adaptation_accepts_valid_input():
    adaptation = Adaptation()
    assert adaptation.test_adaptation({"timeout_seconds": 15.0}, "print('hi')") is True


def test_adapt_and_record_produces_consistent_record():
    adaptation = Adaptation()
    params = {"timeout_seconds": 5.0, "language": "python"}
    adjusted, record = adaptation.adapt_and_record(
        record_id="adaptation_001",
        base_capability_id="CAP-003",
        capability_params=params,
        task_context={"target_language": "java"},
        target_code="public class Foo {}",
        applied_to_task_id="task_045",
    )
    assert adjusted["timeout_seconds"] == 15.0
    assert record.success is True
    assert record.base_capability_id == "CAP-003"
    assert "timeout_seconds" in record.parameters_changed


def test_adaptation_log_round_trip(tmp_path):
    record = AdaptationRecord(
        id="adaptation_001",
        base_capability_id="CAP-003",
        applied_to_task_id="task_045",
        parameters_changed={"timeout_seconds": "5.0s -> 15.0s"},
        success=True,
    )
    log = AdaptationLog()
    log.add_record(record)

    out_path = tmp_path / "adaptations.json"
    log.save_to_json(out_path)
    assert out_path.exists()

    reloaded = AdaptationLog.load_from_json(out_path)
    assert len(reloaded.records) == 1
    assert reloaded.records[0].id == "adaptation_001"


def test_adaptation_log_load_missing_file_returns_empty(tmp_path):
    log = AdaptationLog.load_from_json(tmp_path / "missing.json")
    assert log.records == []
