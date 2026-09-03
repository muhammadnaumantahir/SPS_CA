"""Layer 06: Meta-Learning.

``MetaLearner`` reads Layer 05's :class:`ExperienceLog` and turns raw task
history into actionable strategy changes: detecting when a capability is
failing too often, recommending a better-performing alternative, and
measuring whether success rates are actually improving over time.

Meta-learning only recommends strategy changes for future task routing. It
does not modify code or capabilities itself. Capability generation is Layer 08
(Evolution)'s responsibility.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from layers.layer_05_experience.experience_log import ExperienceLog

from .capability_evaluator import CapabilityEvaluator
from .models import MetaLearningDecision

DEFAULT_DECISIONS_PATH = "experience/logs/meta_learning_decisions.json"
DEFAULT_MIN_OCCURRENCES = 3
DEFAULT_FAILURE_RATE_THRESHOLD = 0.2


class MetaLearner:
    """Detect failure patterns and recommend capability strategy changes."""

    def __init__(self, evaluator: Optional[CapabilityEvaluator] = None) -> None:
        self.evaluator = evaluator or CapabilityEvaluator()

    def analyze_failure_patterns(self, experience_log: ExperienceLog) -> Dict[str, int]:
        """Return ``{failure_category: count}`` from the experience log."""
        return experience_log.get_failure_patterns()

    def detect_capability_failure(
        self,
        experience_log: ExperienceLog,
        capability_id: str,
        min_occurrences: int = DEFAULT_MIN_OCCURRENCES,
        failure_rate_threshold: float = DEFAULT_FAILURE_RATE_THRESHOLD,
    ) -> bool:
        """True if ``capability_id`` has failed often enough to act on."""
        usage_count = experience_log.get_capability_usage_count(capability_id)
        if usage_count < min_occurrences:
            return False
        failure_rate = 1.0 - experience_log.get_capability_success_rate(capability_id)
        return failure_rate > failure_rate_threshold

    def recommend_strategy_change(
        self,
        experience_log: ExperienceLog,
        failed_capability_id: str,
        candidate_capability_ids: Optional[List[str]] = None,
    ) -> str:
        """Recommend the best evidenced alternative capability.

        Phase 2 replaces raw success-rate comparison with the bounded
        behavioral evaluator, which accounts for success, partial outcomes,
        latency and evidence confidence. Candidates still need the evaluator's
        minimum evidence before they can win a recommendation.
        """
        if candidate_capability_ids is None:
            candidate_capability_ids = sorted(
                {
                    task.selected_capability
                    for task in experience_log.tasks
                    if task.selected_capability
                    and task.selected_capability != failed_capability_id
                }
            )

        best_id = self.evaluator.choose_best(
            experience_log,
            candidate_capability_ids,
            min_observations=DEFAULT_MIN_OCCURRENCES,
        )
        if best_id is None:
            return (
                f"No alternative capability with sufficient usage history to "
                f"recommend replacing {failed_capability_id}."
            )
        return best_id

    def evaluate_capabilities(
        self,
        experience_log: ExperienceLog,
        capability_ids: List[str],
        *,
        min_observations: int = DEFAULT_MIN_OCCURRENCES,
    ):
        """Return Phase 2 evidence-ranked capability evaluations."""
        return self.evaluator.rank(
            experience_log,
            capability_ids,
            min_observations=min_observations,
        )

    def measure_improvement(
        self, experience_log: ExperienceLog, baseline_success_rate: float
    ) -> float:
        """Return percentage improvement of current success rate over baseline."""
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
    def load_from_json(
        cls, path: Union[str, Path] = DEFAULT_DECISIONS_PATH
    ) -> "MetaLearningDecisionLog":
        path = Path(path)
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        decisions = [MetaLearningDecision.from_dict(item) for item in data.values()]
        return cls(decisions)
