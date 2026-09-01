"""End-to-end Phase 4 evolution-cycle tests.

Uses deterministic fakes so the thesis prototype can verify the complete
control flow without requiring a running Ollama server.
"""
from pathlib import Path

from layers.layer_03_experience.experience_log import ExperienceLog
from layers.layer_03_experience.models import Task
from layers.layer_07_governance import GovernanceGate
from layers.layer_08_evolution import EvolutionEngine, EvolutionWorkflow
from layers.layer_09_capability_registry import CapabilityRegistry
from models.base import LLMProvider, LLMRequest, LLMResponse


class FakeProvider(LLMProvider):
    name = "fake"

    def is_available(self) -> bool:
        return True

    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            text=(
                "def solve_parser_failure(value):\n"
                "    return value.strip()\n"
            ),
            model="fake-model",
            provider=self.name,
            raw={},
        )


def _history() -> ExperienceLog:
    log = ExperienceLog()
    for i in range(1, 4):
        log.add_task(
            Task(
                id=f"e2e_{i}",
                user_request="Fix parser failure",
                target_project="demo",
                target_language="python",
                status="failure",
                selected_capability="CAP-001",
                outcome="failed",
                failure_category="parser_failure",
            )
        )
    return log


def test_phase4_cycle_stops_before_promotion_without_approval(tmp_path: Path):
    engine = EvolutionEngine(provider=FakeProvider(), staging_root=tmp_path / "staging")
    registry = CapabilityRegistry(path=tmp_path / "registry.json")
    workflow = EvolutionWorkflow(engine, GovernanceGate(), registry)

    result = workflow.evolve(_history(), evidence=["three recurring failures"])

    assert result.test_results.passed
    assert result.governance_status.value in {"AUTO_APPROVED", "APPROVED", "REQUIRES_HUMAN_REVIEW"}
    # A governed evolution must never promote merely because validation passed.
    assert result.promoted_path is None
    assert not result.registered


def test_phase4_cycle_promotes_and_registers_when_explicitly_approved(tmp_path: Path):
    engine = EvolutionEngine(provider=FakeProvider(), staging_root=tmp_path / "staging")
    registry = CapabilityRegistry(path=tmp_path / "registry.json")
    workflow = EvolutionWorkflow(engine, GovernanceGate(), registry)

    result = workflow.evolve(
        _history(), evidence=["three recurring failures"], approved=True
    )

    assert result.test_results.passed
    assert result.promoted_path is not None
    assert result.promoted_path.exists()
    assert result.registered
    assert registry.get(result.capability_id) is not None
