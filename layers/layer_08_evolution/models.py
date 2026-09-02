"""Data models for Layer 8 (Evolution Engine)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class EvolutionTrigger:
    """A repeated failure pattern that has crossed the evolution threshold."""

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
    """Design for a new capability, produced from an evolution trigger or gap."""

    capability_id: str
    name: str
    description: str
    entry_point: str
    supported_languages: List[str] = field(default_factory=lambda: ["python"])
    trigger_pattern: str = ""
    trigger_task_ids: List[str] = field(default_factory=list)
    test_case_names: List[str] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.capability_id:
            raise ValueError("CapabilityPlan.capability_id must be non-empty")
        if not self.entry_point:
            raise ValueError("CapabilityPlan.entry_point must be non-empty")
        if not self.supported_languages:
            raise ValueError("CapabilityPlan.supported_languages must be non-empty")


@dataclass
class GeneratedCapabilityFiles:
    """Concrete artifacts produced for a planned capability."""

    capability_code: str
    tests_code: str
    metadata: Dict[str, Any]
    readme: str


@dataclass
class TestRunResult:
    """Outcome of running a generated capability's own test suite in sandbox."""

    __test__ = False

    passed: bool
    tests_run: int = 0
    tests_failed: int = 0
    coverage_percent: Optional[float] = None
    output: str = ""

    @property
    def meets_coverage_gate(self) -> bool:
        return self.coverage_percent is not None and self.coverage_percent >= 80.0


@dataclass
class EvolutionRecord:
    """Persisted, auditable record of one full evolution cycle."""

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
