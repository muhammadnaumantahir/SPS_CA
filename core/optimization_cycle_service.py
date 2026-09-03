"""Runtime boundary for threshold-triggered Layer 6 optimization cycles."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from layers.layer_05_experience import ExperienceLog
from layers.layer_05_experience.long_term_learning import LongTermLearningStore
from layers.layer_06_meta_learning import OptimizationCycleController, OptimizationCyclePlan
from layers.layer_08_evolution import (
    CapabilityGapPlanner,
    EvolutionActionPlan,
    EvolutionCycleOutcome,
    EvolutionEngine,
    EvolutionExecutionAuthority,
    OptimizationActionPlanner,
)
from layers.layer_08_evolution.evolution_transaction import EvolutionTransaction, EvolutionTransactionError

DEFAULT_STATE_PATH = "experience/logs/optimization_cycle_state.json"
DEFAULT_LONG_TERM_PATH = "experience/logs/long_term_learning.json"


class OptimizationCycleService:
    """Assess evidence, persist long-term learning, and execute controlled Evolution."""

    def __init__(self, *, experience: ExperienceLog, controller: Optional[OptimizationCycleController] = None, gap_planner: Optional[CapabilityGapPlanner] = None, action_planner: Optional[OptimizationActionPlanner] = None, evolution: Optional[EvolutionEngine] = None, execution_authority: Optional[EvolutionExecutionAuthority] = None, state_path: str = DEFAULT_STATE_PATH, long_term_path: str = DEFAULT_LONG_TERM_PATH) -> None:
        self.experience = experience
        self.controller = controller or OptimizationCycleController()
        self.gap_planner = gap_planner or CapabilityGapPlanner()
        self.action_planner = action_planner or OptimizationActionPlanner(gap_planner=self.gap_planner)
        self.evolution = evolution or EvolutionEngine()
        self.execution_authority = execution_authority or EvolutionExecutionAuthority.from_environment()
        self.state_path = Path(state_path)
        self.long_term = LongTermLearningStore(long_term_path)

    def assess_after_task(self, capability_ids: Iterable[str]) -> OptimizationCyclePlan:
        learning = self.long_term.rebuild(self.experience)
        state = self._load_state()
        state["long_term_learning"] = {"path": str(self.long_term.path), "updated_at": learning.get("updated_at"), "total_tasks": learning.get("total_tasks", 0), "overall_success_rate": learning.get("overall_success_rate", 0.0), "failure_patterns": learning.get("failure_patterns", {})}
        self._save_state(state)
        now = datetime.now(timezone.utc)
        raw_last = state.get("last_cycle_at")
        last_cycle_at = None
        if raw_last:
            try:
                last_cycle_at = datetime.fromisoformat(str(raw_last).replace("Z", "+00:00"))
            except ValueError:
                last_cycle_at = None
        plan = self.controller.assess(self.experience, capability_ids, now=now, last_cycle_at=last_cycle_at)
        if plan.triggered:
            self._save_state({**state, "last_cycle_at": plan.created_at, "last_cycle_id": plan.cycle_id, "last_plan": plan.to_dict(), "evolution_candidates": [], "execution_authority": self._authority_dict()})
            latest = self.experience.tasks[-1] if self.experience.tasks else None
            if latest is not None and latest.user_request and latest.target_language:
                action = self.prepare_evolution_action(plan, language=latest.target_language, task_description=latest.user_request)
                execution = self.execute_authorized_action_plan(action)
                state = self._load_state(); state["last_auto_evolution"] = execution; self._save_state(state)
        return plan

    def prepare_evolution_action(self, plan: OptimizationCyclePlan, *, language: str, task_description: str) -> EvolutionActionPlan:
        action = self.action_planner.plan(plan, task_description=task_description, language=language)
        state = self._load_state(); state.update({"last_plan": plan.to_dict(), "last_action_plan": action.to_dict(), "execution_authority": self._authority_dict()}); self._save_state(state)
        return action

    def prepare_evolution_candidates(self, plan: OptimizationCyclePlan, *, language: str, task_description: str) -> list[dict[str, Any]]:
        action = self.prepare_evolution_action(plan, language=language, task_description=task_description)
        candidates = self._candidates_from_action(action)
        state = self._load_state(); state["evolution_candidates"] = [{"cycle_id": item["cycle_id"], "source_capability_id": item["source_capability_id"], "reason": item["reason"], "plan": item["plan"].__dict__} for item in candidates]; self._save_state(state)
        return candidates

    def execute_authorized_action_plan(self, action: EvolutionActionPlan, *, project_root: str = ".") -> list[dict[str, Any]]:
        candidates = self._candidates_from_action(action)
        allowed, reason = self.execution_authority.authorize(len(candidates))
        state = self._load_state(); state["execution_authority"] = self._authority_dict(); state["last_execution_authorization"] = {"cycle_id": action.cycle_id, "authorized": allowed, "reason": reason, "candidate_count": len(candidates), "recorded_at": datetime.now(timezone.utc).isoformat()}
        if not allowed:
            outcomes = [EvolutionCycleOutcome(cycle_id=action.cycle_id, capability_id=str(item["plan"].capability_id), source_capability_id=item.get("source_capability_id", ""), authorized=False, executed=False, result={"reason": reason}).to_dict() for item in candidates]
            state["last_execution_results"] = outcomes; self._save_state(state)
            return [{"cycle_id": action.cycle_id, "authorized": False, "executed": False, "reason": reason}]
        results = []
        for candidate in candidates:
            result = self.execute_candidate(candidate, project_root=project_root)
            outcome = EvolutionCycleOutcome(cycle_id=candidate["cycle_id"], capability_id=str(result.get("capability_id") or candidate["plan"].capability_id), source_capability_id=candidate.get("source_capability_id", ""), authorized=True, executed=True, promoted=bool(result.get("promoted")), rolled_back=bool(result.get("rolled_back")), result=result)
            results.append({"cycle_id": candidate["cycle_id"], "source_capability_id": candidate["source_capability_id"], "authorized": True, "executed": True, "result": result, "evolution_outcome": outcome.to_dict()})
        state = self._load_state(); state["last_execution_results"] = results[-10:]; self._save_state(state)
        return results

    def execute_candidate(self, candidate: dict[str, Any], *, project_root: str = ".") -> dict[str, Any]:
        plan = candidate.get("plan")
        if plan is None: raise ValueError("candidate plan is required")
        module_name = str(plan.capability_id).lower().replace("-", "_")
        transaction = EvolutionTransaction(project_root, transaction_id=str(candidate.get("cycle_id") or plan.capability_id), registry_path="capabilities/registry.json")
        try:
            transaction.begin(["capabilities/registry.json", f"capabilities/generated/{module_name}"])
            result = self.evolution.develop_capability_for_gap(plan, project_root=project_root)
            if result.get("promoted"): transaction.commit()
            else: transaction.rollback()
        except Exception:
            try: transaction.rollback()
            except EvolutionTransactionError: pass
            raise
        state = self._load_state(); history = list(state.get("execution_history", [])); history.append({"cycle_id": candidate.get("cycle_id", ""), "source_capability_id": candidate.get("source_capability_id", ""), "result": result}); state["execution_history"] = history[-50:]; self._save_state(state)
        return result

    @staticmethod
    def _candidates_from_action(action: EvolutionActionPlan) -> list[dict[str, Any]]:
        if not action.triggered: return []
        return [{"cycle_id": action.cycle_id, "source_capability_id": action.source_capabilities[index], "plan": capability_plan, "reason": action.rationale[index]} for index, capability_plan in enumerate(action.capability_plans)]

    def _authority_dict(self) -> dict[str, Any]:
        return {"enabled": self.execution_authority.enabled, "max_actions_per_cycle": self.execution_authority.max_actions_per_cycle, "source": self.execution_authority.source}

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists(): return {}
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8")); return data if isinstance(data, dict) else {}
        except (OSError, ValueError): return {}

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.state_path.with_suffix(self.state_path.suffix + ".tmp"); tmp.write_text(json.dumps(state, indent=2, default=str) + "\n", encoding="utf-8"); tmp.replace(self.state_path)


__all__ = ["DEFAULT_STATE_PATH", "DEFAULT_LONG_TERM_PATH", "OptimizationCycleService"]
