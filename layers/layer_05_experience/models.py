"""Data models for Layer 3 (Experience).

A ``Task`` is one record of SPS-CA attempting to satisfy a user request
against a target project using a selected capability. Tasks are append-only
history: nothing in the system rewrites a past task, it only adds new ones
(see :class:`~layers.layer_05_experience.experience_log.ExperienceLog`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal, Optional

TaskStatus = Literal["success", "failure", "partial"]


@dataclass
class Task:
    """A single logged task execution.

    Attributes:
        id: Stable identifier, e.g. ``"task_001"``.
        user_request: The original natural-language request.
        target_project: Path (or name) of the project the task targeted.
        target_language: ``"python"``, ``"java"``, ``"javascript"``,
            ``"go"``, ``"csharp"``, etc.
        status: Outcome of the task.
        selected_capability: Capability id applied, e.g. ``"CAP-002"``.
        outcome: Short human-readable description of what happened.
        failure_category: Set only when ``status == "failure"``; used by
            Layer 4 (Meta-Learning) to detect recurring failure patterns.
        time_taken_seconds: Wall-clock duration of the task.
        timestamp: When the task was recorded. Defaults to now (UTC).
    """

    id: str
    user_request: str
    target_project: str = ""
    target_language: str = ""
    status: TaskStatus = "success"
    selected_capability: str = ""
    outcome: str = ""
    failure_category: Optional[str] = None
    time_taken_seconds: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Task.id must be non-empty")
        if self.status not in ("success", "failure", "partial"):
            raise ValueError(
                f"Task.status must be 'success', 'failure' or 'partial', "
                f"got {self.status!r}"
            )
        if self.status == "failure" and not self.failure_category:
            # A failure without a category can't feed failure-pattern
            # detection in Layer 4, so default it rather than silently
            # dropping the signal.
            self.failure_category = "Uncategorized"
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

    @property
    def is_failure(self) -> bool:
        return self.status == "failure"

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data["id"],
            user_request=data.get("user_request", ""),
            target_project=data.get("target_project", ""),
            target_language=data.get("target_language", ""),
            status=data.get("status", "success"),
            selected_capability=data.get("selected_capability", ""),
            outcome=data.get("outcome", ""),
            failure_category=data.get("failure_category"),
            time_taken_seconds=data.get("time_taken_seconds", 0.0),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_request": self.user_request,
            "target_project": self.target_project,
            "target_language": self.target_language,
            "status": self.status,
            "selected_capability": self.selected_capability,
            "outcome": self.outcome,
            "failure_category": self.failure_category,
            "time_taken_seconds": self.time_taken_seconds,
            "timestamp": self.timestamp.isoformat(),
        }
