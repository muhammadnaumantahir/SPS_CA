import pytest

from layers.layer_08_evolution.models import (
    CapabilityPlan,
    EvolutionRecord,
    EvolutionTrigger,
    TestRunResult,
)


class TestEvolutionTrigger:
    def test_valid_construction(self):
        trigger = EvolutionTrigger(
            pattern="Parse error", occurrence_count=3, trigger_task_ids=["t1", "t2", "t3"]
        )
        assert trigger.pattern == "Parse error"
        assert trigger.occurrence_count == 3
        assert trigger.trigger_task_ids == ["t1", "t2", "t3"]

    def test_empty_pattern_rejected(self):
        with pytest.raises(ValueError):
            EvolutionTrigger(pattern="", occurrence_count=3)

    def test_negative_occurrence_count_rejected(self):
        with pytest.raises(ValueError):
            EvolutionTrigger(pattern="Parse error", occurrence_count=-1)

    def test_defaults_task_ids_to_empty_list(self):
        trigger = EvolutionTrigger(pattern="Parse error", occurrence_count=3)
        assert trigger.trigger_task_ids == []


class TestCapabilityPlan:
    def _make_plan(self, **overrides):
        defaults = dict(
            capability_id="CAP-009",
            name="Parse Error Handler",
            description="desc",
            entry_point="capabilities.generated.cap_010.capability.run",
        )
        defaults.update(overrides)
        return CapabilityPlan(**defaults)

    def test_valid_construction_defaults_to_python(self):
        plan = self._make_plan()
        assert plan.supported_languages == ["python"]

    def test_empty_capability_id_rejected(self):
        with pytest.raises(ValueError):
            self._make_plan(capability_id="")

    def test_empty_entry_point_rejected(self):
        with pytest.raises(ValueError):
            self._make_plan(entry_point="")

    def test_empty_supported_languages_rejected(self):
        with pytest.raises(ValueError):
            self._make_plan(supported_languages=[])


class TestTestRunResult:
    def test_meets_coverage_gate_true_above_threshold(self):
        result = TestRunResult(passed=True, tests_run=3, coverage_percent=85.0)
        assert result.meets_coverage_gate

    def test_meets_coverage_gate_false_below_threshold(self):
        result = TestRunResult(passed=True, tests_run=3, coverage_percent=50.0)
        assert not result.meets_coverage_gate

    def test_meets_coverage_gate_false_when_unmeasured(self):
        result = TestRunResult(passed=True, tests_run=3, coverage_percent=None)
        assert not result.meets_coverage_gate

    def test_meets_coverage_gate_true_at_exact_threshold(self):
        result = TestRunResult(passed=True, tests_run=3, coverage_percent=80.0)
        assert result.meets_coverage_gate


class TestEvolutionRecord:
    def test_to_dict_round_trips_shape(self):
        test_result = TestRunResult(
            passed=True, tests_run=3, tests_failed=0, coverage_percent=87.5
        )
        record = EvolutionRecord(
            capability_id="CAP-009",
            trigger_pattern="Parse error",
            trigger_task_ids=["t1", "t2", "t3"],
            test_result=test_result,
            governance_decision_id="decision_000001",
            registered=True,
            commit_message="EVOLUTION: CAP-009 ...",
        )
        data = record.to_dict()
        assert data["capability_id"] == "CAP-009"
        assert data["registered"] is True
        assert data["test_result"]["coverage_percent"] == 87.5
        assert "timestamp" in data

    def test_to_dict_handles_missing_test_result(self):
        record = EvolutionRecord(
            capability_id="CAP-009",
            trigger_pattern="Parse error",
            trigger_task_ids=[],
            test_result=None,
            governance_decision_id=None,
            registered=False,
            commit_message="EVOLUTION: CAP-009 ...",
        )
        assert record.to_dict()["test_result"] is None
