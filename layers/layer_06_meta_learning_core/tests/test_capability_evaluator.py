from layers.layer_05_experience import ExperienceLog, Task
from layers.layer_06_meta_learning import CapabilityEvaluator


def _task(task_id, capability, status, seconds=1.0):
    return Task(
        id=task_id,
        user_request=f"request {task_id}",
        status=status,
        selected_capability=capability,
        time_taken_seconds=seconds,
    )


def test_evaluator_is_neutral_without_observations():
    evaluation = CapabilityEvaluator().evaluate(ExperienceLog(), "CAP-011")
    assert evaluation.observations == 0
    assert evaluation.confidence == 0.0
    assert evaluation.score == 0.0


def test_evaluator_rewards_success_and_penalizes_slow_latency():
    fast_log = ExperienceLog([
        _task("1", "CAP-011", "success", 1),
        _task("2", "CAP-011", "success", 1),
        _task("3", "CAP-011", "success", 1),
    ])
    slow_log = ExperienceLog([
        _task("1", "CAP-012", "success", 60),
        _task("2", "CAP-012", "success", 60),
        _task("3", "CAP-012", "success", 60),
    ])
    fast = CapabilityEvaluator().evaluate(fast_log, "CAP-011")
    slow = CapabilityEvaluator().evaluate(slow_log, "CAP-012")
    assert fast.score > slow.score


def test_rank_ignores_capabilities_without_minimum_evidence():
    log = ExperienceLog([
        _task("1", "CAP-011", "success"),
        _task("2", "CAP-012", "success"),
        _task("3", "CAP-012", "success"),
        _task("4", "CAP-012", "success"),
    ])
    ranked = CapabilityEvaluator().rank(log, ["CAP-011", "CAP-012"], min_observations=3)
    assert [item.capability_id for item in ranked] == ["CAP-012"]


def test_choose_best_returns_highest_observed_score():
    log = ExperienceLog([
        _task("1", "CAP-011", "failure"),
        _task("2", "CAP-011", "success"),
        _task("3", "CAP-011", "failure"),
        _task("4", "CAP-012", "success"),
        _task("5", "CAP-012", "success"),
        _task("6", "CAP-012", "partial"),
    ])
    assert CapabilityEvaluator().choose_best(log, ["CAP-011", "CAP-012"], min_observations=3) == "CAP-012"
