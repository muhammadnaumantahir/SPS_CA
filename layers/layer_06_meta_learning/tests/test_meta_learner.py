"""Tests for MetaLearner / MetaLearningDecisionLog (Layer 4)."""

from __future__ import annotations

import pytest

from layers.layer_05_experience.experience_log import ExperienceLog
from layers.layer_05_experience.models import Task
from layers.layer_06_meta_learning.meta_learner import (
    MetaLearner, MetaLearningDecisionLog)
from layers.layer_06_meta_learning.models import MetaLearningDecision


def _task(id_, status="success", capability="CAP-001", failure_category=None):
    return Task(
        id=id_,
        user_request=f"request {id_}",
        selected_capability=capability,
        status=status,
        failure_category=failure_category,
    )


def _log_with_capability_failures() -> ExperienceLog:
    log = ExperienceLog()
    # CAP-002: 4 uses, 1 success, 3 failures -> 75% failure rate.
    log.add_task(_task("t1", status="success", capability="CAP-002"))
    log.add_task(
        _task(
            "t2",
            status="failure",
            capability="CAP-002",
            failure_category="Pattern mismatch",
        )
    )
    log.add_task(
        _task(
            "t3",
            status="failure",
            capability="CAP-002",
            failure_category="Pattern mismatch",
        )
    )
    log.add_task(
        _task("t4", status="failure", capability="CAP-002", failure_category="Timeout")
    )
    # CAP-003: 3 uses, all success.
    log.add_task(_task("t5", status="success", capability="CAP-003"))
    log.add_task(_task("t6", status="success", capability="CAP-003"))
    log.add_task(_task("t7", status="success", capability="CAP-003"))
    return log


def test_analyze_failure_patterns_delegates_to_experience_log():
    log = _log_with_capability_failures()
    learner = MetaLearner()
    assert learner.analyze_failure_patterns(log) == {
        "Pattern mismatch": 2,
        "Timeout": 1,
    }


def test_detect_capability_failure_true_above_threshold():
    log = _log_with_capability_failures()
    learner = MetaLearner()
    assert learner.detect_capability_failure(log, "CAP-002") is True


def test_detect_capability_failure_false_below_min_occurrences():
    log = ExperienceLog()
    log.add_task(
        _task("t1", status="failure", capability="CAP-005", failure_category="X")
    )
    learner = MetaLearner()
    # Only 1 occurrence, default min_occurrences=3.
    assert learner.detect_capability_failure(log, "CAP-005") is False


def test_detect_capability_failure_false_when_success_rate_healthy():
    log = _log_with_capability_failures()
    learner = MetaLearner()
    assert learner.detect_capability_failure(log, "CAP-003") is False


def test_recommend_strategy_change_picks_best_alternative():
    log = _log_with_capability_failures()
    learner = MetaLearner()
    recommendation = learner.recommend_strategy_change(log, "CAP-002")
    assert recommendation == "CAP-003"


def test_recommend_strategy_change_no_data_returns_explanatory_string():
    log = ExperienceLog()
    log.add_task(
        _task("t1", status="failure", capability="CAP-002", failure_category="X")
    )
    learner = MetaLearner()
    recommendation = learner.recommend_strategy_change(log, "CAP-002")
    assert "CAP-002" in recommendation
    assert "No alternative" in recommendation


def test_measure_improvement_positive():
    log = ExperienceLog()
    for i in range(10):
        status = "success" if i < 7 else "failure"
        log.add_task(_task(f"t{i}", status=status))
    learner = MetaLearner()
    improvement = learner.measure_improvement(log, baseline_success_rate=0.5)
    assert improvement == pytest.approx(40.0)


def test_measure_improvement_zero_baseline_uses_current_rate():
    log = ExperienceLog()
    log.add_task(_task("t1", status="success"))
    learner = MetaLearner()
    improvement = learner.measure_improvement(log, baseline_success_rate=0.0)
    assert improvement == pytest.approx(100.0)


def test_decision_log_round_trip(tmp_path):
    decision = MetaLearningDecision(
        decision_id="MLD_001",
        triggered_by="CAP-002 failure rate >20%",
        previous_strategy="Always try CAP-002 first",
        new_strategy="Try CAP-003 first",
        rationale="Higher observed success rate",
    )
    decision_log = MetaLearningDecisionLog()
    decision_log.add_decision(decision)

    out_path = tmp_path / "meta_learning_decisions.json"
    decision_log.save_to_json(out_path)
    assert out_path.exists()

    reloaded = MetaLearningDecisionLog.load_from_json(out_path)
    assert len(reloaded.decisions) == 1
    assert reloaded.decisions[0].decision_id == "MLD_001"


def test_decision_log_load_missing_file_returns_empty(tmp_path):
    decision_log = MetaLearningDecisionLog.load_from_json(tmp_path / "missing.json")
    assert decision_log.decisions == []
