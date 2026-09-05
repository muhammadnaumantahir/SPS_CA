"""Experience log: append-only task history for Layer 3.

The ``ExperienceLog`` is the single source of truth that Layer 4
(Meta-Learning) and Layer 5 (Adaptation) read from. It never mutates past
tasks — it only appends — so that improvement can be measured over time
against a stable history (see Section 21, Metrics & Measurement Framework).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Union

from .models import Task

DEFAULT_LOG_PATH = "experience/logs/experience_log.json"
DEFAULT_FAILURE_PATTERNS_PATH = "experience/logs/failure_patterns.json"


class ExperienceLog:
    """Append-only collection of :class:`Task` records plus derived metrics."""

    def __init__(self, tasks: Optional[List[Task]] = None) -> None:
        self.tasks: List[Task] = list(tasks) if tasks else []
        self.metrics: Dict[str, float] = {}

    # -- Recording ---------------------------------------------------

    def add_task(self, task: Task) -> None:
        """Append a task to the log and refresh derived metrics."""
        self.tasks.append(task)
        self._recompute_metrics()

    # -- Queries -------------------------------------------------------

    def get_failure_patterns(self) -> Dict[str, int]:
        """Return ``{failure_category: count}`` across all failed tasks."""
        counts: Counter = Counter(
            task.failure_category
            for task in self.tasks
            if task.is_failure and task.failure_category
        )
        return dict(counts)

    def get_capability_success_rate(self, capability_id: str) -> float:
        """Return the success rate (0.0-1.0) of a given capability.

        Returns 0.0 if the capability has never been used — callers that
        need to distinguish "no data" from "always fails" should check
        :meth:`get_capability_usage_count` first.
        """
        used = [t for t in self.tasks if t.selected_capability == capability_id]
        if not used:
            return 0.0
        successes = sum(1 for t in used if t.status == "success")
        return successes / len(used)

    def get_capability_usage_count(self, capability_id: str) -> int:
        return sum(1 for t in self.tasks if t.selected_capability == capability_id)

    def get_overall_success_rate(self) -> float:
        if not self.tasks:
            return 0.0
        successes = sum(1 for t in self.tasks if t.status == "success")
        return successes / len(self.tasks)

    # -- Persistence -----------------------------------------------------

    def save_to_json(self, path: Union[str, Path] = DEFAULT_LOG_PATH) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "tasks": [t.to_dict() for t in self.tasks],
            "metrics": self.metrics,
        }
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load_from_json(
        cls, path: Union[str, Path] = DEFAULT_LOG_PATH
    ) -> "ExperienceLog":
        path = Path(path)
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        log = cls(tasks)
        log.metrics.update(data.get("metrics", {}))
        log._recompute_metrics()
        return log

    def save_failure_patterns(
        self, path: Union[str, Path] = DEFAULT_FAILURE_PATTERNS_PATH
    ) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.get_failure_patterns(), indent=2) + "\n", encoding="utf-8"
        )

    # -- Internal ------------------------------------------------------

    def _recompute_metrics(self) -> None:
        self.metrics["total_tasks"] = float(len(self.tasks))
        self.metrics["overall_success_rate"] = self.get_overall_success_rate()
        failures = sum(1 for t in self.tasks if t.is_failure)
        self.metrics["failure_count"] = float(failures)
