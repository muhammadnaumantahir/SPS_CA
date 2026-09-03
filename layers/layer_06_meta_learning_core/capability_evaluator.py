"""Evidence-based behavioral evaluation for capability selection.

Layer 6 (Meta-Learning) turns append-only Experience evidence into comparable
capability scores. The evaluator is deliberately deterministic: it does not
rewrite capabilities and it does not bypass Governance or Execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from layers.layer_05_experience.experience_log import ExperienceLog


@dataclass(frozen=True)
class CapabilityEvaluation:
    """Comparable behavioral score for one capability."""

    capability_id: str
    observations: int
    success_rate: float
    partial_rate: float
    mean_time_seconds: float
    confidence: float
    score: float

    def to_dict(self) -> Dict[str, object]:
        return {
            "capability_id": self.capability_id,
            "observations": self.observations,
            "success_rate": self.success_rate,
            "partial_rate": self.partial_rate,
            "mean_time_seconds": self.mean_time_seconds,
            "confidence": self.confidence,
            "score": self.score,
        }


class CapabilityEvaluator:
    """Rank observed capabilities using success, partial outcomes and latency."""

    DEFAULT_MIN_OBSERVATIONS = 3
    DEFAULT_LATENCY_WEIGHT = 0.10
    DEFAULT_PRIOR_SUCCESS = 0.50

    def evaluate(self, experience_log: ExperienceLog, capability_id: str, *, latency_reference_seconds: float = 30.0) -> CapabilityEvaluation:
        tasks = [task for task in experience_log.tasks if task.selected_capability == capability_id]
        observations = len(tasks)
        if observations == 0:
            return CapabilityEvaluation(capability_id, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
        successes = sum(task.status == "success" for task in tasks)
        partials = sum(task.status == "partial" for task in tasks)
        success_rate = successes / observations
        partial_rate = partials / observations
        mean_time = sum(max(0.0, task.time_taken_seconds) for task in tasks) / observations
        confidence = observations / (observations + 5.0)
        smoothed_success = (successes + self.DEFAULT_PRIOR_SUCCESS) / (observations + 1.0)
        partial_credit = 0.5 * partial_rate
        safe_reference = max(1.0, float(latency_reference_seconds))
        latency_factor = min(1.0, mean_time / safe_reference)
        raw_score = (0.80 * smoothed_success) + (0.20 * partial_credit)
        raw_score *= (1.0 - self.DEFAULT_LATENCY_WEIGHT * latency_factor)
        score = max(0.0, min(1.0, raw_score * (0.50 + 0.50 * confidence)))
        return CapabilityEvaluation(capability_id, observations, success_rate, partial_rate, mean_time, confidence, score)

    def rank(self, experience_log: ExperienceLog, capability_ids: Iterable[str], *, min_observations: int = DEFAULT_MIN_OBSERVATIONS) -> List[CapabilityEvaluation]:
        evaluations = [self.evaluate(experience_log, capability_id) for capability_id in capability_ids]
        return sorted([item for item in evaluations if item.observations >= min_observations], key=lambda item: (item.score, item.confidence, item.success_rate), reverse=True)

    def choose_best(self, experience_log: ExperienceLog, capability_ids: Iterable[str], *, min_observations: int = DEFAULT_MIN_OBSERVATIONS) -> str | None:
        ranked = self.rank(experience_log, capability_ids, min_observations=min_observations)
        return ranked[0].capability_id if ranked else None


__all__ = ["CapabilityEvaluation", "CapabilityEvaluator"]
