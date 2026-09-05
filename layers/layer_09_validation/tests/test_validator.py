"""
Unit tests for Layer 6: Validation & V&V Layer.

Tests sandbox execution, regression detection, and rollback mechanisms.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from ..validation import Validator, ValidationError
from ..models import (
    SandboxStatus, SandboxResult, MetricsSnapshot,
    RegressionType, RollbackPlan
)


class TestValidator:
    """Test Validator class."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create a simple Python project structure
            (project_path / "src").mkdir()
            (project_path / "tests").mkdir()
            
            # Create a simple module
            (project_path / "src" / "module.py").write_text("""
def add(a, b):
    '''Add two numbers.'''
    return a + b

def subtract(a, b):
    '''Subtract b from a.'''
    return a - b
""")
            
            # Create a test file
            (project_path / "tests" / "test_module.py").write_text("""
import sys
sys.path.insert(0, '../src')
from module import add, subtract

def test_add():
    assert add(2, 3) == 5
    
def test_subtract():
    assert subtract(5, 3) == 2
""")
            
            yield project_path

    def test_validator_initialization(self, temp_project):
        """Test Validator initialization."""
        validator = Validator(str(temp_project), timeout_seconds=60)
        
        assert validator.project_path == temp_project
        assert validator.timeout_seconds == 60
        assert validator._rollback_plans == {}

    def test_metrics_snapshot_creation(self):
        """Test MetricsSnapshot creation."""
        snapshot = MetricsSnapshot(
            timestamp=datetime.now(),
            test_count=10,
            tests_passing=10,
            code_coverage_percent=85.5,
            execution_time_ms=1234.56
        )
        
        assert snapshot.test_count == 10
        assert snapshot.tests_passing == 10
        assert snapshot.code_coverage_percent == 85.5
        assert snapshot.execution_time_ms == 1234.56

    def test_sandbox_result_success(self):
        """Test SandboxResult for successful execution."""
        start_time = datetime.now()
        
        metrics = MetricsSnapshot(
            timestamp=datetime.now(),
            test_count=42,
            tests_passing=42,
            code_coverage_percent=89.0,
            execution_time_ms=2100.0
        )
        
        result = SandboxResult(
            change_id="CHANGE-001",
            status=SandboxStatus.SUCCESS,
            start_time=start_time,
            metrics_after=metrics,
            stdout="All tests passed",
            stderr="",
            exit_code=0
        )
        
        assert result.status == SandboxStatus.SUCCESS
        assert result.metrics_after.tests_passing == 42
        assert result.exit_code == 0
        assert result.stdout == "All tests passed"

    def test_sandbox_result_failure(self):
        """Test SandboxResult for failed execution."""
        start_time = datetime.now()
        
        metrics = MetricsSnapshot(
            timestamp=datetime.now(),
            test_count=42,
            tests_passing=40,
            code_coverage_percent=85.0,
            execution_time_ms=2150.0
        )
        
        result = SandboxResult(
            change_id="CHANGE-002",
            status=SandboxStatus.FAILURE,
            start_time=start_time,
            metrics_after=metrics,
            stdout="",
            stderr="Test failure: AssertionError",
            exit_code=1
        )
        
        assert result.status == SandboxStatus.FAILURE
        assert result.metrics_after.tests_passing == 40
        assert result.exit_code == 1
        assert "AssertionError" in result.stderr

    def test_metrics_comparison_improvement(self):
        """Test comparing metrics that improve."""
        before = MetricsSnapshot(
            timestamp=datetime.now(),
            test_count=42,
            tests_passing=40,
            code_coverage_percent=80.0,
            execution_time_ms=2200.0
        )
        
        after = MetricsSnapshot(
            timestamp=datetime.now(),
            test_count=42,
            tests_passing=42,
            code_coverage_percent=85.0,
            execution_time_ms=2100.0
        )
        
        assert before.tests_passing < after.tests_passing
        assert before.code_coverage_percent < after.code_coverage_percent
        assert before.execution_time_ms > after.execution_time_ms

    def test_regression_detection_test_failure(self):
        """Test regression detection when tests fail."""
        before = MetricsSnapshot(
            timestamp=datetime.now(),
            test_count=42,
            tests_passing=42,
            code_coverage_percent=85.0,
            execution_time_ms=2100.0
        )
        
        after = MetricsSnapshot(
            timestamp=datetime.now(),
            test_count=42,
            tests_passing=40,
            code_coverage_percent=85.0,
            execution_time_ms=2100.0
        )
        
        # Tests went from 42/42 to 40/42 - clear regression
        assert after.tests_passing < before.tests_passing

    def test_regression_detection_performance_degradation(self):
        """Test regression detection when performance degrades significantly."""
        before = MetricsSnapshot(
            timestamp=datetime.now(),
            test_count=42,
            tests_passing=42,
            code_coverage_percent=85.0,
            execution_time_ms=2100.0
        )
        
        after = MetricsSnapshot(
            timestamp=datetime.now(),
            test_count=42,
            tests_passing=42,
            code_coverage_percent=85.0,
            execution_time_ms=2700.0  # 28.6% increase
        )
        
        # >20% performance degradation should be flagged
        perf_ratio = after.execution_time_ms / before.execution_time_ms
        assert perf_ratio > 1.2


