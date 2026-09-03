from layers.layer_05_experience import ExperienceLog, Task
from layers.layer_06_meta_learning import OptimizationCycleConfig, OptimizationCycleController
from layers.layer_08_evolution import CapabilityPlan, EvolutionActionPlan, EvolutionExecutionAuthority
from core.optimization_cycle_service import OptimizationCycleService
from evaluation.self_improvement_benchmark import SelfImprovementBenchmark


class FakeEvolution:
    def __init__(self):
        self.calls = []

    def develop_capability_for_gap(self, plan, *, project_root="."):
        self.calls.append(plan.capability_id)
        return {
            "capability_id": plan.capability_id,
            "candidate_created": True,
            "promoted": True,
            "registered": True,
            "test_result": {"passed": True},
        }


def _task(task_id, status, capability="CAP-011"):
    return Task(
        id=task_id,
        user_request="improve capability behavior",
        target_project="sps-ca",
        target_language="python",
        status=status,
        selected_capability=capability,
        time_taken_seconds=1.0,
    )


def test_trigger_authorize_evolve_and_measure_improvement(tmp_path):
    baseline = ExperienceLog([_task(str(i), "failure") for i in range(1, 6)])
    controller = OptimizationCycleController(
        config=OptimizationCycleConfig(
            minimum_total_observations=5,
            minimum_failure_rate=0.30,
            minimum_capability_observations=5,
            minimum_capability_score=0.90,
            cooldown_seconds=0,
        )
    )
    evolution = FakeEvolution()
    service = OptimizationCycleService(
        experience=baseline,
        controller=controller,
        evolution=evolution,
        execution_authority=EvolutionExecutionAuthority(
            enabled=True,
            max_actions_per_cycle=1,
            source="deterministic-benchmark",
        ),
        state_path=str(tmp_path / "optimization.json"),
    )

    cycle = service.assess_after_task(["CAP-011"])
    assert cycle.triggered is True

    action = EvolutionActionPlan(
        cycle_id=cycle.cycle_id,
        triggered=True,
        source_capabilities=["CAP-011"],
        capability_plans=[CapabilityPlan(
            capability_id="CAP-012",
            name="Improved benchmark capability",
            description="Improve benchmark behavior",
            entry_point="capabilities.generated.cap_012.capability:run",
            supported_languages=["python"],
        )],
        rationale=["CAP-011 underperformed"],
    )
    execution = service.execute_authorized_action_plan(action, project_root=str(tmp_path))
    assert execution[0]["authorized"] is True
    assert execution[0]["executed"] is True
    assert evolution.calls == ["CAP-012"]

    improved_experience = ExperienceLog([_task(str(i), "success", "CAP-012") for i in range(6, 11)])
    benchmark = SelfImprovementBenchmark(minimum_score_delta=0.05)
    result = benchmark.measure(
        capability_id="CAP-012",
        baseline_experience=ExperienceLog([_task(str(i), "failure", "CAP-012") for i in range(1, 6)]),
        post_evolution_experience=improved_experience,
        evolution_result=execution[0]["result"],
    )
    assert result.promotion_succeeded is True
    assert result.improved is True
    assert result.score_delta >= 0.05
