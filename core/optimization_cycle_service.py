"""Runtime boundary for threshold-triggered Layer 6 optimization cycles."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from layers.layer_05_experience import ExperienceLog
from layers.layer_06_meta_learning import OptimizationCycleController, OptimizationCyclePlan


DEFAULT_STATE_PATH = "experience/logs/optimization_cycle_state.json"


class OptimizationCycleService:
    """Assess optimization opportunities after new Experience evidence arrives.

    This service is intentionally a boundary/orchestrator: it records the last
    triggered cycle and returns a plan, but it never edits source or executes
    Evolution automatically.
    """

    def __init__(
        self,
        *,
        experience: ExperienceLog,
        controller: Optional[OptimizationCycleController] = None,
        state_path: str = DEFAULT_STATE_PATH,
    ) -> None:
        self.experience = experience
        self.controller = controller or OptimizationCycleController()
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
            })
        return plan

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
        self.state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


__all__ = ["DEFAULT_STATE_PATH", "OptimizationCycleService"]
