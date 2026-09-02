from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from layers.layer_03_experience.experience_log import ExperienceLog
from layers.layer_03_experience.models import Task
from layers.layer_07_governance.governance import GovernanceGate
from layers.layer_07_governance.models import ChangeType, DecisionStatus
from layers.layer_08_evolution.evolution_engine import EvolutionEngine, EvolutionError
from layers.layer_08_evolution.models import CapabilityPlan, EvolutionTrigger, TestRunResult

REPO_ROOT = Path(__file__).resolve().parents[3]


def _failing_log(pattern: str = "Parse error", count: int = 3, capability: str = "CAP-001"):
    log = ExperienceLog()
    for i in range(count):
        log.add_task(
            Task(
                id=f"task_{i:03d}",
                user_request="parse the file",
                status="failure",
                failure_category=pattern,
                selected_capability=capability,
            )
        )
    return log


@pytest.fixture
def hermetic_project(tmp_path: Path) -> Path:
    """A minimal, isolated project root containing a real ``capabilities`` package.

    Generated capabilities import ``from capabilities.base import ...``, so
    the sandbox test run needs a real ``capabilities/base.py`` reachable
    from ``project_root`` -- copied from the actual repo rather than the
    real ``capabilities/generated/`` so tests never touch repo files.
    """
    caps_dir = tmp_path / "capabilities"
    caps_dir.mkdir()
    (caps_dir / "__init__.py").write_text("", encoding="utf-8")
    shutil.copy(REPO_ROOT / "capabilities" / "base.py", caps_dir / "base.py")
    return tmp_path


@pytest.fixture
def engine(hermetic_project: Path) -> EvolutionEngine:
    return EvolutionEngine(
        generated_dir=str(hermetic_project / "capabilities" / "generated"),
        seeds_dir=str(hermetic_project / "capabilities" / "seeds"),
        registry_path=str(hermetic_project / "capabilities" / "registry.json"),
        evaluation_dir=str(hermetic_project / "evaluation" / "evolution"),
    )


class TestShouldEvolve:
    def test_true_when_pattern_meets_threshold(self, engine: EvolutionEngine):
        log = _failing_log(count=3)
        assert engine.should_evolve(log) is True

    def test_false_when_below_threshold(self, engine: EvolutionEngine):
        log = _failing_log(count=2)
        assert engine.should_evolve(log) is False

    def test_false_on_empty_log(self, engine: EvolutionEngine):
        assert engine.should_evolve(ExperienceLog()) is False

    def test_respects_custom_min_occurrences(self, engine: EvolutionEngine):
        log = _failing_log(count=4)
        assert engine.should_evolve(log, min_occurrences=5) is False
        assert engine.should_evolve(log, min_occurrences=4) is True


class TestGetTriggerPatterns:
    def test_returns_trigger_with_task_ids(self, engine: EvolutionEngine):
        log = _failing_log(pattern="Parse error", count=3)
        triggers = engine.get_trigger_patterns(log)
        assert len(triggers) == 1
        assert triggers[0].pattern == "Parse error"
        assert triggers[0].occurrence_count == 3
        assert triggers[0].trigger_task_ids == ["task_000", "task_001", "task_002"]

    def test_excludes_patterns_below_threshold(self, engine: EvolutionEngine):
        log = _failing_log(pattern="Parse error", count=2)
        assert engine.get_trigger_patterns(log) == []

    def test_sorted_most_frequent_first(self, engine: EvolutionEngine):
        log = _failing_log(pattern="Parse error", count=5)
        for i in range(3):
            log.add_task(
                Task(
                    id=f"type_{i}",
                    user_request="check types",
                    status="failure",
                    failure_category="Type mismatch",
                )
            )
        triggers = engine.get_trigger_patterns(log)
        assert [t.pattern for t in triggers] == ["Parse error", "Type mismatch"]


class TestPlanNewCapability:
    def test_plan_uses_next_capability_id_by_default(self, engine: EvolutionEngine):
        trigger = EvolutionTrigger(pattern="Parse error", occurrence_count=3, trigger_task_ids=["t1"])
        plan = engine.plan_new_capability(trigger)
        assert plan.capability_id == "CAP-009"
        assert plan.entry_point == "capabilities.generated.cap_010.capability.run"
        assert plan.trigger_pattern == "Parse error"
        assert len(plan.test_case_names) == 3

    def test_plan_respects_explicit_capability_id(self, engine: EvolutionEngine):
        trigger = EvolutionTrigger(pattern="Parse error", occurrence_count=3)
        plan = engine.plan_new_capability(trigger, capability_id="CAP-050")
        assert plan.capability_id == "CAP-050"

    def test_plan_respects_custom_languages(self, engine: EvolutionEngine):
        trigger = EvolutionTrigger(pattern="Parse error", occurrence_count=3)
        plan = engine.plan_new_capability(trigger, supported_languages=["python", "java"])
        assert plan.supported_languages == ["python", "java"]


