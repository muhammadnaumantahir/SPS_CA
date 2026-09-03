"""Deterministic optimization-cycle controller for Layer 6.

The controller converts accumulated Experience evidence into an auditable
optimization plan. It never edits source, registry state, or execution state.
Layer 8 Evolution remains the only layer that can turn an approved gap into a
new capability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional

from layers.layer_05_experience import ExperienceLog

from .capability_evaluator import CapabilityEvaluation, CapabilityEvaluator


@dataclass(frozen=True)
class OptimizationCycleConfig:
    """Conservative thresholds for triggering a learning cycle."""

    minimum_total_observations: int = 10
    minimum_failure_rate: float = 0.30
    minimum_capability_observations: int = 5
    minimum_capability_score: float = 0.35
    cooldown_seconds: float = 300.0


@dataclass(frozen=True)
class OptimizationCyclePlan:
    """Auditable recommendation produced by an optimization cycle."""

    cycle_id: str
    triggered: bool
    reasons: List[str] = field(default_factory=list)
    total_observations: int = 0
    failure_rate: float = 0.0
    candidates: List[CapabilityEvaluation] = field(default_factory=list)
    created_at: str = ""
    next_eligible_at: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "cycle_id": self.cycle_id,
            "triggered": self.triggered,
            "reasons": list(self.reasons),
            "total_observations": self.total_observations,
            "failure_rate": self.failure_rate,
            "candidates": [item.to_dict() for item in self.candidates],
            "created_at": self.created_at,
            "next_eligible_at": self.next_eligible_at,
        }


class OptimizationCycleController:
    """Detect when enough evidence exists to begin a controlled optimization cycle."""

    def __init__(
        self,
        *,
        config: Optional[OptimizationCycleConfig] = None,
        evaluator: Optional[CapabilityEvaluator] = None,
    ) -> None:
        self.config = config or OptimizationCycleConfig()
        self.evaluator = evaluator or CapabilityEvaluator()

    def assess(
        self,
        experience_log: ExperienceLog,
        capability_ids: Iterable[str],
        *,
        now: Optional[datetime] = None,
        last_cycle_at: Optional[datetime] = None,
        cycle_id: Optional[str] = None,
    ) -> OptimizationCyclePlan:
        """Return a threshold/cooldown-gated optimization plan."""
        current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        total = len(experience_log.tasks)
        failures = sum(1 for task in experience_log.tasks if task.is_failure)
        failure_rate = (failures / total) if total else 0.0

        reasons: List[str] = []
        if total >= self.config.minimum_total_observations:
            reasons.append("minimum_total_observations")
        if failure_rate >= self.config.minimum_failure_rate:
            reasons.append("failure_rate_threshold")

        eligible_by_capability = self._underperforming_capabilities(experience_log, capability_ids)
        if eligible_by_capability:
            reasons.append("underperforming_capability")

        cooldown_active = False
        next_eligible = current
        if last_cycle_at is not None:
            previous = last_cycle_at.astimezone(timezone.utc)
            next_eligible = previous.replace(microsecond=0)  # deterministic serialization baseline
            next_eligible = previous + _seconds(self.config.cooldown_seconds)
            cooldown_active = current < next_eligible
            if cooldown_active:
                reasons.append("cooldown_active")

        trigger_reasons = [item for item in reasons if item != "cooldown_active"]
        triggered = bool(trigger_reasons) and not cooldown_active
        cycle_timestamp = current.isoformat()
        resolved_id = cycle_id or f"OPT-{current.strftime('%Y%m%dT%H%M%S%fZ')}"

        return OptimizationCyclePlan(
            cycle_id=resolved_id,
            triggered=triggered,
            reasons=reasons,
            total_observations=total,
            failure_rate=failure_rate,
            candidates=eligible_by_capability,
            created_at=cycle_timestamp,
            next_eligible_at=next_eligible.isoformat(),
        )

    def _underperforming_capabilities(
        self,
        experience_log: ExperienceLog,
        capability_ids: Iterable[str],
    ) -> List[CapabilityEvaluation]:
        evaluations = [
            self.evaluator.evaluate(experience_log, capability_id)
            for capability_id in capability_ids
        ]
        return sorted(
            [
                item
                for item in evaluations
                if item.observations >= self.config.minimum_capability_observations
                and item.score <= self.config.minimum_capability_score
            ],
            key=lambda item: (item.score, -item.observations, item.capability_id),
        )


def _seconds(value: float):
    from datetime import timedelta

    return timedelta(seconds=max(0.0, float(value)))


__all__ = [
    "OptimizationCycleConfig",
    "OptimizationCyclePlan",
    "OptimizationCycleController",
]
