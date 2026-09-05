"""Layer 06: Meta-Learning.

Reads Layer 05 Experience evidence to detect recurring failure patterns,
compare observed capability behavior, recommend strategy changes, and measure
improvement over time. Meta-Learning never modifies source directly; Layer 08
Evolution owns structural self-growth.
"""

from .ab_experiment import ABComparisonEngine, ABComparisonResult
from .capability_evaluator import CapabilityEvaluation, CapabilityEvaluator
from .meta_learner import (
    DEFAULT_DECISIONS_PATH,
    DEFAULT_FAILURE_RATE_THRESHOLD,
    DEFAULT_MIN_OCCURRENCES,
    MetaLearner,
    MetaLearningDecisionLog,
)
from .models import MetaLearningDecision
from .optimization_cycle import OptimizationCycleConfig, OptimizationCycleController, OptimizationCyclePlan
from .strategy_policy import StrategyPolicy, StrategyRecommendation

__all__ = [
    "MetaLearner",
    "MetaLearningDecisionLog",
    "MetaLearningDecision",
    "CapabilityEvaluation",
    "CapabilityEvaluator",
    "StrategyPolicy",
    "StrategyRecommendation",
    "ABComparisonEngine",
    "ABComparisonResult",
    "OptimizationCycleConfig",
    "OptimizationCyclePlan",
    "OptimizationCycleController",
    "DEFAULT_DECISIONS_PATH",
    "DEFAULT_MIN_OCCURRENCES",
    "DEFAULT_FAILURE_RATE_THRESHOLD",
]
