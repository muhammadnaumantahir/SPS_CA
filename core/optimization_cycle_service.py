"""Runtime boundary for threshold-triggered Layer 6 optimization cycles."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from layers.layer_05_experience import ExperienceLog, Task
from layers.layer_06_meta_learning import OptimizationCycleController, OptimizationCyclePlan
from layers.layer_08_evolution import (
    CapabilityGapPlanner,
    EvolutionActionPlan,
    EvolutionEngine,
    EvolutionExecutionAuthority,
    OptimizationActionPlanner,
)


DEFAULT_STATE_PATH = "experience/logs/optimization_cycle_state.json"


class OptimizationCycleService:
    """Assess optimization opportunities and execute only explicitly authorized Evolution work.

    Layer 6 decides whether evidence is sufficient. Layer 8 prepares and owns
    implementation. Automatic execution is default-deny and must be explicitly
    enabled by the deployment environment. Any authorized execution still goes
    through the existing candidate -> test -> Software DNA -> Governance ->
    promotion/rollback pipeline.
    """

    def __init__(
        self,
        *,
        experience: ExperienceLog,
        controller: Optional[OptimizationCycleController] = None,
        gap_planner: Optional[CapabilityGapPlanner] = None,
        action_planner: Optional[OptimizationActionPlanner] = None,
        evolution: Optional[EvolutionEngine] = None,
        execution_authority: Optional[EvolutionExecutionAuthority] = None,
        state_path: str = DEFAULT_STATE_PATH,
    ) -> None:
        self.experience = experience
        self.controller = controller or OptimizationCycleController()
        self.gap_planner = gap_planner or CapabilityGapPlanner()
        self.action_planner = action_planner or OptimizationActionPlanner(gap_planner=self.gap_planner)
        self.evolution = evolution or EvolutionEngine()
        self.execution_authority = execution_authority or EvolutionExecutionAuthority.from_environment()
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
                "execution_authority": self._authority_dict(),
            })
            latest = self.experience.tasks[-1] if self.experience.tasks else None
            if latest is not None and latest.user_request and latest.target_language:
                action = self.prepare_evolution_action(
                    plan,
                    language=latest.target_language,
                    task_description=latest.user_request,
                )
                execution = self.execute_authorized_action_plan(action)
                state = self._load_state()
                state["last_auto_evolution"] = execution
                self._save_state(state)
        return plan

    def prepare_evolution_action(
        self,
        plan: OptimizationCyclePlan,
        *,
        language: str,
        task_description: str,
    ) -> EvolutionActionPlan:
        """Convert a triggered Layer-6 recommendation into one auditable Layer-8 action plan."""
        action = self.action_planner.plan(
            plan,
            task_description=task_description,
            language=language,
        )
        state = self._load_state()
        state.update({
            "last_plan": plan.to_dict(),
            "last_action_plan": action.to_dict(),
            "execution_authority": self._authority_dict(),
        })
        self._save_state(state)
        return action

    def prepare_evolution_candidates(
        self,
        plan: OptimizationCyclePlan,
        *,
        language: str,
        task_description: str,
    ) -> list[dict[str, Any]]:
        """Backward-compatible candidate preparation using the canonical action planner."""
        action = self.prepare_evolution_action(
            plan,
            language=language,
            task_description=task_description,
        )
        candidates = self._candidates_from_action(action)
        state = self._load_state()
        state["evolution_candidates"] = [
            {
                "cycle_id": item["cycle_id"],
                "source_capability_id": item["source_capability_id"],
                "reason": item["reason"],
                "plan": item["plan"].__dict__,
            }
            for item in candidates
        ]
        self._save_state(state)
        return candidates

    def execute_authorized_action_plan(
        self,
        action: EvolutionActionPlan,
        *,
        project_root: str = ".",
    ) -> list[dict[str, Any]]:
        """Execute an action only when explicit authority permits it."""
        candidates = self._candidates_from_action(action)
        allowed, reason = self.execution_authority.authorize(len(candidates))
        state = self._load_state()
        state["execution_authority"] = self._authority_dict()
        state["last_execution_authorization"] = {
            "cycle_id": action.cycle_id,
            "authorized": allowed,
            "reason": reason,
            "candidate_count": len(candidates),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        if not allowed:
            self._save_state(state)
            return [{
                "cycle_id": action.cycle_id,
                "authorized": False,
                "executed": False,
                "reason": reason,
            }]

        results: list[dict[str, Any]] = []
        for candidate in candidates:
            result = self.execute_candidate(candidate, project_root=project_root)
            results.append({
                "cycle_id": candidate["cycle_id"],
                "source_capability_id": candidate["source_capability_id"],
                "authorized": True,
                "executed": True,
                "result": result,
            })
        state = self._load_state()
        state["last_execution_results"] = results[-10:]
        self._save_state(state)
        return results

    def execute_candidate(self, candidate: dict[str, Any], *, project_root: str = ".") -> dict[str, Any]:
        """Execute one explicit Layer-8 candidate through DNA/governance/validation/rollback."""
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
        self._record_evolution_experience(candidate, result)
        return result

    def _record_evolution_experience(self, candidate: dict[str, Any], result: dict[str, Any]) -> None:
        capability_id = str(result.get("capability_id") or candidate.get("source_capability_id") or "evolution")
        successful = bool(result.get("promoted") or result.get("registered"))
        self.experience.add_task(Task(
            id=f"evolution_{candidate.get('cycle_id', 'unknown')}_{capability_id}",
            user_request=f"Controlled Evolution for optimization cycle {candidate.get('cycle_id', 'unknown')}",
            target_project="sps-ca",
            target_language="python",
            status="success" if successful else "failure",
            selected_capability=capability_id,
            outcome=json.dumps(result, default=str, sort_keys=True),
            failure_category=None if successful else "EvolutionExecutionFailure",
            time_taken_seconds=0.0,
        ))
        experience_path = Path("experience/logs/experience_log.json")
        try:
            self.experience.save_to_json(experience_path)
        except OSError:
            pass

    @staticmethod
    def _candidates_from_action(action: EvolutionActionPlan) -> list[dict[str, Any]]:
        if not action.triggered:
            return []
        candidates: list[dict[str, Any]] = []
        for capability_plan, source_id, reason in zip(
            action.capability_plans,
            action.source_capabilities,
            action.rationale,
        ):
            candidates.append({
                "cycle_id": action.cycle_id,
                "source_capability_id": source_id,
                "plan": capability_plan,
                "reason": reason,
            })
        if action.capability_plan is not None:
            candidates.append({
                "cycle_id": action.cycle_id,
                "source_capability_id": "",
                "plan": action.capability_plan,
                "reason": action.reason,
            })
        return candidates

    def _authority_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.execution_authority.enabled,
            "max_actions_per_cycle": self.execution_authority.max_actions_per_cycle,
            "source": self.execution_authority.source,
        }

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
