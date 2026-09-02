"""Layer 08: Evolution Engine.

The core self-programming mechanism: detects repeated failure patterns in
Layer 3's experience log and generates new, tested, governed capabilities
in response. See ``evolution_engine.py`` for the full pipeline and
``models.py`` for the data it produces and persists.
"""

from .evolution_engine import EvolutionEngine, EvolutionError
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
    "CapabilityPlan",
    "EvolutionRecord",
    "EvolutionTrigger",
    "GeneratedCapabilityFiles",
    "TestRunResult",
]
