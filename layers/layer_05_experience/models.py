"""Data models for Layer 5 (Experience).

A ``Task`` is one durable record of SPS-CA attempting to satisfy a request.
Execution provenance is intentionally part of Experience so Web UI, CLI and
scenario evaluation can share one historical memory without changing the
canonical layer structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal, Optional

TaskStatus = Literal["success", "failure", "partial"]


@dataclass
class Task:
    """A single logged task execution.

    Existing fields are backward-compatible. New provenance fields identify
    where the execution came from and let later reasoning retrieve historical
    outcomes without replaying the original request.
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
    source: str = ""
    scenario_id: str = ""
    run_id: str = ""
    feedback: str = ""
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Task.id must be non-empty")
        if self.status not in ("success", "failure", "partial"):
            raise ValueError(
                f"Task.status must be 'success', 'failure' or 'partial', "
                f"got {self.status!r}"
            )
        if self.status == "failure" and not self.failure_category:
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
            source=data.get("source", ""),
            scenario_id=data.get("scenario_id", ""),
            run_id=data.get("run_id", ""),
            feedback=data.get("feedback", ""),
            error=data.get("error"),
            metadata=dict(data.get("metadata", {}) or {}),
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
            "source": self.source,
            "scenario_id": self.scenario_id,
            "run_id": self.run_id,
            "feedback": self.feedback,
            "error": self.error,
            "metadata": dict(self.metadata),
        }
