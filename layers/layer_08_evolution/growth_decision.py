"""Reasoned Layer-8 SPS Growth Decision.

Disagreement is evidence, not an automatic capability-creation trigger. This
module keeps the growth decision explicit and auditable so Layer 8 decides
whether the system should reuse, adapt, compose, improve, create, or defer.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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


class GrowthDecisionEngine:
    """Choose the least-structural growth action justified by evidence."""

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
    ) -> GrowthDecisionResult:
        evidence = {
            "existing_capability_id": existing_capability_id,
            "disagreement_count": max(0, disagreement_count),
            "capability_match": capability_match,
            "repeated_pattern": repeated_pattern,
            "adaptation_viable": adaptation_viable,
            "composition_viable": composition_viable,
            "improvement_viable": improvement_viable,
        }
        if capability_match and adaptation_viable:
            return self._result(GrowthDecision.ADAPT, "adapt", f"{existing_capability_id or 'Existing capability'} can address the request through contextual adaptation; structural growth is unnecessary.", evidence)
        if capability_match and composition_viable:
            return self._result(GrowthDecision.COMPOSE, "composition_pattern", "Existing capabilities cover the required primitives and a reusable composition is justified.", evidence)
        if capability_match and improvement_viable:
            return self._result(GrowthDecision.IMPROVE, "capability_degradation", f"{existing_capability_id} is relevant but improvement is better justified than creating another capability.", evidence)
        if repeated_pattern and disagreement_count >= 3:
            return self._result(GrowthDecision.CREATE, "persistent_capability_gap", f"The unmet pattern persisted across {disagreement_count} disagreement signals and no lower-structural response was selected; a specialized reusable capability is justified.", evidence)
        if capability_match:
            return self._result(GrowthDecision.REUSE, "capability_sufficient", f"{existing_capability_id} is sufficiently relevant for the request; reuse it without structural growth.", evidence)
        if not capability_match and not existing_capability_id:
            return self._result(GrowthDecision.CREATE, "capability_gap", "No suitable registered capability matches the requested behavior, so a genuine capability gap is present.", evidence)
        return self._result(GrowthDecision.DEFER, "insufficient_gap", "Evidence does not yet justify structural capability growth; preserve the signal for future reasoning.", evidence)

    @staticmethod
    def _result(decision, reason_code, reasoning, evidence):
        return GrowthDecisionResult(decision, reason_code, reasoning, evidence)


__all__ = ["GrowthDecision", "GrowthDecisionResult", "GrowthDecisionEngine"]