class TestNextCapabilityId:
    def test_starts_at_cap_009_with_no_seeds_or_generated(self, engine: EvolutionEngine):
        assert engine.next_capability_id() == "CAP-009"

    def test_skips_ids_already_used_by_seeds(self, engine: EvolutionEngine):
        seed_dir = engine.seeds_dir / "cap_009_something"
        seed_dir.mkdir(parents=True)
        (seed_dir / "metadata.json").write_text(json.dumps({"id": "CAP-009"}), encoding="utf-8")
        assert engine.next_capability_id() == "CAP-010"

    def test_skips_ids_already_used_by_generated_capabilities(self, engine: EvolutionEngine):
        gen_dir = engine.generated_dir / "cap_009"
        gen_dir.mkdir(parents=True)
        (gen_dir / "metadata.json").write_text(json.dumps({"id": "CAP-009"}), encoding="utf-8")
        assert engine.next_capability_id() == "CAP-010"

    def test_fills_gaps(self, engine: EvolutionEngine):
        for cap_id in ("CAP-009", "CAP-011"):
            gen_dir = engine.generated_dir / cap_id.lower().replace("-", "_")
            gen_dir.mkdir(parents=True)
            (gen_dir / "metadata.json").write_text(json.dumps({"id": cap_id}), encoding="utf-8")
        assert engine.next_capability_id() == "CAP-010"


class TestGenerateCapabilityCode:
    def _plan(self):
        return CapabilityPlan(
            capability_id="CAP-009",
            name="Parse Error Handler",
            description="Generated from repeated Parse error failures.",
            entry_point="capabilities.generated.cap_010.capability.run",
            trigger_pattern="Parse error",
            trigger_task_ids=["task_000", "task_001", "task_002"],
        )

    def test_generated_code_is_syntactically_valid(self, engine: EvolutionEngine):
        files = engine.generate_capability_code(self._plan())
        compile(files.capability_code, "capability.py", "exec")
        compile(files.tests_code, "tests.py", "exec")

    def test_metadata_has_required_fields(self, engine: EvolutionEngine):
        files = engine.generate_capability_code(self._plan())
        assert files.metadata["id"] == "CAP-009"
        assert files.metadata["generated"] is True
        assert files.metadata["failure_pattern"] == "Parse error"
        assert files.metadata["trigger_tasks"] == ["task_000", "task_001", "task_002"]
        assert files.metadata["entry_point"] == "capabilities.generated.cap_010.capability.run"

    def test_readme_mentions_trigger(self, engine: EvolutionEngine):
        files = engine.generate_capability_code(self._plan())
        assert "Parse error" in files.readme


class TestImplementCapability:
    def test_writes_all_expected_files(self, engine: EvolutionEngine):
        plan = CapabilityPlan(
            capability_id="CAP-009",
            name="Parse Error Handler",
            description="desc",
            entry_point="capabilities.generated.cap_010.capability.run",
            trigger_pattern="Parse error",
        )
        files = engine.generate_capability_code(plan)
        module_dir = engine.implement_capability(plan, files)

        assert module_dir == engine.generated_dir / "cap_009"
        for name in ("__init__.py", "capability.py", "tests.py", "metadata.json", "README.md"):
            assert (module_dir / name).exists()
        assert (engine.generated_dir / "__init__.py").exists()

        saved_metadata = json.loads((module_dir / "metadata.json").read_text())
        assert saved_metadata["id"] == "CAP-009"


