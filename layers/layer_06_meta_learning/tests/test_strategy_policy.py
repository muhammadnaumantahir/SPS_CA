"""Tests for the Phase 2 evidence-based strategy policy."""

from __future__ import annotations

from layers.layer_05_experience.experience_log import ExperienceLog
from layers.layer_05_experience.models import Task
from layers.layer_06_meta_learning.strategy_policy import StrategyPolicy


def _task(task_id: str, capability: str, status: str, seconds: float = 1.0) -> Task:
    return Task(
        id=task_id,
        user_request=f"request {task_id}",
        selected_capability=capability,
        status=status,
        time_taken_seconds=seconds,
        failure_category="x" if status == "failure" else None,
    )


def test_recommends_clear_winner_with_sufficient_evidence():
    log = ExperienceLog()
    for i in range(4):
        log.add_task(_task(f"bad-{i}", "CAP-002", "failure", 10.0))
    for i in range(4):
        log.add_task(_task(f"good-{i}", "CAP-011", "success", 1.0))

    result = StrategyPolicy().recommend(log, "CAP-002", ["CAP-011"])

    assert result.recommended_capability_id == "CAP-011"
    assert result.evidence_sufficient is True
    assert result.score_margin >= 0.08


def test_rejects_switch_when_evidence_is_too_small():
    log = ExperienceLog()
    log.add_task(_task("a", "CAP-002", "failure"))
    log.add_task(_task("b", "CAP-011", "success"))

    result = StrategyPolicy().recommend(log, "CAP-002", ["CAP-011"])

    assert result.recommended_capability_id is None
    assert result.evidence_sufficient is False


def test_rejects_switch_when_margin_is_too_small():
    log = ExperienceLog()
    for i in range(6):
        log.add_task(_task(f"current-{i}", "CAP-002", "success", 1.0))
        log.add_task(_task(f"alt-{i}", "CAP-011", "success", 1.0))

    result = StrategyPolicy().recommend(log, "CAP-002", ["CAP-011"])

    assert result.recommended_capability_id is None
    assert result.evidence_sufficient is True
    assert "minimum score margin" in result.reason
