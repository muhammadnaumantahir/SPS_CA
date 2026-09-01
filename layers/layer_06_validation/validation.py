"""
Layer 6: Validation & V&V Layer

Implements sandbox testing, regression detection, performance monitoring,
and rollback mechanisms for safe code modification.
"""

import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from .models import (
    SandboxStatus, SandboxResult, MetricsSnapshot, RegressionDetected,
    RegressionAnalysis, RegressionType, RollbackPlan
)


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class Validator:
    """
    Validates code changes safely using sandbox execution and regression detection.
    
    Responsibilities:
    - Execute changes in isolated sandbox environment
    - Compare metrics before/after
    - Detect regressions
    - Prepare rollback if needed
    - Log all validation decisions
    """
    
    def __init__(self, project_path: str, timeout_seconds: int = 300):
        """
        Initialize validator.
        
        Args:
            project_path: Path to target project
            timeout_seconds: Max time for sandbox execution
        """
        self.project_path = Path(project_path)
        self.timeout_seconds = timeout_seconds
        self._rollback_plans: Dict[str, RollbackPlan] = {}
    
    def run_in_sandbox(
        self,
        code_change: str,
        change_id: str,
        target_file: str,
        create_snapshot_before: bool = True,
    ) -> SandboxResult:
        """
        Execute code modification in isolated sandbox environment.
        
        Args:
            code_change: The code change to test
            change_id: Unique identifier for this change
            target_file: File to modify
            create_snapshot_before: Whether to capture metrics before
            
        Returns:
            SandboxResult with execution details
        """
        start_time = datetime.now()
        result = SandboxResult(
            change_id=change_id,
            status=SandboxStatus.RUNNING,
            start_time=start_time,
        )
        
        try:
            # Capture before metrics if requested
            if create_snapshot_before:
                result.metrics_before = self._capture_metrics()
            
            # Create temporary copy of project
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_project = Path(tmpdir) / "test_project"
                shutil.copytree(self.project_path, tmp_project)
                
                # Apply change to temporary project
                target_path = tmp_project / target_file
                if not target_path.exists():
                    raise ValidationError(f"Target file not found: {target_file}")
                
                target_path.write_text(code_change)
                
                # Run tests in sandbox
                result = self._run_tests_in_sandbox(tmp_project, result)
                
                # Capture after metrics
                result.metrics_after = self._capture_metrics()
        
        except Exception as e:
            result.status = SandboxStatus.ERROR
            result.exception = str(e)
        
        finally:
            result.end_time = datetime.now()
        
        return result
    
    def regression_test(
        self,
        metrics_before: MetricsSnapshot,
        metrics_after: MetricsSnapshot,
        change_id: str,
    ) -> RegressionAnalysis:
        """
        Analyze metrics before/after to detect regressions.
        
        Args:
            metrics_before: Metrics snapshot before change
            metrics_after: Metrics snapshot after change
            change_id: Identifier of the change
            
        Returns:
            RegressionAnalysis with detected issues
        """
        analysis = RegressionAnalysis(change_id=change_id, has_regression=False)
        
        # Check for test failures
        if metrics_after.tests_failing > metrics_before.tests_failing:
            delta = metrics_after.tests_failing - metrics_before.tests_failing
            analysis.has_regression = True
            analysis.regressions_detected.append(
                RegressionDetected(
                    type=RegressionType.TEST_FAILURE,
                    description=f"{delta} test(s) started failing",
                    severity="critical",
                    details={
                        "before": metrics_before.tests_failing,
                        "after": metrics_after.tests_failing,
                    }
                )
            )
        
        # Check for coverage reduction
        coverage_delta = metrics_after.code_coverage_percent - metrics_before.code_coverage_percent
        analysis.coverage_delta_percent = coverage_delta
        
        if coverage_delta < -0.5:  # More than 0.5% coverage loss
            analysis.has_regression = True
            analysis.regressions_detected.append(
                RegressionDetected(
                    type=RegressionType.COVERAGE_REDUCTION,
                    description=f"Code coverage decreased by {abs(coverage_delta):.2f}%",
                    severity="medium",
                    details={
                        "before": metrics_before.code_coverage_percent,
                        "after": metrics_after.code_coverage_percent,
                    }
                )
            )
        
        # Check for performance degradation
        perf_delta = metrics_after.execution_time_ms - metrics_before.execution_time_ms
        perf_delta_percent = (perf_delta / metrics_before.execution_time_ms * 100) if metrics_before.execution_time_ms > 0 else 0
        analysis.performance_delta_percent = perf_delta_percent
        
        if perf_delta_percent > 20:  # More than 20% slower
            analysis.has_regression = True
            analysis.regressions_detected.append(
                RegressionDetected(
                    type=RegressionType.PERFORMANCE_DEGRADATION,
                    description=f"Execution time increased by {perf_delta_percent:.2f}%",
                    severity="high" if perf_delta_percent > 50 else "medium",
                    details={
                        "before_ms": metrics_before.execution_time_ms,
                        "after_ms": metrics_after.execution_time_ms,
                        "delta_percent": perf_delta_percent,
                    }
                )
            )
        
        return analysis
    
    def prepare_rollback(
        self,
        change_id: str,
        affected_files: Dict[str, str],
        reason: Optional[str] = None,
    ) -> RollbackPlan:
        """
        Prepare a rollback plan for a change.
        
        Args:
            change_id: Identifier of the change
            affected_files: {filepath: original_content}
            reason: Why rollback might be needed
            
        Returns:
            RollbackPlan that can be executed later
        """
        plan = RollbackPlan(
            change_id=change_id,
            original_files=affected_files,
            timestamp=datetime.now(),
            reason=reason,
        )
        self._rollback_plans[change_id] = plan
        return plan
    
    def execute_rollback(self, change_id: str) -> bool:
        """
        Execute a rollback plan.
        
        Args:
            change_id: Which change to rollback
            
        Returns:
            True if rollback succeeded
        """
        if change_id not in self._rollback_plans:
            raise ValidationError(f"No rollback plan found for {change_id}")
        
        plan = self._rollback_plans[change_id]
        try:
            for filepath, original_content in plan.original_files.items():
                file_path = self.project_path / filepath
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(original_content)
            
            plan.executed = True
            return True
        except Exception as e:
            raise ValidationError(f"Rollback failed: {str(e)}")
    
    def _capture_metrics(self) -> MetricsSnapshot:
        """Capture current project metrics."""
        snapshot = MetricsSnapshot(timestamp=datetime.now())
        
        try:
            # Run pytest to get metrics
            result = subprocess.run(
                ["pytest", str(self.project_path), "--tb=no", "-q", "--co"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            # Parse pytest output for test count
            output_lines = result.stdout.split("\n")
            for line in output_lines:
                if "test session starts" in line or "selected" in line:
                    # Extract test count
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "selected" in part and i > 0:
                            try:
                                snapshot.test_count = int(parts[i-1])
                            except (ValueError, IndexError):
                                pass
            
            # Run tests with coverage
            result = subprocess.run(
                ["pytest", str(self.project_path), "--cov", "--cov-report=term-missing", "-q"],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            
            snapshot.exit_code = result.returncode
            snapshot.tests_passing = (
                snapshot.test_count if result.returncode == 0 else 0
            )
            snapshot.tests_failing = (
                snapshot.test_count - snapshot.tests_passing
            )
            
            # Extract coverage from output
            for line in result.stdout.split("\n"):
                if "%" in line and "coverage" in line.lower():
                    try:
                        # Try to extract percentage
                        parts = line.split()
                        for part in parts:
                            if "%" in part:
                                snapshot.code_coverage_percent = float(part.rstrip("%"))
                                break
                    except (ValueError, IndexError):
                        pass
            
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
        
        return snapshot
    
    def _run_tests_in_sandbox(
        self,
        project_path: Path,
        result: SandboxResult,
    ) -> SandboxResult:
        """Run tests in sandbox project."""
        try:
            test_result = subprocess.run(
                ["pytest", str(project_path), "-v"],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                cwd=str(project_path),
            )
            
            result.stdout = test_result.stdout
            result.stderr = test_result.stderr
            result.exit_code = test_result.returncode
            
            if test_result.returncode == 0:
                result.status = SandboxStatus.SUCCESS
            else:
                result.status = SandboxStatus.FAILURE
        
        except subprocess.TimeoutExpired:
            result.status = SandboxStatus.TIMEOUT
            result.exception = "Sandbox execution timed out"
        except Exception as e:
            result.status = SandboxStatus.ERROR
            result.exception = str(e)
        
        return result
