"""End-to-end Phase 4 evolution-cycle tests.

Uses deterministic fakes so the thesis prototype can verify the complete
control flow without requiring a running Ollama server.
"""
import json
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
        capability = '''from capabilities.base import CapabilityContext, CapabilityResult

def solve_parser_failure(value):
    if value is None:
        return ""
    return str(value).strip()

def run(context: CapabilityContext) -> CapabilityResult:
    value = solve_parser_failure(context.code)
    return CapabilityResult.ok(summary="parsed", findings=[{"value": value}])
'''
        tests = '''from capabilities.base import CapabilityContext
from capability import run, solve_parser_failure

def test_none():
    assert solve_parser_failure(None) == ""

def test_trim():
    assert solve_parser_failure(" value ") == "value"

def test_run():
    result = run(CapabilityContext(code=" value ", language="python"))
    assert result.success
    assert result.findings[0]["value"] == "value"
'''
        return LLMResponse(
            text=json.dumps({
                "capability_py": capability,
                "tests_py": tests,
                "readme_md": "Generated parser capability.",
            }),
            model="fake-model",
            provider=self.name,
            raw={},
        )


def _history() -> ExperienceLog:
    log = ExperienceLog()
    for i in range(1, 4):
        log.add_task(Task(
            id=f"e2e_{i}",
            user_request="Fix parser failure",
            target_project="demo",
            target_language="python",
            status="failure",
            selected_capability="CAP-001",
            outcome="failed",
            failure_category="parser_failure",
        ))
    return log


def test_phase4_cycle_stops_before_promotion_without_approval(tmp_path: Path):
    engine = EvolutionEngine(
        provider=FakeProvider(),
        pending_root=str(tmp_path / "staging"),
        generated_root=str(tmp_path / "generated"),
    )
    registry = CapabilityRegistry(registry_path=str(tmp_path / "registry.json"))
    workflow = EvolutionWorkflow(engine, GovernanceGate(), registry)

    result = workflow.evolve(_history(), evidence=["three recurring failures"])

    assert result.test_results.passed
    assert result.governance_status.value in {"AUTO_APPROVED", "APPROVED", "REQUIRES_HUMAN_REVIEW"}
    assert result.promoted_path is None
    assert not result.registered


def test_phase4_cycle_promotes_and_registers_when_explicitly_approved(tmp_path: Path):
    engine = EvolutionEngine(
        provider=FakeProvider(),
        pending_root=str(tmp_path / "staging"),
        generated_root=str(tmp_path / "generated"),
    )
    registry = CapabilityRegistry(registry_path=str(tmp_path / "registry.json"))
    workflow = EvolutionWorkflow(engine, GovernanceGate(), registry)

    result = workflow.evolve(_history(), evidence=["three recurring failures"], approved=True)

    assert result.test_results.passed
    assert result.promoted_path is not None
    assert result.promoted_path.exists()
    assert result.registered
    assert registry.get(result.capability_id) is not None
