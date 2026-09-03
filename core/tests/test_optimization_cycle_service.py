from datetime import datetime, timedelta, timezone

from core.optimization_cycle_service import OptimizationCycleService
from layers.layer_05_experience import ExperienceLog, Task
from layers.layer_06_meta_learning import OptimizationCycleConfig, OptimizationCycleController


def _task(index, capability, status):
    return Task(
        id=str(index),
        user_request=f"request {index}",
        target_language="python",
        status=status,
        selected_capability=capability,
        time_taken_seconds=1.0,
    )


def test_service_triggers_and_persists_state(tmp_path):
    log = ExperienceLog([_task(i, "CAP-011", "failure" if i < 5 else "success") for i in range(10)])
    controller = OptimizationCycleController(
        config=OptimizationCycleConfig(
            minimum_total_observations=10,
            minimum_failure_rate=0.30,
            minimum_capability_observations=5,
            minimum_capability_score=0.35,
            cooldown_seconds=300,
        )
    )
    service = OptimizationCycleService(
        experience=log,
        controller=controller,
        state_path=str(tmp_path / "state.json"),
    )
    plan = service.assess_after_task(["CAP-011"])
    assert plan.triggered is True
    assert plan.cycle_id.startswith("OPT-")
    assert (tmp_path / "state.json").exists()


def test_service_honors_cooldown(tmp_path):
    log = ExperienceLog([_task(i, "CAP-011", "failure" if i < 5 else "success") for i in range(10)])
    controller = OptimizationCycleController(
        config=OptimizationCycleConfig(minimum_total_observations=10, minimum_failure_rate=0.30, cooldown_seconds=300)
    )
    state = tmp_path / "state.json"
    state.write_text(
        '{"last_cycle_at": "2026-09-03T09:45:00+00:00", "last_cycle_id": "OPT-prev"}\n',
        encoding="utf-8",
    )
    service = OptimizationCycleService(experience=log, controller=controller, state_path=str(state))
    plan = service.assess_after_task(["CAP-011"])
    assert plan.triggered is False
    assert "cooldown_active" in plan.reasons
