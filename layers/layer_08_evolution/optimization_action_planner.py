"""Layer 8 action planning for threshold-triggered optimization cycles.

The planner converts a Layer 6 optimization recommendation into explicit
CapabilityPlan objects. It does not implement, register, execute, or retire
anything; those operations remain behind the existing governed Evolution
pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from layers.layer_06_meta_learning import OptimizationCyclePlan

from .gap_planner import CapabilityGapPlanner
from .models import CapabilityPlan


@dataclass(frozen=True)
class EvolutionActionPlan:
    """Auditable set of Layer 8 actions prepared from one optimization cycle."""

    cycle_id: str
    triggered: bool
    source_capabilities: List[str] = field(default_factory=list)
    capability_plans: List[CapabilityPlan] = field(default_factory=list)
    rationale: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "cycle_id": self.cycle_id,
            "triggered": self.triggered,
            "source_capabilities": list(self.source_capabilities),
            "capability_plans": [plan.__dict__ for plan in self.capability_plans],
            "rationale": list(self.rationale),
        }


class OptimizationActionPlanner:
    """Convert an eligible optimization cycle into governed Evolution actions."""

    def __init__(self, *, gap_planner: CapabilityGapPlanner | None = None) -> None:
        self.gap_planner = gap_planner or CapabilityGapPlanner()

    def plan(
        self,
        optimization_plan: OptimizationCyclePlan,
        *,
        task_description: str,
        language: str,
    ) -> EvolutionActionPlan:
        if not optimization_plan.triggered:
            return EvolutionActionPlan(
                cycle_id=optimization_plan.cycle_id,
                triggered=False,
            )
        if not task_description.strip():
            raise ValueError("task_description must be non-empty")
        if not language.strip():
            raise ValueError("language must be non-empty")

        capability_plans: List[CapabilityPlan] = []
        rationale: List[str] = []
        source_capabilities: List[str] = []
        for evaluation in optimization_plan.candidates:
            source_capabilities.append(evaluation.capability_id)
            reason = (
                f"Optimization cycle {optimization_plan.cycle_id} identified "
                f"{evaluation.capability_id} as underperforming: score="
                f"{evaluation.score:.3f}, observations={evaluation.observations}."
            )
            capability_plans.append(
                self.gap_planner.plan(
                    task_description=task_description,
                    language=language,
                    reason=reason,
                    task_id=optimization_plan.cycle_id,
                )
            )
            rationale.append(reason)

        return EvolutionActionPlan(
            cycle_id=optimization_plan.cycle_id,
            triggered=True,
            source_capabilities=source_capabilities,
            capability_plans=capability_plans,
            rationale=rationale,
        )


__all__ = ["EvolutionActionPlan", "OptimizationActionPlanner"]
