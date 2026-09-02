"""
Layer 9: Capability Registry

Manages capability registration, querying, and lifecycle.
Provides the registry that Layer 8 (Evolution) populates and Layer 10 (Execution) consumes.
"""

from .models import (
    CapabilityMetadata,
    CapabilityType,
    CapabilityLanguage,
    CapabilityQuery,
    CapabilityQueryResult,
    CapabilityReusageRecord,
    CapabilityRegistry,
)
from .registry import CapabilityRegistryManager

__all__ = [
    "CapabilityMetadata",
    "CapabilityType",
    "CapabilityLanguage",
    "CapabilityQuery",
    "CapabilityQueryResult",
    "CapabilityReusageRecord",
    "CapabilityRegistry",
    "CapabilityRegistryManager",
]