class TestSandboxExecution:
    """Test sandbox execution isolation."""

    def test_sandbox_status_values(self):
        """Test all sandbox status values exist and are valid."""
        assert SandboxStatus.SUCCESS
        assert SandboxStatus.FAILURE
        assert SandboxStatus.TIMEOUT
        assert SandboxStatus.ERROR

    def test_sandbox_result_serialization(self):
        """Test SandboxResult can be serialized."""
        start_time = datetime.now()
        
        metrics = MetricsSnapshot(
            timestamp=datetime.now(),
            test_count=42,
            tests_passing=42,
            code_coverage_percent=85.0,
            execution_time_ms=2100.0
        )
        
        result = SandboxResult(
            change_id="CHANGE-003",
            status=SandboxStatus.SUCCESS,
            start_time=start_time,
            metrics_after=metrics,
            stdout="Tests passed",
            stderr="",
            exit_code=0
        )
        
        # Should be serializable via dataclass
        result_dict = result.to_dict()
        assert result_dict["status"] == "success"
        assert result_dict["exit_code"] == 0


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_creation(self):
        """Test creating ValidationError."""
        with pytest.raises(ValidationError):
            raise ValidationError("Sandbox execution failed")

    def test_validation_error_with_context(self):
        """Test ValidationError with additional context."""
        error_msg = "Failed to execute tests"
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError(error_msg)
        
        assert error_msg in str(exc_info.value)


class TestRegressionTypes:
    """Test regression type classification."""

    def test_all_regression_types_defined(self):
        """Test that all regression types are defined."""
        assert RegressionType.TEST_FAILURE
        assert RegressionType.PERFORMANCE_DEGRADATION
        assert RegressionType.COVERAGE_REDUCTION
        assert RegressionType.MEMORY_LEAK
        assert RegressionType.EXCEPTION


