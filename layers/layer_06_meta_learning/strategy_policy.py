"""Phase 2 strategy policy for evidence-based capability switching.

Layer 6 owns the decision policy for future routing. It does not mutate
capabilities and does not bypass the Brain, Governance, Verification &
Validation, or Execution boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from layers.layer_05_experience.experience_log import ExperienceLog

from .capability_evaluator import CapabilityEvaluation, CapabilityEvaluator


@dataclass(frozen=True)
class StrategyRecommendation:
    """Auditable recommendation to prefer one capability over another."""

    current_capability_id: str
    recommended_capability_id: Optional[str]
    current_score: float
    recommended_score: float
    score_margin: float
    reason: str
    evidence_sufficient: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "current_capability_id": self.current_capability_id,
            "recommended_capability_id": self.recommended_capability_id,
            "current_score": self.current_score,
            "recommended_score": self.recommended_score,
            "score_margin": self.score_margin,
            "reason": self.reason,
            "evidence_sufficient": self.evidence_sufficient,
        }


class StrategyPolicy:
    """Apply conservative evidence and margin rules to evaluator results."""

    DEFAULT_MIN_OBSERVATIONS = 3
    DEFAULT_MIN_SCORE_MARGIN = 0.08

    def __init__(
        self,
        *,
        evaluator: CapabilityEvaluator | None = None,
        min_observations: int = DEFAULT_MIN_OBSERVATIONS,
        min_score_margin: float = DEFAULT_MIN_SCORE_MARGIN,
    ) -> None:
        self.evaluator = evaluator or CapabilityEvaluator()
        self.min_observations = max(1, int(min_observations))
        self.min_score_margin = max(0.0, float(min_score_margin))

    def recommend(
        self,
        experience_log: ExperienceLog,
        current_capability_id: str,
        candidate_capability_ids: Iterable[str],
    ) -> StrategyRecommendation:
        """Return a recommendation only when evidence justifies switching."""
        candidate_ids = [
            str(capability_id)
            for capability_id in candidate_capability_ids
            if str(capability_id) and str(capability_id) != current_capability_id
        ]
        current = self.evaluator.evaluate(experience_log, current_capability_id)
        if current.observations < self.min_observations:
            return StrategyRecommendation(
                current_capability_id=current_capability_id,
                recommended_capability_id=None,
                current_score=current.score,
                recommended_score=0.0,
                score_margin=0.0,
                reason="Insufficient evidence for the current capability.",
                evidence_sufficient=False,
            )

        ranked = self.evaluator.rank(
            experience_log,
            candidate_ids,
            min_observations=self.min_observations,
        )
        if not ranked:
            return StrategyRecommendation(
                current_capability_id=current_capability_id,
                recommended_capability_id=None,
                current_score=current.score,
                recommended_score=0.0,
                score_margin=0.0,
                reason="No alternative capability has sufficient evidence.",
                evidence_sufficient=False,
            )

        best: CapabilityEvaluation = ranked[0]
        margin = best.score - current.score
        if margin < self.min_score_margin:
            return StrategyRecommendation(
                current_capability_id=current_capability_id,
                recommended_capability_id=None,
                current_score=current.score,
                recommended_score=best.score,
                score_margin=margin,
                reason=(
                    f"Best alternative {best.capability_id} does not clear the "
                    f"minimum score margin of {self.min_score_margin:.2f}."
                ),
                evidence_sufficient=True,
            )

        return StrategyRecommendation(
            current_capability_id=current_capability_id,
            recommended_capability_id=best.capability_id,
            current_score=current.score,
            recommended_score=best.score,
            score_margin=margin,
            reason=(
                f"{best.capability_id} outscored {current_capability_id} by "
                f"{margin:.3f} with at least {self.min_observations} observations."
            ),
            evidence_sufficient=True,
        )


__all__ = ["StrategyPolicy", "StrategyRecommendation"]
