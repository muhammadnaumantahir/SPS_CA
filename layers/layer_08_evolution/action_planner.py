"""Layer 8 planner that turns optimization evidence into a governed action plan."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from .gap_planner import CapabilityGapPlanner
from .models import CapabilityPlan


@dataclass(frozen=True)
class EvolutionActionPlan:
    """Auditable proposal for the next Layer-8 action.

    This object is advisory. It does not mutate source, approve Governance, or
    execute a capability. The existing controlled Evolution pipeline remains
    responsible for those steps.
    """

    cycle_id: str
    action: str
    reason: str
    task_description: str
    language: str
    capability_ids: List[str] = field(default_factory=list)
    capability_plan: Optional[CapabilityPlan] = None

    def to_dict(self) -> dict:
        return {
            "cycle_id": self.cycle_id,
            "action": self.action,
            "reason": self.reason,
            "task_description": self.task_description,
            "language": self.language,
            "capability_ids": list(self.capability_ids),
            "capability_plan": (
                self.capability_plan.__dict__ if self.capability_plan is not None else None
            ),
        }


class OptimizationActionPlanner:
    """Convert a triggered optimization cycle into one conservative Evolution action."""

    def __init__(self, gap_planner: Optional[CapabilityGapPlanner] = None) -> None:
        self.gap_planner = gap_planner or CapabilityGapPlanner()

    def plan(
        self,
        *,
        cycle_id: str,
        triggered: bool,
        reasons: Iterable[str],
        language: str,
        underperforming_capabilities: Iterable[str] = (),
        failure_rate: float = 0.0,
    ) -> EvolutionActionPlan:
        reason_list = list(reasons)
        capability_ids = list(dict.fromkeys(underperforming_capabilities))
        reason = "; ".join(reason_list) if reason_list else "no_threshold_trigger"

        if not triggered:
            return EvolutionActionPlan(
                cycle_id=cycle_id,
                action="no_action",
                reason=reason,
                task_description="",
                language=language.lower(),
                capability_ids=capability_ids,
            )

        if capability_ids:
            task_description = (
                "Improve or replace underperforming generated capability variants "
                + ", ".join(capability_ids)
            )
            return EvolutionActionPlan(
                cycle_id=cycle_id,
                action="optimize_existing_capability",
                reason=reason,
                task_description=task_description,
                language=language.lower(),
                capability_ids=capability_ids,
            )

        task_description = (
            "Investigate and address the recurring capability gap indicated by "
            f"optimization evidence (aggregate failure rate={failure_rate:.3f})"
        )
        capability_plan = self.gap_planner.plan(
            task_description=task_description,
            language=language,
            reason=reason,
            task_id=cycle_id,
        )
        return EvolutionActionPlan(
            cycle_id=cycle_id,
            action="create_new_capability",
            reason=reason,
            task_description=task_description,
            language=language.lower(),
            capability_ids=[],
            capability_plan=capability_plan,
        )


__all__ = ["EvolutionActionPlan", "OptimizationActionPlanner"]
