"""Data models for Layer 8 (Evolution Engine).

These mirror the workflow described in Phase 4 of the master document:
a repeated failure pattern (:class:`EvolutionTrigger`) is turned into a
design (:class:`CapabilityPlan`), the design is turned into concrete files
(:class:`GeneratedCapabilityFiles`), the files are exercised by their own
generated test suite (:class:`TestRunResult`), and the whole cycle is
captured for audit as an :class:`EvolutionRecord`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class EvolutionTrigger:
    """A repeated failure pattern that has crossed the evolution threshold.

    Mirrors the Phase 4 example: three or more failures sharing a
    ``failure_category`` (e.g. ``"Parse error"``) justify generating a new
    capability rather than continuing to retry existing ones.

    Attributes:
        pattern: The ``failure_category`` this trigger is built from.
        occurrence_count: How many failed tasks share this category.
        trigger_task_ids: The specific task ids that make up the count, for
            traceability into the GitHub commit message and audit trail.
    """

    pattern: str
    occurrence_count: int
    trigger_task_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.pattern:
            raise ValueError("EvolutionTrigger.pattern must be non-empty")
        if self.occurrence_count < 0:
            raise ValueError("EvolutionTrigger.occurrence_count must be >= 0")


@dataclass
class CapabilityPlan:
    """Design for a new capability, produced from an :class:`EvolutionTrigger`."""

    capability_id: str
    name: str
    description: str
    entry_point: str
    supported_languages: List[str] = field(default_factory=lambda: ["python"])
    trigger_pattern: str = ""
    trigger_task_ids: List[str] = field(default_factory=list)
    test_case_names: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.capability_id:
            raise ValueError("CapabilityPlan.capability_id must be non-empty")
        if not self.entry_point:
            raise ValueError("CapabilityPlan.entry_point must be non-empty")
        if not self.supported_languages:
            raise ValueError("CapabilityPlan.supported_languages must be non-empty")


@dataclass
class GeneratedCapabilityFiles:
    """The concrete artifacts produced for a planned capability.

    Attributes:
        capability_code: Contents of ``capability.py``.
        tests_code: Contents of ``tests.py``.
        metadata: Contents of ``metadata.json`` (as a dict, not yet serialized).
        readme: Contents of ``README.md``.
    """

    capability_code: str
    tests_code: str
    metadata: Dict[str, Any]
    readme: str


@dataclass
class TestRunResult:
    """Outcome of running a generated capability's own test suite in sandbox."""

    # Not a pytest test case -- stop pytest's collector from warning about
    # the "Test" prefix just because this dataclass defines __init__.
    __test__ = False

    passed: bool
    tests_run: int = 0
    tests_failed: int = 0
    coverage_percent: Optional[float] = None
    output: str = ""

    @property
    def meets_coverage_gate(self) -> bool:
        """True only if coverage was actually measured and is >= 80%."""
        return self.coverage_percent is not None and self.coverage_percent >= 80.0


@dataclass
class EvolutionRecord:
    """Persisted, auditable record of one full evolution cycle.

    Written to ``evaluation/evolution/<capability_id>.json`` and the basis
    for the GitHub commit message described in Phase 4 ("Commit message
    format"). ``registered`` is only ``True`` when the capability passed its
    own tests, met the coverage gate, and was not rejected by Governance.
    """

    capability_id: str
    trigger_pattern: str
    trigger_task_ids: List[str]
    test_result: Optional[TestRunResult]
    governance_decision_id: Optional[str]
    registered: bool
    commit_message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "trigger_pattern": self.trigger_pattern,
            "trigger_task_ids": self.trigger_task_ids,
            "test_result": (
                {
                    "passed": self.test_result.passed,
                    "tests_run": self.test_result.tests_run,
                    "tests_failed": self.test_result.tests_failed,
                    "coverage_percent": self.test_result.coverage_percent,
                }
                if self.test_result
                else None
            ),
            "governance_decision_id": self.governance_decision_id,
            "registered": self.registered,
            "commit_message": self.commit_message,
            "timestamp": self.timestamp.isoformat(),
        }