class TestFullCycle:
    """End-to-end tests that actually run the generated tests in a subprocess sandbox."""

    def _run(self, engine: EvolutionEngine, project_root: Path, governance_gate=None):
        engine.governance_gate = governance_gate
        log = _failing_log(count=3)
        return engine.run_evolution_cycle(log, project_root=str(project_root))

    def test_full_cycle_generates_tests_and_registers(
        self, engine: EvolutionEngine, hermetic_project: Path
    ):
        record = self._run(engine, hermetic_project)

        assert record is not None
        assert record.capability_id == "CAP-009"
        assert record.test_result.passed is True
        assert record.test_result.tests_run == 3
        assert record.test_result.tests_failed == 0
        assert record.test_result.coverage_percent == 100.0
        assert record.registered is True
        assert "EVOLUTION: CAP-009" in record.commit_message

        registry = json.loads(engine.registry_path.read_text())
        assert "CAP-009" in registry
        assert registry["CAP-009"]["test_coverage"] == 100.0

        record_path = engine.evaluation_dir / "CAP-009.json"
        assert record_path.exists()

    def test_full_cycle_returns_none_when_nothing_triggers(self, engine: EvolutionEngine):
        assert engine.run_evolution_cycle(ExperienceLog()) is None

    def test_full_cycle_goes_through_governance_and_records_decision(
        self, engine: EvolutionEngine, hermetic_project: Path
    ):
        gate = GovernanceGate(
            dna_rules_path=str(hermetic_project / "does_not_exist.json"),
            decisions_dir=str(hermetic_project / "governance" / "decisions"),
        )
        record = self._run(engine, hermetic_project, governance_gate=gate)

        assert record.governance_decision_id is not None
        decision = gate.get_decision(record.governance_decision_id)
        assert decision is not None
        assert decision.change_type == ChangeType.EVOLUTION
        # A brand-new generated module doesn't match any mechanical DNA
        # rule's affected_files globs, so it should clear governance.
        assert decision.decision != DecisionStatus.REJECTED
        assert record.registered is True

    def test_registration_skipped_when_governance_rejects(
        self, engine: EvolutionEngine, hermetic_project: Path
    ):
        # gov_mech_002 rejects any change touching capabilities/seeds/*/capability.py.
        gate = GovernanceGate(
            dna_rules_path=str(hermetic_project / "does_not_exist.json"),
            decisions_dir=str(hermetic_project / "governance" / "decisions"),
        )
        log = _failing_log(count=3)
        engine.governance_gate = gate
        triggers = engine.get_trigger_patterns(log)
        plan = engine.plan_new_capability(triggers[0])
        files = engine.generate_capability_code(plan)
        engine.implement_capability(plan, files)
        test_result = engine.test_capability(plan.capability_id, project_root=str(hermetic_project))

        registered = engine.register_capability(
            plan, files, test_result, governance_decision_status=DecisionStatus.REJECTED
        )
        assert registered is False


class TestTestCapability:
    def test_raises_when_no_generated_tests_exist(self, engine: EvolutionEngine):
        with pytest.raises(EvolutionError):
            engine.test_capability("CAP-999")

    def test_reports_failure_when_generated_test_fails(
        self, engine: EvolutionEngine, hermetic_project: Path
    ):
        plan = CapabilityPlan(
            capability_id="CAP-009",
            name="Broken Handler",
            description="desc",
            entry_point="capabilities.generated.cap_010.capability.run",
            trigger_pattern="Parse error",
        )
        files = engine.generate_capability_code(plan)
        # Corrupt one assertion so the generated test suite fails.
        broken_tests = files.tests_code.replace("assert result.success", "assert not result.success", 1)
        files.tests_code = broken_tests
        engine.implement_capability(plan, files)

        result = engine.test_capability("CAP-009", project_root=str(hermetic_project))
        assert result.passed is False
        assert result.tests_failed >= 1


class TestBuildCommitMessage:
    def test_message_includes_key_fields(self, engine: EvolutionEngine):
        plan = CapabilityPlan(
            capability_id="CAP-009",
            name="Parse Error Handler",
            description="Generated from 3 repeated 'Parse error' failures (tasks: t1, t2, t3).",
            entry_point="capabilities.generated.cap_010.capability.run",
            trigger_pattern="Parse error",
            trigger_task_ids=["t1", "t2", "t3"],
        )
        test_result = TestRunResult(passed=True, tests_run=3, coverage_percent=87.5)
        message = engine.build_commit_message(plan, test_result, governance_decision_id="decision_000001")

        assert message.startswith("EVOLUTION: CAP-009 Parse Error Handler")
        assert "87.5%" in message
        assert "run()" in message
        assert "t1, t2, t3" in message
        assert "Decision: decision_000001" in message

    def test_message_handles_unmeasured_coverage(self, engine: EvolutionEngine):
        plan = CapabilityPlan(
            capability_id="CAP-009",
            name="Parse Error Handler",
            description="desc",
            entry_point="capabilities.generated.cap_010.capability.run",
            trigger_pattern="Parse error",
        )
        test_result = TestRunResult(passed=True, tests_run=3, coverage_percent=None)
        message = engine.build_commit_message(plan, test_result)
        assert "unmeasured" in message
        assert "Decision:" not in message
