"""Data models for Layer 6 (Meta-Learning)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class MetaLearningDecision:
    """Auditable strategy-change decision backed by measured evidence."""

    decision_id: str
    triggered_by: str
    previous_strategy: str
    new_strategy: str
    rationale: str
    evidence: Optional[dict[str, Any]] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("MetaLearningDecision.decision_id must be non-empty")
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if self.evidence is not None and not isinstance(self.evidence, dict):
            raise ValueError("MetaLearningDecision.evidence must be a mapping")

    @classmethod
    def from_dict(cls, data: dict) -> "MetaLearningDecision":
        return cls(
            decision_id=data["decision_id"],
            triggered_by=data.get("triggered_by", ""),
            previous_strategy=data.get("previous_strategy", ""),
            new_strategy=data.get("new_strategy", ""),
            rationale=data.get("rationale", ""),
            evidence=data.get("evidence"),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
        )

    def to_dict(self) -> dict:
        return {
            "decision_id": self.decision_id,
            "triggered_by": self.triggered_by,
            "previous_strategy": self.previous_strategy,
            "new_strategy": self.new_strategy,
            "rationale": self.rationale,
            "evidence": self.evidence or {},
            "timestamp": self.timestamp.isoformat(),
        }
