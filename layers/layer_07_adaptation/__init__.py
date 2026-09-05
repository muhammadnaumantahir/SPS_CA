"""Layer 05: Adaptation.

Reuses existing capabilities across tasks and languages by adjusting
parameters (timeout, aggressiveness, language) rather than generating new
code. Always a Type 6 change (Change Type Taxonomy) — never triggers
Layer 8 (Evolution).
"""

from .adaptation import (DEFAULT_ADAPTATIONS_PATH,
                         DEFAULT_SIMILARITY_THRESHOLD, DEFAULT_TIMEOUT_SECONDS,
                         SLOW_LANGUAGE_TIMEOUT_SECONDS, SLOWER_LANGUAGES,
                         Adaptation, AdaptationLog)
from .models import AdaptationRecord

__all__ = [
    "Adaptation",
    "AdaptationLog",
    "AdaptationRecord",
    "DEFAULT_ADAPTATIONS_PATH",
    "DEFAULT_SIMILARITY_THRESHOLD",
    "DEFAULT_TIMEOUT_SECONDS",
    "SLOW_LANGUAGE_TIMEOUT_SECONDS",
    "SLOWER_LANGUAGES",
]
