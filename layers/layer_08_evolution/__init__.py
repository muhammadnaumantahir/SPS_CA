"""Layer 08: Evolution Engine.

Layer 8 owns the self-programming lifecycle: detecting limitations,
planning capability growth, generating candidates, validating them, and
preserving evolution provenance. The public ten-layer model is unchanged.
"""

from .controlled_evolution import ControlledEvolutionEngine
from .evolution_engine import EvolutionError
from .gap_planner import CapabilityGapPlanner
from .governed_self_programming import SelfProgrammingEngine
from .optimization_action_planner import EvolutionActionPlan, OptimizationActionPlanner
from .retirement import GovernedRetirementManager, RetirementRecommendation
from .self_programming import FailureDiagnosis, SelfProgrammingError, SelfRepairResult
from .models import (
    CapabilityPlan,
    EvolutionRecord,
    EvolutionTrigger,
    GeneratedCapabilityFiles,
    TestRunResult,
)

# Keep existing imports source-compatible while activating the governed
# candidate-based implementation for all Layer-8 callers.
EvolutionEngine = ControlledEvolutionEngine

__all__ = [
    "EvolutionEngine",
    "ControlledEvolutionEngine",
    "EvolutionError",
    "CapabilityGapPlanner",
    "OptimizationActionPlanner",
    "EvolutionActionPlan",
    "SelfProgrammingEngine",
    "SelfProgrammingError",
    "FailureDiagnosis",
    "SelfRepairError" if False else "SelfRepairResult",
    "GovernedRetirementManager",
    "RetirementRecommendation",
    "CapabilityPlan",
    "EvolutionRecord",
    "EvolutionTrigger",
    "GeneratedCapabilityFiles",
    "TestRunResult",
]
