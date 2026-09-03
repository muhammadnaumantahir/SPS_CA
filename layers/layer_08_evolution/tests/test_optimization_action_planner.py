from datetime import datetime, timezone

from layers.layer_05_experience import ExperienceLog, Task
from layers.layer_06_meta_learning import OptimizationCycleConfig, OptimizationCycleController
from layers.layer_08_evolution import OptimizationActionPlanner


def _task(task_id: str, capability: str, status: str) -> Task:
    return Task(
        id=task_id,
        user_request=f"request {task_id}",
        target_project="chat",
        target_language="python",
        status=status,
        selected_capability=capability,
        time_taken_seconds=1.0,
    )


def _triggered_plan():
    log = ExperienceLog([
        _task("1", "CAP-011", "failure"),
        _task("2", "CAP-011", "failure"),
        _task("3", "CAP-011", "failure"),
        _task("4", "CAP-011", "failure"),
        _task("5", "CAP-011", "success"),
    ])
    controller = OptimizationCycleController(
        config=OptimizationCycleConfig(
            minimum_total_observations=5,
            minimum_failure_rate=0.30,
            minimum_capability_observations=5,
            minimum_capability_score=0.90,
            cooldown_seconds=60,
        )
    )
    return controller.assess(
        log,
        ["CAP-011"],
        now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        cycle_id="OPT-TEST-001",
    )


def test_planner_does_not_create_actions_for_non_triggered_cycle():
    log = ExperienceLog([_task("1", "CAP-011", "success")])
    controller = OptimizationCycleController()
    plan = controller.assess(
        log,
        ["CAP-011"],
        now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        cycle_id="OPT-TEST-EMPTY",
    )
    action_plan = OptimizationActionPlanner().plan(
        plan,
        task_description="improve request handling",
        language="python",
    )
    assert action_plan.triggered is False
    assert action_plan.capability_plans == []


def test_planner_converts_underperformance_into_explicit_layer8_plan():
    plan = _triggered_plan()
    action_plan = OptimizationActionPlanner().plan(
        plan,
        task_description="improve request handling",
        language="python",
    )
    assert action_plan.triggered is True
    assert action_plan.cycle_id == "OPT-TEST-001"
    assert action_plan.source_capabilities == ["CAP-011"]
    assert len(action_plan.capability_plans) == 1
    assert action_plan.capability_plans[0].capability_id.startswith("CAP-")
    assert action_plan.capability_plans[0].provenance["trigger"] == "capability_gap"
