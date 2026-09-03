"""Evidence-based retirement of persistently poor generated capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from layers.capability_registry import CapabilityRegistryManager
from layers.layer_02_governance import ChangeType, GovernanceGate
from layers.layer_02_governance.models import DecisionStatus
from layers.layer_05_experience import ExperienceLog
from layers.layer_06_meta_learning import CapabilityEvaluator


@dataclass(frozen=True)
class RetirementRecommendation:
    capability_id: str
    observations: int
    score: float
    eligible: bool
    reason: str
    confidence: float = 0.0
    recommended_action: str = "retain"
    evidence_strength: str = "insufficient"


class GovernedRetirementManager:
    """Recommend and, after Governance approval, deactivate generated variants."""

    DEFAULT_MIN_OBSERVATIONS = 5
    DEFAULT_MAX_SCORE = 0.35

    def __init__(self, registry: Optional[CapabilityRegistryManager] = None, governance: Optional[GovernanceGate] = None) -> None:
        self.registry = registry or CapabilityRegistryManager()
        self.governance = governance or GovernanceGate()
        self.evaluator = CapabilityEvaluator()

    def recommend(self, experience_log: ExperienceLog, capability_id: str, *, min_observations: int = DEFAULT_MIN_OBSERVATIONS, max_score: float = DEFAULT_MAX_SCORE) -> RetirementRecommendation:
        capability = self.registry.get_capability(capability_id)
        if capability is None:
            return RetirementRecommendation(capability_id, 0, 0.0, False, "capability_not_found")
        if not capability.generated:
            return RetirementRecommendation(capability_id, 0, 0.0, False, "canonical_capability_protected")
        if capability.status != "active":
            return RetirementRecommendation(capability_id, 0, 0.0, False, "capability_not_active")

        evaluation = self.evaluator.evaluate(experience_log, capability_id)
        minimum = max(1, int(min_observations))
        eligible = evaluation.observations >= minimum and evaluation.score <= max(0.0, float(max_score))
        evidence_ratio = min(1.0, evaluation.observations / max(1.0, minimum * 2.0))
        confidence = round(0.35 + evidence_ratio * 0.5 + (0.15 if evaluation.score <= max_score else 0.0), 4)
        if evaluation.observations < minimum:
            reason, action, strength = "insufficient_observations", "retain", "insufficient"
        elif evaluation.score > max_score:
            reason, action, strength = "score_not_low_enough", "retain", "adequate"
        else:
            reason, action, strength = "persistent_underperformance", "retire", "strong" if confidence >= 0.75 else "moderate"
        return RetirementRecommendation(
            capability_id=capability_id,
            observations=evaluation.observations,
            score=evaluation.score,
            eligible=eligible,
            reason=reason,
            confidence=confidence,
            recommended_action=action,
            evidence_strength=strength,
        )

    def retire(self, experience_log: ExperienceLog, capability_id: str, *, min_observations: int = DEFAULT_MIN_OBSERVATIONS, max_score: float = DEFAULT_MAX_SCORE) -> dict:
        recommendation = self.recommend(experience_log, capability_id, min_observations=min_observations, max_score=max_score)
        if not recommendation.eligible:
            return {"retired": False, "recommendation": recommendation, "governance": None, "action": recommendation.recommended_action}

        capability = self.registry.get_capability(capability_id)
        decision = self.governance.make_decision(
            change_id=f"retirement_{capability_id}",
            change_type=ChangeType.EVOLUTION,
            change_description=f"Deactivate generated capability {capability_id} after persistent underperformance",
            affected_files=[capability.metadata_path] if capability and capability.metadata_path else [],
            related_capabilities=[capability_id],
        )
        approved = decision.decision in {DecisionStatus.AUTO_APPROVED, DecisionStatus.APPROVED}
        retired = approved and self.registry.deprecate_capability(capability_id)
        return {
            "retired": retired,
            "recommendation": recommendation,
            "governance": decision.decision.value,
            "governance_rationale": decision.rationale,
            "action": "retired" if retired else "retain",
        }


__all__ = ["RetirementRecommendation", "GovernedRetirementManager"]
