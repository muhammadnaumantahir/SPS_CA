from datetime import datetime, timezone, timedelta

from layers.layer_05_experience import ExperienceLog, Task
from layers.layer_06_meta_learning.optimization_cycle import (
    OptimizationCycleConfig,
    OptimizationCycleController,
)


def _task(task_id, capability, status):
    return Task(
        id=task_id,
        user_request=f"request {task_id}",
        status=status,
        selected_capability=capability,
        time_taken_seconds=1.0,
    )


def test_cycle_does_not_trigger_before_thresholds():
    log = ExperienceLog([_task(str(i), "CAP-011", "failure") for i in range(4)])
    controller = OptimizationCycleController()
    plan = controller.assess(log, ["CAP-011"], cycle_id="OPT-TEST-1")
    assert plan.triggered is False
    assert plan.reasons == []


def test_cycle_triggers_on_failure_threshold():
    log = ExperienceLog([_task(str(i), "CAP-011", "failure") for i in range(10)])
    controller = OptimizationCycleController()
    plan = controller.assess(log, ["CAP-011"], cycle_id="OPT-TEST-2")
    assert plan.triggered is True
    assert "minimum_total_observations" in plan.reasons
    assert "failure_rate_threshold" in plan.reasons


def test_cycle_reports_underperforming_capability():
    log = ExperienceLog([_task(str(i), "CAP-011", "failure") for i in range(5)])
    config = OptimizationCycleConfig(minimum_total_observations=100)
    plan = OptimizationCycleController(config=config).assess(log, ["CAP-011"], cycle_id="OPT-TEST-3")
    assert plan.triggered is True
    assert "underperforming_capability" in plan.reasons
    assert plan.candidates[0].capability_id == "CAP-011"


def test_cycle_cooldown_blocks_trigger():
    log = ExperienceLog([_task(str(i), "CAP-011", "failure") for i in range(10)])
    config = OptimizationCycleConfig(cooldown_seconds=300)
    controller = OptimizationCycleController(config=config)
    now = datetime(2026, 9, 3, 14, 0, tzinfo=timezone.utc)
    plan = controller.assess(
        log,
        ["CAP-011"],
        now=now,
        last_cycle_at=now - timedelta(seconds=60),
        cycle_id="OPT-TEST-4",
    )
    assert plan.triggered is False
    assert "cooldown_active" in plan.reasons
