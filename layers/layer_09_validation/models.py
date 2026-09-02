"""
Layer 6: Validation & V&V - Data Models

Defines structures for validation results, sandbox execution, and regression detection.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum


class SandboxStatus(str, Enum):
    """Status of sandbox execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"


class RegressionType(str, Enum):
    """Types of regression detected."""
    TEST_FAILURE = "test_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    COVERAGE_REDUCTION = "coverage_reduction"
    MEMORY_LEAK = "memory_leak"
    EXCEPTION = "exception"


@dataclass
class MetricsSnapshot:
    """Snapshot of code metrics at a point in time."""
    timestamp: datetime
    test_count: int = 0
    tests_passing: int = 0
    tests_failing: int = 0
    code_coverage_percent: float = 0.0
    execution_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    lines_of_code: int = 0
    
    @property
    def test_pass_rate(self) -> float:
        """Calculate test pass rate as percentage."""
        if self.test_count == 0:
            return 0.0
        return (self.tests_passing / self.test_count) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "test_count": self.test_count,
            "tests_passing": self.tests_passing,
            "tests_failing": self.tests_failing,
            "code_coverage_percent": self.code_coverage_percent,
            "execution_time_ms": self.execution_time_ms,
            "memory_usage_mb": self.memory_usage_mb,
            "lines_of_code": self.lines_of_code,
            "test_pass_rate": self.test_pass_rate,
        }


@dataclass
class SandboxResult:
    """Result of sandbox execution."""
    change_id: str
    status: SandboxStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    exception: Optional[str] = None
    metrics_before: Optional[MetricsSnapshot] = None
    metrics_after: Optional[MetricsSnapshot] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate execution duration."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def success(self) -> bool:
        """Whether execution was successful."""
        return self.status == SandboxStatus.SUCCESS
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "change_id": self.change_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "exception": self.exception,
            "metrics_before": self.metrics_before.to_dict() if self.metrics_before else None,
            "metrics_after": self.metrics_after.to_dict() if self.metrics_after else None,
        }


@dataclass
class RegressionDetected:
    """Details of a regression detected."""
    type: RegressionType
    description: str
    severity: str  # "critical", "high", "medium", "low"
    affected_tests: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "description": self.description,
            "severity": self.severity,
            "affected_tests": self.affected_tests,
            "details": self.details,
        }


@dataclass
class RegressionAnalysis:
    """Analysis of regressions between before/after states."""
    change_id: str
    has_regression: bool
    regressions_detected: List[RegressionDetected] = field(default_factory=list)
    test_failures: List[str] = field(default_factory=list)
    performance_delta_percent: float = 0.0  # Positive = slower
    coverage_delta_percent: float = 0.0     # Positive = better coverage
    
    @property
    def critical_regressions(self) -> List[RegressionDetected]:
        """Get only critical regressions."""
        return [r for r in self.regressions_detected if r.severity == "critical"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "change_id": self.change_id,
            "has_regression": self.has_regression,
            "regressions_detected": [r.to_dict() for r in self.regressions_detected],
            "test_failures": self.test_failures,
            "performance_delta_percent": self.performance_delta_percent,
            "coverage_delta_percent": self.coverage_delta_percent,
            "critical_regressions": len(self.critical_regressions),
        }


@dataclass
class RollbackPlan:
    """Plan for rolling back a change if needed."""
    change_id: str
    original_files: Dict[str, str]  # {filepath: original_content}
    timestamp: datetime
    reason: Optional[str] = None
    executed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "change_id": self.change_id,
            "original_files": list(self.original_files.keys()),
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
            "executed": self.executed,
        }