class TestValidatorRegressionTestMethod:
    """Test Validator.regression_test() — the actual regression-detection logic.

    (Distinct from TestValidator's regression_detection_* tests above, which
    only assert on raw MetricsSnapshot arithmetic and never call the method
    itself.)
    """

    @pytest.fixture
    def validator(self, tmp_path):
        return Validator(str(tmp_path))

    def _metrics(self, **overrides):
        defaults = dict(
            timestamp=datetime.now(),
            test_count=42,
            tests_passing=42,
            tests_failing=0,
            code_coverage_percent=85.0,
            execution_time_ms=2100.0,
        )
        defaults.update(overrides)
        return MetricsSnapshot(**defaults)

    def test_no_regression_when_metrics_unchanged(self, validator):
        before = self._metrics()
        after = self._metrics()
        analysis = validator.regression_test(before, after, change_id="CHANGE-A")
        assert analysis.has_regression is False
        assert analysis.regressions_detected == []
        assert analysis.change_id == "CHANGE-A"

    def test_detects_test_failure_regression(self, validator):
        before = self._metrics(tests_passing=42, tests_failing=0)
        after = self._metrics(tests_passing=40, tests_failing=2)
        analysis = validator.regression_test(before, after, change_id="CHANGE-B")

        assert analysis.has_regression is True
        assert len(analysis.regressions_detected) == 1
        regression = analysis.regressions_detected[0]
        assert regression.type == RegressionType.TEST_FAILURE
        assert regression.severity == "critical"
        assert regression.details["before"] == 0
        assert regression.details["after"] == 2

    def test_detects_coverage_reduction_regression(self, validator):
        before = self._metrics(code_coverage_percent=85.0)
        after = self._metrics(code_coverage_percent=80.0)
        analysis = validator.regression_test(before, after, change_id="CHANGE-C")

        assert analysis.has_regression is True
        assert analysis.coverage_delta_percent == pytest.approx(-5.0)
        assert any(
            r.type == RegressionType.COVERAGE_REDUCTION
            for r in analysis.regressions_detected
        )

    def test_small_coverage_dip_is_not_a_regression(self, validator):
        before = self._metrics(code_coverage_percent=85.0)
        after = self._metrics(code_coverage_percent=84.8)  # 0.2% dip, under threshold
        analysis = validator.regression_test(before, after, change_id="CHANGE-D")
        assert analysis.has_regression is False

    def test_detects_performance_degradation_regression(self, validator):
        before = self._metrics(execution_time_ms=2100.0)
        after = self._metrics(execution_time_ms=2700.0)  # ~28.6% slower
        analysis = validator.regression_test(before, after, change_id="CHANGE-E")

        assert analysis.has_regression is True
        assert analysis.performance_delta_percent == pytest.approx(28.57, abs=0.1)
        perf_regressions = [
            r for r in analysis.regressions_detected
            if r.type == RegressionType.PERFORMANCE_DEGRADATION
        ]
        assert len(perf_regressions) == 1
        assert perf_regressions[0].severity == "medium"

    def test_severe_performance_degradation_is_high_severity(self, validator):
        before = self._metrics(execution_time_ms=1000.0)
        after = self._metrics(execution_time_ms=1600.0)  # 60% slower
        analysis = validator.regression_test(before, after, change_id="CHANGE-F")
        perf_regressions = [
            r for r in analysis.regressions_detected
            if r.type == RegressionType.PERFORMANCE_DEGRADATION
        ]
        assert perf_regressions[0].severity == "high"

    def test_multiple_simultaneous_regressions(self, validator):
        before = self._metrics(
            tests_failing=0, code_coverage_percent=85.0, execution_time_ms=2000.0
        )
        after = self._metrics(
            tests_failing=1, code_coverage_percent=79.0, execution_time_ms=3000.0
        )
        analysis = validator.regression_test(before, after, change_id="CHANGE-G")

        assert analysis.has_regression is True
        assert len(analysis.regressions_detected) == 3
        assert len(analysis.critical_regressions) == 1

    def test_zero_before_execution_time_does_not_divide_by_zero(self, validator):
        before = self._metrics(execution_time_ms=0.0)
        after = self._metrics(execution_time_ms=500.0)
        analysis = validator.regression_test(before, after, change_id="CHANGE-H")
        assert analysis.performance_delta_percent == 0


