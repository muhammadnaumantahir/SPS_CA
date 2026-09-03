"""Immutable DNA rule model.

A DNARule represents a constraint that governs what SPS-CA is permitted to
do to itself. Rules are loaded from ``governance/dna_rules.json`` and are
treated as read-only at runtime: nothing in the system is allowed to mutate
a loaded rule (see :class:`SoftwareDNA` for enforcement).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Severity = Literal["hard", "soft"]


@dataclass(frozen=True)
class DNARule:
    """A single immutable governance constraint.

    Attributes:
        id: Stable identifier, e.g. ``"rule_001"``.
        constraint: Human-readable description of the constraint.
        severity: ``"hard"`` rules cause a violating action to be rejected.
            ``"soft"`` rules are logged as warnings but do not block.
        category: Grouping used for reporting, e.g. ``"governance"``,
            ``"safety"``, ``"scope"``.
        rationale: Optional explanation of why the rule exists.
    """

    id: str
    constraint: str
    severity: Severity
    category: str = "general"
    rationale: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("DNARule.id must be non-empty")
        if not self.constraint:
            raise ValueError("DNARule.constraint must be non-empty")
        if self.severity not in ("hard", "soft"):
            raise ValueError(
                f"DNARule.severity must be 'hard' or 'soft', got {self.severity!r}"
            )

    @property
    def is_hard(self) -> bool:
        """True if a violation of this rule must be rejected outright."""
        return self.severity == "hard"

    @classmethod
    def from_dict(cls, data: dict) -> "DNARule":
        return cls(
            id=data["id"],
            constraint=data["constraint"],
            severity=data["severity"],
            category=data.get("category", "general"),
            rationale=data.get("rationale", ""),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "constraint": self.constraint,
            "severity": self.severity,
            "category": self.category,
            "rationale": self.rationale,
        }
