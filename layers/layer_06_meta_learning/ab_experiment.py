"""Evidence-based A/B capability comparison for Layer 6."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, Optional

from layers.layer_05_experience.experience_log import ExperienceLog

from .capability_evaluator import CapabilityEvaluation, CapabilityEvaluator


@dataclass(frozen=True)
class ABComparisonResult:
    """Auditable comparison between two compatible capability arms."""

    experiment_id: str
    control_capability_id: str
    treatment_capability_id: str
    control: CapabilityEvaluation
    treatment: CapabilityEvaluation
    balanced: bool
    winner: Optional[str]
    score_margin: float
    evidence_sufficient: bool
    recommendation: str = "insufficient_evidence"
    confidence: float = 0.0
    total_observations: int = 0

    def to_dict(self) -> Dict[str, object]:
        return {
            "experiment_id": self.experiment_id,
            "control_capability_id": self.control_capability_id,
            "treatment_capability_id": self.treatment_capability_id,
            "control": self.control.to_dict(),
            "treatment": self.treatment.to_dict(),
            "balanced": self.balanced,
            "winner": self.winner,
            "score_margin": self.score_margin,
            "evidence_sufficient": self.evidence_sufficient,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "total_observations": self.total_observations,
        }


class ABComparisonEngine:
    """Assign compatible capabilities to A/B arms and compare real behavior."""

    DEFAULT_MIN_OBSERVATIONS_PER_ARM = 5
    DEFAULT_MIN_SCORE_MARGIN = 0.08

    @staticmethod
    def assign_arm(experiment_id: str, task_id: str) -> str:
        material = f"{experiment_id}:{task_id}".encode("utf-8")
        digest = hashlib.sha256(material).hexdigest()
        return "A" if int(digest[-2:], 16) % 2 == 0 else "B"

    def compare(
        self,
        experience_log: ExperienceLog,
        *,
        experiment_id: str,
        control_capability_id: str,
        treatment_capability_id: str,
        min_observations_per_arm: int = DEFAULT_MIN_OBSERVATIONS_PER_ARM,
        min_score_margin: float = DEFAULT_MIN_SCORE_MARGIN,
    ) -> ABComparisonResult:
        evaluator = CapabilityEvaluator()
        control = evaluator.evaluate(experience_log, control_capability_id)
        treatment = evaluator.evaluate(experience_log, treatment_capability_id)
        minimum = max(1, int(min_observations_per_arm))
        balanced = abs(control.observations - treatment.observations) <= max(1, minimum // 2)
        evidence_sufficient = control.observations >= minimum and treatment.observations >= minimum and balanced
        score_margin = abs(control.score - treatment.score)
        winner: Optional[str] = None
        recommendation = "insufficient_evidence"
        confidence = 0.0
        total_observations = control.observations + treatment.observations
        if evidence_sufficient:
            relative_margin = score_margin / max(0.0001, max(abs(control.score), abs(treatment.score), 1.0))
            confidence = min(0.99, 0.5 + (min(control.observations, treatment.observations) / max(minimum, 1)) * 0.1 + relative_margin * 0.5)
            if score_margin >= max(0.0, float(min_score_margin)):
                winner = treatment_capability_id if treatment.score > control.score else control_capability_id
                recommendation = winner
            else:
                recommendation = "continue"
        return ABComparisonResult(
            experiment_id=experiment_id,
            control_capability_id=control_capability_id,
            treatment_capability_id=treatment_capability_id,
            control=control,
            treatment=treatment,
            balanced=balanced,
            winner=winner,
            score_margin=score_margin,
            evidence_sufficient=evidence_sufficient,
            recommendation=recommendation,
            confidence=round(confidence, 4),
            total_observations=total_observations,
        )


__all__ = ["ABComparisonResult", "ABComparisonEngine"]
