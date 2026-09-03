"""Deterministic evidence harness for proving SPS-CA self-improvement.

The benchmark does not mutate the repository. It evaluates a capability before
and after an Evolution operation and only reports improvement when the
post-Evolution behavioral score exceeds the baseline by the configured margin.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

from layers.layer_05_experience import ExperienceLog
from layers.layer_06_meta_learning import CapabilityEvaluator, CapabilityEvaluation


@dataclass(frozen=True)
class SelfImprovementBenchmarkResult:
    capability_id: str
    baseline: CapabilityEvaluation
    post_evolution: CapabilityEvaluation
    score_delta: float
    improved: bool
    promotion_succeeded: bool
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "baseline": self.baseline.to_dict(),
            "post_evolution": self.post_evolution.to_dict(),
            "score_delta": self.score_delta,
            "improved": self.improved,
            "promotion_succeeded": self.promotion_succeeded,
            "evidence": dict(self.evidence),
        }


class SelfImprovementBenchmark:
    """Measure whether a governed Evolution result produces better evidence."""

    def __init__(self, *, evaluator: CapabilityEvaluator | None = None, minimum_score_delta: float = 0.05) -> None:
        if minimum_score_delta < 0:
            raise ValueError("minimum_score_delta must be >= 0")
        self.evaluator = evaluator or CapabilityEvaluator()
        self.minimum_score_delta = minimum_score_delta

    def measure(
        self,
        *,
        capability_id: str,
        baseline_experience: ExperienceLog,
        post_evolution_experience: ExperienceLog,
        evolution_result: dict[str, Any],
    ) -> SelfImprovementBenchmarkResult:
        baseline = self.evaluator.evaluate(baseline_experience, capability_id)
        post = self.evaluator.evaluate(post_evolution_experience, capability_id)
        promotion_succeeded = bool(evolution_result.get("promoted") or evolution_result.get("registered"))
        delta = post.score - baseline.score
        improved = promotion_succeeded and delta >= self.minimum_score_delta
        evidence = {
            "minimum_score_delta": self.minimum_score_delta,
            "baseline_observations": baseline.observations,
            "post_evolution_observations": post.observations,
            "promotion_succeeded": promotion_succeeded,
        }
        return SelfImprovementBenchmarkResult(
            capability_id=capability_id,
            baseline=baseline,
            post_evolution=post,
            score_delta=delta,
            improved=improved,
            promotion_succeeded=promotion_succeeded,
            evidence=evidence,
        )

    def run(
        self,
        *,
        capability_id: str,
        baseline_experience: ExperienceLog,
        evolution: Callable[[], dict[str, Any]],
        post_evolution_experience_factory: Callable[[dict[str, Any]], ExperienceLog],
    ) -> SelfImprovementBenchmarkResult:
        """Run a caller-supplied governed Evolution action and score its outcome."""
        result = evolution()
        post_experience = post_evolution_experience_factory(result)
        return self.measure(
            capability_id=capability_id,
            baseline_experience=baseline_experience,
            post_evolution_experience=post_experience,
            evolution_result=result,
        )


__all__ = ["SelfImprovementBenchmark", "SelfImprovementBenchmarkResult"]
