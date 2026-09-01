"""
Layer 6: Validation & V&V Layer

Implements sandbox testing, regression detection, performance monitoring,
and rollback mechanisms for safe code modification.
"""

from .validation import Validator, ValidationError
from .capability_package_validator import CapabilityPackageValidator, PackageValidationResult
from .models import (
    SandboxStatus,
    SandboxResult,
    MetricsSnapshot,
    RegressionDetected,
    RegressionAnalysis,
    RegressionType,
    RollbackPlan,
)

__version__ = "0.2.0"
__all__ = [
    "Validator",
    "ValidationError",
    "CapabilityPackageValidator",
    "PackageValidationResult",
    "SandboxStatus",
    "SandboxResult",
    "MetricsSnapshot",
    "RegressionDetected",
    "RegressionAnalysis",
    "RegressionType",
    "RollbackPlan",
]
