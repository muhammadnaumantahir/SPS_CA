"""Layer 08: Evolution Engine.

Layer 8 owns the self-programming lifecycle: detecting limitations,
planning capability growth, generating capabilities, and preserving their
evolution provenance. Layer names remain aligned with the SPS ten-layer
framework.
"""

from .evolution_engine import EvolutionEngine, EvolutionError
from .gap_planner import CapabilityGapPlanner
from .models import (
    CapabilityPlan,
    EvolutionRecord,
    EvolutionTrigger,
    GeneratedCapabilityFiles,
    TestRunResult,
)

__all__ = [
    "EvolutionEngine",
    "EvolutionError",
    "CapabilityGapPlanner",
    "CapabilityPlan",
    "EvolutionRecord",
    "EvolutionTrigger",
    "GeneratedCapabilityFiles",
    "TestRunResult",
]
