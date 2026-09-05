"""Transactional outcome model for governed Layer-8 Evolution cycles.

The model keeps planning, promotion, rollback, and measured improvement as one
auditable record. It does not execute changes itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class EvolutionCycleOutcome:
    """Auditable outcome for one controlled self-programming attempt."""

    cycle_id: str
    capability_id: str
    source_capability_id: str = ""
    authorized: bool = False
    executed: bool = False
    promoted: bool = False
    rolled_back: bool = False
    improvement_measured: bool = False
    improved: bool = False
    score_delta: Optional[float] = None
    result: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if not self.cycle_id:
            raise ValueError("cycle_id must be non-empty")
        if not self.capability_id:
            raise ValueError("capability_id must be non-empty")
        if self.score_delta is not None and not isinstance(self.score_delta, (int, float)):
            raise TypeError("score_delta must be numeric or None")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "capability_id": self.capability_id,
            "source_capability_id": self.source_capability_id,
            "authorized": self.authorized,
            "executed": self.executed,
            "promoted": self.promoted,
            "rolled_back": self.rolled_back,
            "improvement_measured": self.improvement_measured,
            "improved": self.improved,
            "score_delta": self.score_delta,
            "result": dict(self.result),
            "timestamp": self.timestamp,
        }


__all__ = ["EvolutionCycleOutcome"]
