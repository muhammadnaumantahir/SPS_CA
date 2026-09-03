"""Layer 08: Evolution Engine.

Layer 8 owns the self-programming lifecycle: detecting limitations,
planning capability growth, generating candidates, validating them, and
preserving evolution provenance. The public ten-layer model is unchanged.
"""

from .controlled_evolution import ControlledEvolutionEngine
from .evolution_engine import EvolutionError
from .evolution_cycle import EvolutionCycleOutcome
from .execution_authority import EvolutionExecutionAuthority
from .gap_planner import CapabilityGapPlanner
from .governed_self_programming import SelfProgrammingEngine
from .growth_decision import GrowthDecision, GrowthDecisionEngine, GrowthDecisionResult
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

EvolutionEngine = ControlledEvolutionEngine

__all__ = [
    "EvolutionEngine",
    "ControlledEvolutionEngine",
    "EvolutionError",
    "EvolutionCycleOutcome",
    "EvolutionExecutionAuthority",
    "CapabilityGapPlanner",
    "GrowthDecision",
    "GrowthDecisionEngine",
    "GrowthDecisionResult",
    "OptimizationActionPlanner",
    "EvolutionActionPlan",
    "SelfProgrammingEngine",
    "SelfProgrammingError",
    "FailureDiagnosis",
    "SelfRepairResult",
    "GovernedRetirementManager",
    "RetirementRecommendation",
    "CapabilityPlan",
    "EvolutionRecord",
    "EvolutionTrigger",
    "GeneratedCapabilityFiles",
    "TestRunResult",
]
