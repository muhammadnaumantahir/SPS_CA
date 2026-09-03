"""Runtime boundary for threshold-triggered Layer 6 optimization cycles."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from layers.layer_05_experience import ExperienceLog
from layers.layer_06_meta_learning import OptimizationCycleController, OptimizationCyclePlan
from layers.layer_08_evolution import CapabilityGapPlanner, EvolutionEngine


DEFAULT_STATE_PATH = "experience/logs/optimization_cycle_state.json"


class OptimizationCycleService:
    """Assess optimization opportunities and prepare controlled Evolution work.

    This service is an orchestration boundary. Layer 6 decides when evidence is
    sufficient; Layer 8 remains responsible for capability implementation and
    all Software DNA/Governance/validation gates. No source mutation happens in
    this service merely because a cycle was triggered.
    """

    def __init__(
        self,
        *,
        experience: ExperienceLog,
        controller: Optional[OptimizationCycleController] = None,
        gap_planner: Optional[CapabilityGapPlanner] = None,
        evolution: Optional[EvolutionEngine] = None,
        state_path: str = DEFAULT_STATE_PATH,
    ) -> None:
        self.experience = experience
        self.controller = controller or OptimizationCycleController()
        self.gap_planner = gap_planner or CapabilityGapPlanner()
        self.evolution = evolution or EvolutionEngine()
        self.state_path = Path(state_path)

    def assess_after_task(self, capability_ids: Iterable[str]) -> OptimizationCyclePlan:
        state = self._load_state()
        now = datetime.now(timezone.utc)
        raw_last = state.get("last_cycle_at")
        last_cycle_at = None
        if raw_last:
            try:
                last_cycle_at = datetime.fromisoformat(str(raw_last).replace("Z", "+00:00"))
            except ValueError:
                last_cycle_at = None

        plan = self.controller.assess(
            self.experience,
            capability_ids,
            now=now,
            last_cycle_at=last_cycle_at,
        )
        if plan.triggered:
            self._save_state({
                "last_cycle_at": plan.created_at,
                "last_cycle_id": plan.cycle_id,
                "last_plan": plan.to_dict(),
                "evolution_candidates": [],
            })
        return plan

    def prepare_evolution_candidates(
        self,
        plan: OptimizationCyclePlan,
        *,
        language: str,
        task_description: str,
    ) -> list[dict[str, Any]]:
        """Turn a triggered plan into explicit Layer-8 gap plans without executing them."""
        if not plan.triggered:
            return []

        candidates: list[dict[str, Any]] = []
        for evaluation in plan.candidates:
            reason = (
                f"Optimization cycle {plan.cycle_id}: capability {evaluation.capability_id} "
                f"scored {evaluation.score:.3f} after {evaluation.observations} observations."
            )
            gap_plan = self.gap_planner.plan(
                task_description=task_description,
                language=language,
                reason=reason,
                task_id=plan.cycle_id,
            )
            candidates.append({
                "cycle_id": plan.cycle_id,
                "source_capability_id": evaluation.capability_id,
                "plan": gap_plan,
                "reason": reason,
            })

        state = self._load_state()
        state.update({
            "last_plan": plan.to_dict(),
            "evolution_candidates": [
                {
                    "cycle_id": item["cycle_id"],
                    "source_capability_id": item["source_capability_id"],
                    "reason": item["reason"],
                    "plan": item["plan"].__dict__,
                }
                for item in candidates
            ],
        })
        self._save_state(state)
        return candidates

    def execute_candidate(self, candidate: dict[str, Any], *, project_root: str = ".") -> dict[str, Any]:
        """Execute one already-planned gap through the existing Layer-8 safety pipeline."""
        plan = candidate.get("plan")
        if plan is None:
            raise ValueError("candidate plan is required")
        result = self.evolution.develop_capability_for_gap(plan, project_root=project_root)
        state = self._load_state()
        history = list(state.get("execution_history", []))
        history.append({
            "cycle_id": candidate.get("cycle_id", ""),
            "source_capability_id": candidate.get("source_capability_id", ""),
            "result": result,
        })
        state["execution_history"] = history[-50:]
        self._save_state(state)
        return result

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {}
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state, indent=2, default=str) + "\n", encoding="utf-8")


__all__ = ["DEFAULT_STATE_PATH", "OptimizationCycleService"]