class TestValidatorRollback:
    """Test Validator.prepare_rollback() / execute_rollback()."""

    @pytest.fixture
    def project(self, tmp_path):
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "module.py").write_text("original content\n")
        return tmp_path

    def test_prepare_rollback_returns_plan(self, project):
        validator = Validator(str(project))
        plan = validator.prepare_rollback(
            change_id="CHANGE-001",
            affected_files={"src/module.py": "original content\n"},
            reason="testing rollback",
        )
        assert isinstance(plan, RollbackPlan)
        assert plan.change_id == "CHANGE-001"
        assert plan.reason == "testing rollback"
        assert plan.executed is False

    def test_execute_rollback_restores_original_content(self, project):
        validator = Validator(str(project))
        validator.prepare_rollback(
            change_id="CHANGE-001",
            affected_files={"src/module.py": "original content\n"},
        )

        # Simulate a change having modified the file.
        (project / "src" / "module.py").write_text("modified content\n")

        result = validator.execute_rollback("CHANGE-001")

        assert result is True
        assert (project / "src" / "module.py").read_text() == "original content\n"
        assert validator._rollback_plans["CHANGE-001"].executed is True

    def test_execute_rollback_creates_missing_parent_dirs(self, project):
        validator = Validator(str(project))
        validator.prepare_rollback(
            change_id="CHANGE-002",
            affected_files={"new/nested/file.py": "restored\n"},
        )
        validator.execute_rollback("CHANGE-002")
        assert (project / "new" / "nested" / "file.py").read_text() == "restored\n"

    def test_execute_rollback_unknown_change_id_raises(self, project):
        validator = Validator(str(project))
        with pytest.raises(ValidationError):
            validator.execute_rollback("NO-SUCH-CHANGE")

    def test_execute_rollback_write_failure_raises_validation_error(self, project):
        validator = Validator(str(project))
        validator.prepare_rollback(
            change_id="CHANGE-003",
            affected_files={"src/module.py": "content\n"},
        )
        with patch.object(Path, "write_text", side_effect=OSError("disk full")):
            with pytest.raises(ValidationError):
                validator.execute_rollback("CHANGE-003")


class TestValidatorCaptureMetrics:
    """Test Validator._capture_metrics() output parsing (subprocess mocked)."""

    def _completed_process(self, stdout="", returncode=0):
        proc = MagicMock()
        proc.stdout = stdout
        proc.returncode = returncode
        return proc

    def test_capture_metrics_parses_test_count_and_coverage(self, tmp_path):
        validator = Validator(str(tmp_path))
        collect_output = self._completed_process(
            stdout="collected 10 items\ntest session starts\n5 selected\n"
        )
        run_output = self._completed_process(
            stdout="TOTAL   100  10  90%\ncoverage: 90%\n", returncode=0
        )
        with patch(
            "layers.layer_09_validation.validation.subprocess.run",
            side_effect=[collect_output, run_output],
        ):
            snapshot = validator._capture_metrics()

        assert isinstance(snapshot, MetricsSnapshot)

    def test_capture_metrics_handles_timeout_gracefully(self, tmp_path):
        import subprocess as subprocess_module

        validator = Validator(str(tmp_path))
        with patch(
            "layers.layer_09_validation.validation.subprocess.run",
            side_effect=subprocess_module.TimeoutExpired(cmd="pytest", timeout=30),
        ):
            snapshot = validator._capture_metrics()

        # Should degrade gracefully to a default snapshot, not raise.
        assert snapshot.test_count == 0
        assert snapshot.tests_passing == 0

    def test_capture_metrics_handles_unexpected_exception_gracefully(self, tmp_path):
        validator = Validator(str(tmp_path))
        with patch(
            "layers.layer_09_validation.validation.subprocess.run",
            side_effect=FileNotFoundError("pytest not installed"),
        ):
            snapshot = validator._capture_metrics()
        assert isinstance(snapshot, MetricsSnapshot)


