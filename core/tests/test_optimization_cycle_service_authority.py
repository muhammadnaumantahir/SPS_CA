from layers.layer_05_experience import ExperienceLog
from layers.layer_08_evolution import CapabilityPlan, EvolutionActionPlan, EvolutionExecutionAuthority
from core.optimization_cycle_service import OptimizationCycleService


class FakeEvolution:
    def __init__(self):
        self.calls = []

    def develop_capability_for_gap(self, plan, *, project_root="."):
        self.calls.append((plan.capability_id, project_root))
        return {
            "capability_id": plan.capability_id,
            "registered": True,
            "promoted": True,
        }


def _action():
    plan = CapabilityPlan(
        capability_id="CAP-011",
        name="Test capability",
        description="Test",
        entry_point="capabilities.generated.cap_011.capability:run",
        supported_languages=["python"],
    )
    return EvolutionActionPlan(
        cycle_id="OPT-TEST-AUTH",
        triggered=True,
        source_capabilities=["CAP-010"],
        capability_plans=[plan],
        rationale=["underperforming"],
    )


def test_authorized_action_executes_through_evolution(tmp_path):
    evolution = FakeEvolution()
    service = OptimizationCycleService(
        experience=ExperienceLog(),
        evolution=evolution,
        execution_authority=EvolutionExecutionAuthority(enabled=True, max_actions_per_cycle=1, source="test"),
        state_path=str(tmp_path / "state.json"),
    )
    result = service.execute_authorized_action_plan(_action(), project_root=str(tmp_path))
    assert result[0]["authorized"] is True
    assert result[0]["executed"] is True
    assert evolution.calls == [("CAP-011", str(tmp_path))]


def test_unauthorized_action_does_not_execute(tmp_path):
    evolution = FakeEvolution()
    service = OptimizationCycleService(
        experience=ExperienceLog(),
        evolution=evolution,
        execution_authority=EvolutionExecutionAuthority(enabled=False, max_actions_per_cycle=1, source="test"),
        state_path=str(tmp_path / "state.json"),
    )
    result = service.execute_authorized_action_plan(_action(), project_root=str(tmp_path))
    assert result[0]["authorized"] is False
    assert result[0]["executed"] is False
    assert evolution.calls == []
