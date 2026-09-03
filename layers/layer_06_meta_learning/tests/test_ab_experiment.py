from layers.layer_05_experience import ExperienceLog, Task
from layers.layer_06_meta_learning import ABComparisonEngine


def _task(task_id, capability, status, seconds=1.0):
    return Task(
        id=task_id,
        user_request=f"request {task_id}",
        status=status,
        selected_capability=capability,
        time_taken_seconds=seconds,
    )


def test_ab_assignment_is_deterministic():
    engine = ABComparisonEngine()
    first = engine.assign_arm("exp-1", "task-42")
    assert first in {"A", "B"}
    assert engine.assign_arm("exp-1", "task-42") == first
    assert engine.assign_arm("exp-2", "task-42") != first or engine.assign_arm("exp-2", "task-43") in {"A", "B"}


def test_ab_comparison_requires_minimum_evidence():
    log = ExperienceLog([
        _task("1", "CAP-010", "success"),
        _task("2", "CAP-011", "success"),
        _task("3", "CAP-011", "success"),
        _task("4", "CAP-011", "success"),
    ])
    result = ABComparisonEngine().compare(
        log,
        experiment_id="exp-1",
        control_capability_id="CAP-010",
        treatment_capability_id="CAP-011",
        min_observations_per_arm=3,
    )
    assert result.evidence_sufficient is False
    assert result.winner is None


def test_ab_comparison_selects_clear_winner_after_balanced_evidence():
    log = ExperienceLog([
        _task("a1", "CAP-010", "success"),
        _task("a2", "CAP-010", "partial"),
        _task("a3", "CAP-010", "failure"),
        _task("a4", "CAP-010", "success"),
        _task("a5", "CAP-010", "failure"),
        _task("b1", "CAP-011", "success"),
        _task("b2", "CAP-011", "success"),
        _task("b3", "CAP-011", "success"),
        _task("b4", "CAP-011", "partial"),
        _task("b5", "CAP-011", "success"),
    ])
    result = ABComparisonEngine().compare(
        log,
        experiment_id="exp-2",
        control_capability_id="CAP-010",
        treatment_capability_id="CAP-011",
        min_observations_per_arm=5,
        min_score_margin=0.08,
    )
    assert result.balanced is True
    assert result.evidence_sufficient is True
    assert result.winner == "CAP-011"
    assert result.score_margin >= 0.08
