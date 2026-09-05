"""Layer 06: Meta-Learning.

Reads Layer 05 Experience evidence, detects recurring failures, compares
capability behavior, and persists auditable strategy recommendations.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Union

from layers.layer_05_experience.experience_log import ExperienceLog

from .capability_evaluator import CapabilityEvaluator
from .models import MetaLearningDecision
from .strategy_policy import StrategyPolicy, StrategyRecommendation

DEFAULT_DECISIONS_PATH = "experience/logs/meta_learning_decisions.json"
DEFAULT_MIN_OCCURRENCES = 3
DEFAULT_FAILURE_RATE_THRESHOLD = 0.2


class MetaLearner:
    """Detect failure patterns and recommend capability strategy changes."""

    def __init__(self, evaluator: Optional[CapabilityEvaluator] = None, policy: Optional[StrategyPolicy] = None) -> None:
        self.evaluator = evaluator or CapabilityEvaluator()
        self.policy = policy or StrategyPolicy(evaluator=self.evaluator)

    def analyze_failure_patterns(self, experience_log: ExperienceLog) -> Dict[str, int]:
        return experience_log.get_failure_patterns()

    def detect_capability_failure(self, experience_log: ExperienceLog, capability_id: str, min_occurrences: int = DEFAULT_MIN_OCCURRENCES, failure_rate_threshold: float = DEFAULT_FAILURE_RATE_THRESHOLD) -> bool:
        usage_count = experience_log.get_capability_usage_count(capability_id)
        if usage_count < min_occurrences:
            return False
        failure_rate = 1.0 - experience_log.get_capability_success_rate(capability_id)
        return failure_rate > failure_rate_threshold

    def recommend_strategy_change(self, experience_log: ExperienceLog, failed_capability_id: str, candidate_capability_ids: Optional[List[str]] = None) -> str:
        if candidate_capability_ids is None:
            candidate_capability_ids = sorted({task.selected_capability for task in experience_log.tasks if task.selected_capability and task.selected_capability != failed_capability_id})
        recommendation = self.policy.recommend(experience_log, failed_capability_id, candidate_capability_ids)
        if recommendation.recommended_capability_id is None:
            return f"No strategy switch recommended for {failed_capability_id}: {recommendation.reason}"
        return recommendation.recommended_capability_id

    def recommend_with_evidence(self, experience_log: ExperienceLog, current_capability_id: str, candidate_capability_ids: List[str], *, recent_selected_capabilities: List[str] | None = None) -> StrategyRecommendation:
        return self.policy.recommended_for_future_routing(
            experience_log,
            current_capability_id,
            candidate_capability_ids,
            recent_selected_capabilities=recent_selected_capabilities or [],
        )

    def create_decision(self, recommendation: StrategyRecommendation, *, triggered_by: str) -> MetaLearningDecision:
        """Convert a recommendation and measured evidence into an auditable record."""
        return MetaLearningDecision(
            decision_id=f"meta_learning_decision_{uuid.uuid4().hex[:12]}",
            triggered_by=triggered_by,
            previous_strategy=recommendation.current_capability_id,
            new_strategy=recommendation.recommended_capability_id or recommendation.current_capability_id,
            rationale=recommendation.reason,
            evidence=recommendation.to_dict(),
        )

    def evaluate_capabilities(self, experience_log: ExperienceLog, capability_ids: List[str], *, min_observations: int = DEFAULT_MIN_OCCURRENCES):
        return self.evaluator.rank(experience_log, capability_ids, min_observations=min_observations)

    def measure_improvement(self, experience_log: ExperienceLog, baseline_success_rate: float) -> float:
        current = experience_log.get_overall_success_rate()
        if baseline_success_rate <= 0:
            return current * 100.0
        return ((current - baseline_success_rate) / baseline_success_rate) * 100.0


class MetaLearningDecisionLog:
    """Append-only, persisted history of :class:`MetaLearningDecision` records."""

    def __init__(self, decisions: Optional[List[MetaLearningDecision]] = None) -> None:
        self.decisions: List[MetaLearningDecision] = list(decisions) if decisions else []

    def add_decision(self, decision: MetaLearningDecision) -> None:
        self.decisions.append(decision)

    def save_to_json(self, path: Union[str, Path] = DEFAULT_DECISIONS_PATH) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {decision.decision_id: decision.to_dict() for decision in self.decisions}
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load_from_json(cls, path: Union[str, Path] = DEFAULT_DECISIONS_PATH) -> "MetaLearningDecisionLog":
        path = Path(path)
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        decisions = [MetaLearningDecision.from_dict(item) for item in data.values()]
        return cls(decisions)
