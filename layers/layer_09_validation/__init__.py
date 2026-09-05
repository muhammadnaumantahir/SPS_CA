"""
Layer 9: Verification & Validation

Implements sandbox testing, regression detection, performance monitoring,
and rollback mechanisms for safe code modification.

This layer ensures all proposed changes are validated in an isolated environment
before deployment to user projects. It provides:

- Sandbox execution: Execute code changes in isolation
- Regression detection: Compare test results before/after changes
- Performance monitoring: Track execution time and resource usage
- Rollback preparation: Store state for easy restoration if needed
- Metrics tracking: Collect before/after metrics for analysis
"""

from .validation import Validator, ValidationError
from .models import (
    SandboxStatus,
    SandboxResult,
    MetricsSnapshot,
    RegressionDetected,
    RegressionAnalysis,
    RegressionType,
    RollbackPlan,
)

__all__ = [
    "Validator",
    "ValidationError",
    "SandboxStatus",
    "SandboxResult",
    "MetricsSnapshot",
    "RegressionDetected",
    "RegressionAnalysis",
    "RegressionType",
    "RollbackPlan",
]
