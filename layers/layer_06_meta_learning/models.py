"""Data models for Layer 4 (Meta-Learning)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class MetaLearningDecision:
    """A single strategy-change decision made by :class:`MetaLearner`.

    Mirrors the ``meta_learning_decision_NNN`` records described in
    the design, kept as a first-class model so they
    can be validated, persisted, and unit tested like any other record.
    """

    decision_id: str
    triggered_by: str
    previous_strategy: str
    new_strategy: str
    rationale: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("MetaLearningDecision.decision_id must be non-empty")
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

    @classmethod
    def from_dict(cls, data: dict) -> "MetaLearningDecision":
        return cls(
            decision_id=data["decision_id"],
            triggered_by=data.get("triggered_by", ""),
            previous_strategy=data.get("previous_strategy", ""),
            new_strategy=data.get("new_strategy", ""),
            rationale=data.get("rationale", ""),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
        )

    def to_dict(self) -> dict:
        return {
            "decision_id": self.decision_id,
            "triggered_by": self.triggered_by,
            "previous_strategy": self.previous_strategy,
            "new_strategy": self.new_strategy,
            "rationale": self.rationale,
            "timestamp": self.timestamp.isoformat(),
        }
