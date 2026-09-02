"""Layer 04: Meta-Learning.

Reads Layer 3's ExperienceLog to detect recurring failure patterns,
recommend capability strategy changes, and measure improvement over time.
Never modifies code or capabilities directly (see Layer 8: Evolution).
"""

from .meta_learner import (DEFAULT_DECISIONS_PATH,
                           DEFAULT_FAILURE_RATE_THRESHOLD,
                           DEFAULT_MIN_OCCURRENCES, MetaLearner,
                           MetaLearningDecisionLog)
from .models import MetaLearningDecision

__all__ = [
    "MetaLearner",
    "MetaLearningDecisionLog",
    "MetaLearningDecision",
    "DEFAULT_DECISIONS_PATH",
    "DEFAULT_MIN_OCCURRENCES",
    "DEFAULT_FAILURE_RATE_THRESHOLD",
]
