from layers.layer_05_experience import ExperienceLog
from layers.layer_08_evolution import CapabilityPlan, EvolutionActionPlan, EvolutionExecutionAuthority
from core.optimization_cycle_service import OptimizationCycleService


class FakeEvolution:
    def develop_capability_for_gap(self, plan, *, project_root="."):
        return {
            "capability_id": plan.capability_id,
            "registered": True,
            "promoted": True,
            "rolled_back": False,
        }


def _action():
    plan = CapabilityPlan(
        capability_id="CAP-012",
        name="benchmark capability",
        description="benchmark",
        entry_point="capabilities.generated.cap_012.capability:run",
        supported_languages=["python"],
    )
    return EvolutionActionPlan(
        cycle_id="OPT-EVIDENCE-001",
        triggered=True,
        source_capabilities=["CAP-011"],
        capability_plans=[plan],
        rationale=["underperforming"],
    )


def test_promotion_does_not_create_fake_capability_performance_observation(tmp_path):
    experience = ExperienceLog()
    service = OptimizationCycleService(
        experience=experience,
        evolution=FakeEvolution(),
        execution_authority=EvolutionExecutionAuthority(enabled=True, max_actions_per_cycle=1, source="test"),
        state_path=str(tmp_path / "state.json"),
    )

    result = service.execute_authorized_action_plan(_action(), project_root=str(tmp_path))

    assert result[0]["executed"] is True
    assert len(experience.tasks) == 0
    state = (tmp_path / "state.json").read_text(encoding="utf-8")
    assert "evolution_outcome" in state
