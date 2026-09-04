"""Reasoned Layer-8 SPS Growth Decision.

Evidence produces action scores rather than a hard disagreement-count trigger.
Historical counts remain useful evidence, but the decision is driven by
capability fitness, recurrence, viability, confidence and regression risk.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class GrowthDecision(str, Enum):
    REUSE = "reuse"
    ADAPT = "adapt"
    COMPOSE = "compose"
    IMPROVE = "improve"
    CREATE = "create"
    DEFER = "defer"


@dataclass(frozen=True)
class GrowthDecisionResult:
    decision: GrowthDecision
    reason_code: str
    reasoning: str
    evidence: dict[str, object]
    scores: dict[str, float]


@dataclass(frozen=True)
class GrowthScoreThresholds:
    reuse_min: float = 90.0
    adapt_min: float = 70.0
    improve_min: float = 65.0
    compose_min: float = 60.0
    create_min: float = 70.0
    confidence_min: float = 60.0


class GrowthDecisionEngine:
    """Choose the least-structural growth action justified by scored evidence."""

    _ACTIONS = tuple(decision.value for decision in GrowthDecision if decision is not GrowthDecision.DEFER)

    def __init__(self, thresholds: GrowthScoreThresholds | None = None) -> None:
        self.thresholds = thresholds or GrowthScoreThresholds()

    def decide(
        self,
        *,
        existing_capability_id: str = "",
        disagreement_count: int = 0,
        capability_match: bool = False,
        repeated_pattern: bool = False,
        adaptation_viable: bool = False,
        composition_viable: bool = False,
        improvement_viable: bool = False,
        capability_fitness: float | None = None,
        recurrence: float | None = None,
        adaptation_viability: float | None = None,
        improvement_viability: float | None = None,
        composition_viability: float | None = None,
        creation_need: float | None = None,
        confidence: float | None = None,
        regression_risk: float | None = None,
        evidence: Mapping[str, object] | None = None,
    ) -> GrowthDecisionResult:
        values = self._normalise_inputs(
            existing_capability_id=existing_capability_id,
            disagreement_count=disagreement_count,
            capability_match=capability_match,
            repeated_pattern=repeated_pattern,
            adaptation_viable=adaptation_viable,
            composition_viable=composition_viable,
            improvement_viable=improvement_viable,
            capability_fitness=capability_fitness,
            recurrence=recurrence,
            adaptation_viability=adaptation_viability,
            improvement_viability=improvement_viability,
            composition_viability=composition_viability,
            creation_need=creation_need,
            confidence=confidence,
            regression_risk=regression_risk,
        )
        scores = self._score_actions(values)
        combined_evidence = dict(evidence or {})
        combined_evidence.update(values)
        selected = self._select(scores, values)
        reason_code, reasoning = self._explain(selected, values, scores)
        return self._result(selected, reason_code, reasoning, combined_evidence, scores)

    def _normalise_inputs(self, **kwargs: object) -> dict[str, object]:
        capability_fitness = self._clip(kwargs.pop("capability_fitness"), 100.0 if kwargs.get("capability_match") else 0.0)
        disagreement_count = max(0, int(kwargs["disagreement_count"]))
        recurrence_default = min(100.0, disagreement_count * 25.0)
        return {
            **kwargs,
            "disagreement_count": disagreement_count,
            "capability_fitness": capability_fitness,
            "recurrence": self._clip(kwargs.pop("recurrence"), recurrence_default),
            "adaptation_viability": self._clip(kwargs.pop("adaptation_viability"), 100.0 if kwargs.get("adaptation_viable") else 0.0),
            "improvement_viability": self._clip(kwargs.pop("improvement_viability"), 100.0 if kwargs.get("improvement_viable") else 0.0),
            "composition_viability": self._clip(kwargs.pop("composition_viability"), 100.0 if kwargs.get("composition_viable") else 0.0),
            "creation_need": self._clip(kwargs.pop("creation_need"), 100.0 if (not kwargs.get("capability_match") and kwargs.get("repeated_pattern")) else 0.0),
            "confidence": self._clip(kwargs.pop("confidence"), 100.0 if (kwargs.get("capability_match") or kwargs.get("repeated_pattern")) else 0.0),
            "regression_risk": self._clip(kwargs.pop("regression_risk"), 0.0),
        }

    def _score_actions(self, values: dict[str, object]) -> dict[str, float]:
        fitness = float(values["capability_fitness"])
        recurrence = float(values["recurrence"])
        adaptation = float(values["adaptation_viability"])
        improvement = float(values["improvement_viability"])
        composition = float(values["composition_viability"])
        creation = float(values["creation_need"])
        confidence = float(values["confidence"])
        risk = float(values["regression_risk"])
        match = bool(values["capability_match"])

        scores = {
            "reuse": self._weighted((fitness, 0.55), (100.0 - risk, 0.15), (confidence, 0.30)) if match else 0.0,
            "adapt": self._weighted((adaptation, 0.55), (recurrence, 0.15), (confidence, 0.30)) if match else 0.0,
            "improve": self._weighted((improvement, 0.55), (100.0 - fitness, 0.20), (recurrence, 0.10), (confidence, 0.15)) if match else 0.0,
            "compose": self._weighted((composition, 0.60), (recurrence, 0.15), (confidence, 0.25)) if match else 0.0,
            "create": self._weighted((creation, 0.50), (recurrence, 0.20), (confidence, 0.20), (100.0 - fitness, 0.10)) if not match else self._weighted((creation, 0.55), (recurrence, 0.20), (confidence, 0.20), (100.0 - fitness, 0.05)),
        }
        return {key: round(value, 2) for key, value in scores.items()}

    def _select(self, scores: dict[str, float], values: dict[str, object]) -> GrowthDecision:
        confidence = float(values["confidence"])
        match = bool(values["capability_match"])
        fitness = float(values["capability_fitness"])
        thresholds = self.thresholds

        if confidence < thresholds.confidence_min:
            return GrowthDecision.DEFER
        if match and fitness >= thresholds.reuse_min and scores["reuse"] >= thresholds.reuse_min:
            return GrowthDecision.REUSE

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        for action, score in ranked:
            threshold = getattr(thresholds, f"{action}_min")
            if score < threshold:
                continue
            if action == "create" and match and fitness >= thresholds.improve_min:
                continue
            return GrowthDecision(action)
        return GrowthDecision.DEFER

    @staticmethod
    def _explain(decision: GrowthDecision, values: dict[str, object], scores: dict[str, float]) -> tuple[str, str]:
        if decision is GrowthDecision.REUSE:
            return "capability_sufficient", "Existing capability fitness is high enough to reuse without structural growth."
        if decision is GrowthDecision.ADAPT:
            return "contextual_adaptation", "Evidence shows the existing capability is suitable after contextual adaptation."
        if decision is GrowthDecision.IMPROVE:
            return "capability_degradation", "The capability remains relevant but scored improvement is better justified than replacement."
        if decision is GrowthDecision.COMPOSE:
            return "composition_pattern", "Existing capabilities cover the required primitives and the composition score justifies a reusable composite."
        if decision is GrowthDecision.CREATE:
            return "capability_gap", "Evidence and confidence indicate a genuine capability gap with sufficient creation score."
        return "insufficient_evidence", "Evidence does not yet justify structural growth with sufficient confidence."

    @staticmethod
    def _weighted(*parts: tuple[float, float]) -> float:
        return sum(value * weight for value, weight in parts)

    @staticmethod
    def _clip(value: object, default: float) -> float:
        try:
            result = default if value is None else float(value)
        except (TypeError, ValueError):
            result = default
        return max(0.0, min(100.0, result))

    @staticmethod
    def _result(decision, reason_code, reasoning, evidence, scores):
        return GrowthDecisionResult(decision, reason_code, reasoning, evidence, scores)


__all__ = ["GrowthDecision", "GrowthDecisionResult", "GrowthDecisionEngine", "GrowthScoreThresholds"]