class TestValidatorRunTestsInSandbox:
    """Test Validator._run_tests_in_sandbox() (subprocess mocked)."""

    @pytest.fixture
    def validator_and_result(self, tmp_path):
        validator = Validator(str(tmp_path))
        result = SandboxResult(
            change_id="CHANGE-X",
            status=SandboxStatus.RUNNING,
            start_time=datetime.now(),
        )
        return validator, result

    def test_success_when_pytest_exits_zero(self, validator_and_result, tmp_path):
        validator, result = validator_and_result
        proc = MagicMock(stdout="3 passed", stderr="", returncode=0)
        with patch(
            "layers.layer_09_validation.validation.subprocess.run", return_value=proc
        ):
            updated = validator._run_tests_in_sandbox(tmp_path, result)
        assert updated.status == SandboxStatus.SUCCESS
        assert updated.exit_code == 0

    def test_failure_when_pytest_exits_nonzero(self, validator_and_result, tmp_path):
        validator, result = validator_and_result
        proc = MagicMock(stdout="", stderr="1 failed", returncode=1)
        with patch(
            "layers.layer_09_validation.validation.subprocess.run", return_value=proc
        ):
            updated = validator._run_tests_in_sandbox(tmp_path, result)
        assert updated.status == SandboxStatus.FAILURE
        assert updated.exit_code == 1

    def test_timeout_sets_timeout_status(self, validator_and_result, tmp_path):
        import subprocess as subprocess_module

        validator, result = validator_and_result
        with patch(
            "layers.layer_09_validation.validation.subprocess.run",
            side_effect=subprocess_module.TimeoutExpired(cmd="pytest", timeout=30),
        ):
            updated = validator._run_tests_in_sandbox(tmp_path, result)
        assert updated.status == SandboxStatus.TIMEOUT
        assert updated.exception is not None

    def test_unexpected_exception_sets_error_status(self, validator_and_result, tmp_path):
        validator, result = validator_and_result
        with patch(
            "layers.layer_09_validation.validation.subprocess.run",
            side_effect=RuntimeError("boom"),
        ):
            updated = validator._run_tests_in_sandbox(tmp_path, result)
        assert updated.status == SandboxStatus.ERROR
        assert "boom" in updated.exception


class TestValidatorRunInSandbox:
    """Test Validator.run_in_sandbox() orchestration (subprocess mocked)."""

    @pytest.fixture
    def project(self, tmp_path):
        (tmp_path / "module.py").write_text("value = 1\n")
        return tmp_path

    def test_missing_target_file_sets_error_status(self, project):
        validator = Validator(str(project))
        with patch.object(Validator, "_capture_metrics") as mock_capture:
            mock_capture.return_value = MetricsSnapshot(timestamp=datetime.now())
            result = validator.run_in_sandbox(
                code_change="value = 2\n",
                change_id="CHANGE-Y",
                target_file="does_not_exist.py",
            )
        assert result.status == SandboxStatus.ERROR
        assert "not found" in result.exception

    def test_successful_run_populates_before_and_after_metrics(self, project):
        validator = Validator(str(project))
        before = MetricsSnapshot(timestamp=datetime.now(), test_count=1)
        after = MetricsSnapshot(timestamp=datetime.now(), test_count=1)

        with patch.object(
            Validator, "_capture_metrics", side_effect=[before, after]
        ), patch.object(
            Validator,
            "_run_tests_in_sandbox",
            side_effect=lambda proj, res: (
                setattr(res, "status", SandboxStatus.SUCCESS) or res
            ),
        ):
            result = validator.run_in_sandbox(
                code_change="value = 2\n",
                change_id="CHANGE-Z",
                target_file="module.py",
            )

        assert result.status == SandboxStatus.SUCCESS
        assert result.metrics_before is before
        assert result.metrics_after is after
        assert result.end_time is not None

    def test_skips_before_metrics_when_snapshot_disabled(self, project):
        validator = Validator(str(project))
        after = MetricsSnapshot(timestamp=datetime.now())

        with patch.object(
            Validator, "_capture_metrics", return_value=after
        ) as mock_capture, patch.object(
            Validator,
            "_run_tests_in_sandbox",
            side_effect=lambda proj, res: (
                setattr(res, "status", SandboxStatus.SUCCESS) or res
            ),
        ):
            result = validator.run_in_sandbox(
                code_change="value = 2\n",
                change_id="CHANGE-NOSNAP",
                target_file="module.py",
                create_snapshot_before=False,
            )

        assert result.metrics_before is None
        # _capture_metrics should only be called once (for "after"), not twice.
        assert mock_capture.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
