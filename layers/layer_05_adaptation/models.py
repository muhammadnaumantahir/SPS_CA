"""Data models for Layer 5 (Adaptation)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict


@dataclass
class AdaptationRecord:
    """One logged adaptation: an existing capability reused with adjusted
    parameters for a new task/language, per the ``adaptation_NNN`` records
    described in the master document.

    Adaptations are Type 6 changes (Change Type Taxonomy, Section 11) — they
    reuse an existing capability with parameter adjustment and never trigger
    Evolution (Type 7, new capability generation).
    """

    id: str
    base_capability_id: str
    applied_to_task_id: str
    parameters_changed: Dict[str, str] = field(default_factory=dict)
    success: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("AdaptationRecord.id must be non-empty")
        if not self.base_capability_id:
            raise ValueError("AdaptationRecord.base_capability_id must be non-empty")
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

    @classmethod
    def from_dict(cls, data: dict) -> "AdaptationRecord":
        return cls(
            id=data["id"],
            base_capability_id=data["base_capability_id"],
            applied_to_task_id=data.get("applied_to_task_id", ""),
            parameters_changed=dict(data.get("parameters_changed", {})),
            success=data.get("success", False),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "base_capability_id": self.base_capability_id,
            "applied_to_task_id": self.applied_to_task_id,
            "parameters_changed": self.parameters_changed,
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
            "change_type": 6,
        }
