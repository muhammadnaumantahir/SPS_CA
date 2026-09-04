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

    def __init__(self, thresholds: GrowthScoreThresholds | None = None) -> None:
        self.thresholds = thresholds or GrowthScoreThresholds()

    def decide(self, *, existing_capability_id: str = "", disagreement_count: int = 0, capability_match: bool = False, repeated_pattern: bool = False, adaptation_viable: bool = False, composition_viable: bool = False, improvement_viable: bool = False, capability_fitness: float | None = None, recurrence: float | None = None, adaptation_viability: float | None = None, improvement_viability: float | None = None, composition_viability: float | None = None, creation_need: float | None = None, confidence: float | None = None, regression_risk: float | None = None, evidence: Mapping[str, object] | None = None) -> GrowthDecisionResult:
        values = {
            "existing_capability_id": existing_capability_id,
            "disagreement_count": max(0, int(disagreement_count)),
            "capability_match": bool(capability_match), "repeated_pattern": bool(repeated_pattern),
            "capability_fitness": self._clip(capability_fitness, 100.0 if capability_match else 0.0),
            "recurrence": self._clip(recurrence, min(100.0, max(0, int(disagreement_count)) * 25.0)),
            "adaptation_viability": self._clip(adaptation_viability, 100.0 if adaptation_viable else 0.0),
            "improvement_viability": self._clip(improvement_viability, 100.0 if improvement_viable else 0.0),
            "composition_viability": self._clip(composition_viability, 100.0 if composition_viable else 0.0),
            "creation_need": self._clip(creation_need, 100.0 if (not capability_match and repeated_pattern) else 0.0),
            "confidence": self._clip(confidence, 100.0 if (capability_match or repeated_pattern) else 0.0),
            "regression_risk": self._clip(regression_risk, 0.0),
        }
        scores = self._score_actions(values)
        combined_evidence = dict(evidence or {}); combined_evidence.update(values)
        selected = self._select(scores, values)
        reason_code, reasoning = self._explain(selected)
        return GrowthDecisionResult(selected, reason_code, reasoning, combined_evidence, scores)

    def _score_actions(self, values: dict[str, object]) -> dict[str, float]:
        fitness = float(values["capability_fitness"]); recurrence = float(values["recurrence"]); adaptation = float(values["adaptation_viability"]); improvement = float(values["improvement_viability"]); composition = float(values["composition_viability"]); creation = float(values["creation_need"]); confidence = float(values["confidence"]); risk = float(values["regression_risk"]); match = bool(values["capability_match"])
        scores = {
            "reuse": self._weighted((fitness, .55), (100.0-risk, .15), (confidence, .30)) if match else 0.0,
            "adapt": self._weighted((adaptation, .55), (recurrence, .15), (confidence, .30)) if match else 0.0,
            "improve": self._weighted((improvement, .55), (100.0-fitness, .20), (recurrence, .10), (confidence, .15)) if match else 0.0,
            "compose": self._weighted((composition, .60), (recurrence, .15), (confidence, .25)) if match else 0.0,
            "create": self._weighted((creation, .50), (recurrence, .20), (confidence, .20), (100.0-fitness, .10)),
        }
        return {key: round(value, 2) for key, value in scores.items()}

    def _select(self, scores: dict[str, float], values: dict[str, object]) -> GrowthDecision:
        t = self.thresholds
        if float(values["confidence"]) < t.confidence_min: return GrowthDecision.DEFER
        if bool(values["capability_match"]) and float(values["capability_fitness"]) >= t.reuse_min and scores["reuse"] >= t.reuse_min: return GrowthDecision.REUSE
        for action, score in sorted(scores.items(), key=lambda item: item[1], reverse=True):
            if score < getattr(t, f"{action}_min"): continue
            if action == "create" and bool(values["capability_match"]) and float(values["capability_fitness"]) >= t.improve_min: continue
            return GrowthDecision(action)
        return GrowthDecision.DEFER

    @staticmethod
    def _explain(decision: GrowthDecision) -> tuple[str, str]:
        return {
            GrowthDecision.REUSE: ("capability_sufficient", "Existing capability fitness is high enough to reuse without structural growth."),
            GrowthDecision.ADAPT: ("contextual_adaptation", "Evidence shows the existing capability is suitable after contextual adaptation."),
            GrowthDecision.IMPROVE: ("capability_degradation", "The capability remains relevant but scored improvement is better justified than replacement."),
            GrowthDecision.COMPOSE: ("composition_pattern", "Existing capabilities cover the required primitives and the composition score justifies a reusable composite."),
            GrowthDecision.CREATE: ("capability_gap", "Evidence and confidence indicate a genuine capability gap with sufficient creation score."),
            GrowthDecision.DEFER: ("insufficient_evidence", "Evidence does not yet justify structural growth with sufficient confidence."),
        }[decision]

    @staticmethod
    def _weighted(*parts: tuple[float, float]) -> float: return sum(value * weight for value, weight in parts)
    @staticmethod
    def _clip(value: object, default: float) -> float:
        try: result = default if value is None else float(value)
        except (TypeError, ValueError): result = default
        return max(0.0, min(100.0, result))


__all__ = ["GrowthDecision", "GrowthDecisionResult", "GrowthDecisionEngine", "GrowthScoreThresholds"]
