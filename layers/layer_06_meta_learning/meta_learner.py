"""Layer 4: Meta-Learning.

``MetaLearner`` reads Layer 3's :class:`ExperienceLog` and turns raw task
history into actionable strategy changes: detecting when a capability is
failing too often, recommending a better-performing alternative, and
measuring whether success rates are actually improving over time.

Meta-learning only ever *recommends* strategy changes for future task
routing — it does not modify code or capabilities itself. Capability
generation (Type 7 change) is Layer 8 (Evolution)'s job.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from layers.layer_05_experience.experience_log import ExperienceLog

from .models import MetaLearningDecision

DEFAULT_DECISIONS_PATH = "experience/logs/meta_learning_decisions.json"
DEFAULT_MIN_OCCURRENCES = 3
DEFAULT_FAILURE_RATE_THRESHOLD = 0.2


class MetaLearner:
    """Detects failure patterns and recommends capability strategy changes."""

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
        """True if ``capability_id`` has failed often enough to act on.

        Requires at least ``min_occurrences`` uses (to avoid reacting to
        noise from a single unlucky run) *and* a failure rate above
        ``failure_rate_threshold`` (default 20%, matching the example in
        the design: "If CAP-002 fails >20% of the
        time, recommend trying CAP-003 instead").
        """
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
        """Recommend a replacement capability for a failing one.

        Picks the candidate with the highest observed success rate in
        ``experience_log`` (excluding the failing capability itself). If no
        candidate has any usage history, falls back to a descriptive string
        explaining that there isn't enough data yet, rather than guessing.
        """
        if candidate_capability_ids is None:
            candidate_capability_ids = sorted(
                {
                    t.selected_capability
                    for t in experience_log.tasks
                    if t.selected_capability
                    and t.selected_capability != failed_capability_id
                }
            )

        best_id: Optional[str] = None
        best_rate = -1.0
        for candidate_id in candidate_capability_ids:
            if experience_log.get_capability_usage_count(candidate_id) == 0:
                continue
            rate = experience_log.get_capability_success_rate(candidate_id)
            if rate > best_rate:
                best_rate = rate
                best_id = candidate_id

        if best_id is None:
            return (
                f"No alternative capability with sufficient usage history to "
                f"recommend replacing {failed_capability_id}."
            )
        return best_id

    def measure_improvement(
        self, experience_log: ExperienceLog, baseline_success_rate: float
    ) -> float:
        """Return percentage improvement of current success rate over baseline.

        E.g. baseline 0.50, current 0.65 -> 30.0 (a 30% relative
        improvement), matching the target of >15% improvement over the
        evaluation horizon.
        """
        current = experience_log.get_overall_success_rate()
        if baseline_success_rate <= 0:
            return current * 100.0
        return ((current - baseline_success_rate) / baseline_success_rate) * 100.0


class MetaLearningDecisionLog:
    """Append-only, persisted history of :class:`MetaLearningDecision` records."""

    def __init__(self, decisions: Optional[List[MetaLearningDecision]] = None) -> None:
        self.decisions: List[MetaLearningDecision] = (
            list(decisions) if decisions else []
        )

    def add_decision(self, decision: MetaLearningDecision) -> None:
        self.decisions.append(decision)

    def save_to_json(self, path: Union[str, Path] = DEFAULT_DECISIONS_PATH) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {d.decision_id: d.to_dict() for d in self.decisions}
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load_from_json(
        cls, path: Union[str, Path] = DEFAULT_DECISIONS_PATH
    ) -> "MetaLearningDecisionLog":
        path = Path(path)
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        decisions = [MetaLearningDecision.from_dict(d) for d in data.values()]
        return cls(decisions)
