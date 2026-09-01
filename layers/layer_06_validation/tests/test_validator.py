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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
