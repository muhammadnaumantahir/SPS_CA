"""Controlled A/B capability comparison for Layer 6.

A/B assignment is deterministic and evidence-based. It never executes code,
changes the registry, or bypasses Governance; it only records which arm should
be used for a request and decides whether enough evidence exists to name a
winner for future routing.
"""

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
        }


class ABComparisonEngine:
    """Assign compatible capabilities to A/B arms and compare observed behavior."""

    DEFAULT_MIN_OBSERVATIONS_PER_ARM = 5
    DEFAULT_MIN_SCORE_MARGIN = 0.08

    @staticmethod
    def assign_arm(experiment_id: str, task_id: str) -> str:
        """Deterministically assign a task to A or B using a stable hash."""
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
        evidence_sufficient = (
            control.observations >= minimum
            and treatment.observations >= minimum
            and balanced
        )
        score_margin = abs(control.score - treatment.score)
        winner: Optional[str] = None
        if evidence_sufficient and score_margin >= max(0.0, float(min_score_margin)):
            winner = (
                treatment_capability_id
                if treatment.score > control.score
                else control_capability_id
            )
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
        )


__all__ = ["ABComparisonResult", "ABComparisonEngine"]
