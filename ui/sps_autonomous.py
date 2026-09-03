"""Canonical closed-loop SPS executor controlled by the AI Brain."""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from brain import Brain
from brain.ai_evolution import AIEvolutionEngine
from brain.sps_controller import SPSBrainController, SPSDecision
from brain.task_planner import BrainTaskPlanner, BrainTaskPlan
from capabilities.base import CapabilityContext
from layers.capability_registry import CapabilityRegistryManager
from layers.layer_02_governance import ChangeType, DecisionStatus, GovernanceGate
from layers.layer_08_evolution import EvolutionEngine
from layers.layer_09_validation import Validator
from layers.layer_10_execution import Change, ExecutionEngine, ExecutionStatus, FileEdit

from .sps_execution import SPSExecutionService


class AutonomousSPSExecutionService(SPSExecutionService):
    """Observe -> decide -> plan -> execute -> validate -> reflect -> repeat."""

    def run_submission(self, *, user_request: str, code: str, language: str, file_path: str = "", target_project: Optional[str] = None) -> Dict[str, Any]:
        scenario = self.trace_store.start_scenario(user_request=user_request, code=code, language=language, file_path=file_path, metadata={"source": "autonomous_sps_brain"})
        scenario_id = scenario["scenario_id"]
        stage = int(scenario["stage_before"])
        workspace, relative_file = self._prepare_workspace(scenario_id=scenario_id, code=code, language=language, file_path=file_path, target_project=target_project)
        current_code = (workspace / relative_file).read_text(encoding="utf-8")
        controller = SPSBrainController()
        planner = BrainTaskPlanner()
        evolution = EvolutionEngine(
            governance_gate=GovernanceGate(),
            generated_dir=self.analysis_service.evolution.generated_dir,
            seeds_dir=self.analysis_service.evolution.seeds_dir,
            registry_path=self.registry_path,
            evaluation_dir=self.analysis_service.evolution.evaluation_dir,
        )
        ai_evolution = AIEvolutionEngine(evolution)
        observations: list[dict[str, Any]] = []
        task_results: list[dict[str, Any]] = []
        executed_changes: list[dict[str, Any]] = []
        plan: Optional[BrainTaskPlan] = None
        pending: list[Any] = []
        max_iterations = 5

        def registry() -> CapabilityRegistryManager:
            return CapabilityRegistryManager(self.registry_path)

        def capabilities() -> list[dict[str, Any]]:
            return [
                {"id": c.id, "name": c.name, "description": c.description, "status": c.status,
                 "generated": bool(c.generated), "allowed_intents": list(getattr(c, "allowed_intents", []) or []),
                 "forbidden_intents": list(getattr(c, "forbidden_intents", []) or []),
                 "supported_languages": list(getattr(c, "supported_languages", []) or [])}
                for c in registry().list_all_capabilities()
            ]

        def create_capability(request: str) -> dict[str, Any]:
            outcome = ai_evolution.create_from_gap(
                gap=request,
                language=language.lower(),
                scenario_id=scenario_id,
                existing_capabilities=capabilities(),
                observations=observations,
            )
            if not outcome.get("registered"):
                raise RuntimeError(f"Layer 8 failed quality gates for {outcome.get('capability_id', 'new capability')}")
            return outcome

        def make_plan() -> BrainTaskPlan:
            nonlocal max_iterations
            controller_decision = controller.decide(
                goal=user_request, current_code=current_code,
                task_plan=plan.as_dict() if plan else {},
                capabilities=capabilities(), observations=observations,
                iteration=len(observations) + 1,
            )
            max_iterations = max(max_iterations, controller_decision.max_iterations)
            if controller_decision.strategy == "create":
                outcome = create_capability(controller_decision.task_instruction or user_request)
                observations.append({"event": "capability_created", **outcome})
            intent = Brain.infer_intent_class(user_request, current_code, relative_file)
            new_plan = planner.plan(
                request=user_request, code=current_code, language=language.lower(),
                file_path=relative_file, capability_catalog=capabilities(), intent_class=intent,
            )
            observations.append({"event": "strategy", "strategy": controller_decision.strategy, "reason": controller_decision.reason})
            return new_plan

        try:
            plan = make_plan()
            pending = list(plan.tasks)
            while pending and len(task_results) < max_iterations:
                task = pending.pop(0)
                cap_registry = registry()
                capability = cap_registry.get_capability(task.capability_id)
                if capability is None:
                    observation = {"status": "missing_capability", "task_id": task.id, "capability_id": task.capability_id}
                    observations.append(observation)
                    decision = controller.reflect(goal=user_request, decision=SPSDecision("reuse", "missing capability"), observation=observation, current_code=current_code, remaining_tasks=[t.as_dict() for t in pending], iteration=len(task_results) + 1)
                    if decision.strategy == "create":
                        outcome = create_capability(decision.task_instruction or task.instruction)
                        observations.append({"event": "capability_created", **outcome})
                    plan = make_plan(); pending = list(plan.tasks); continue

                dependencies = [r for r in task_results if r.get("task_id") in set(task.depends_on)]
                instruction = task.instruction
                if dependencies:
                    instruction += "\n\nDEPENDENCY TASK OUTPUTS:\n" + json.dumps(dependencies, ensure_ascii=False, default=str)
                result = self._load_capability_fn(capability.entry_point, task.capability_id, {})(
                    CapabilityContext(
                        code=current_code, language=language.lower(), file_path=relative_file, project_path=str(workspace),
                        metadata={"request": instruction, "task_instruction": task.instruction, "task_id": task.id,
                                  "depends_on": list(task.depends_on), "dependency_results": dependencies,
                                  "brain_plan": plan.as_dict()},
                    )
                )
                record: dict[str, Any] = {"task_id": task.id, "intent_class": task.intent_class, "capability_id": task.capability_id,
                    "instruction": task.instruction, "depends_on": list(task.depends_on), "success": result.success,
                    "summary": result.summary, "findings": result.findings}
                if not result.success:
                    record["error"] = result.error or "Capability failed"
                    task_results.append(record)
                    observation = {"status": "capability_failed", **record}
                    observations.append(observation)
                    decision = controller.reflect(goal=user_request, decision=SPSDecision("reuse", "capability failed"), observation=observation,
                        current_code=current_code, remaining_tasks=[t.as_dict() for t in pending], iteration=len(task_results))
                    if len(task_results) >= max_iterations:
                        break
                    if decision.strategy == "create":
                        outcome = create_capability(decision.task_instruction or task.instruction)
                        observations.append({"event": "capability_created", **outcome})
                    plan = make_plan(); pending = list(plan.tasks); continue

                if result.modified_code is not None:
                    change = Change.new(capability_id=task.capability_id, description=task.instruction,
                        edits=[FileEdit(file_path=relative_file, new_content=result.modified_code)],
                        target_language=language.lower(), test_command=self._test_command(language, relative_file))
                    validation = Validator(str(workspace)).run_in_sandbox(result.modified_code, change.change_id, relative_file)
                    record["validation"] = validation.status.value
                    if validation.status.value != "success":
                        task_results.append(record)
                        observation = {"status": "validation_failed", **record}
                        observations.append(observation)
                        decision = controller.reflect(goal=user_request, decision=SPSDecision("reuse", "validation failed"), observation=observation,
                            current_code=current_code, remaining_tasks=[t.as_dict() for t in pending], iteration=len(task_results))
                        if len(task_results) < max_iterations:
                            if decision.strategy == "create":
                                outcome = create_capability(decision.task_instruction or task.instruction)
                                observations.append({"event": "capability_created", **outcome})
                            plan = make_plan(); pending = list(plan.tasks); continue
                        break
                    governance = GovernanceGate().make_decision(change.change_id, self._change_type({}, task.instruction), task.instruction, [relative_file], related_capabilities=[task.capability_id])
                    record["governance"] = governance.decision.value
                    if governance.decision not in {DecisionStatus.AUTO_APPROVED, DecisionStatus.APPROVED}:
                        task_results.append(record); break
                    dna = self.dna.check_action(task.instruction, affected_files=[relative_file], require_rollback=True, validated=True, governed=True, sandboxed=True, explicit_user_request=True)
                    record["dna"] = {"allowed": dna.allowed, "checked_rule_ids": dna.checked_rule_ids, "warnings": dna.warnings}
                    if not dna.allowed:
                        task_results.append(record); break
                    execution = ExecutionEngine(snapshot_dir=str(workspace / ".sps_snapshots"), log_path=str(workspace / "execution_log.json"), registry=cap_registry).execute_change(change, str(workspace))
                    record["execution"] = execution.status.value; record["change_id"] = execution.change_id
                    if execution.status != ExecutionStatus.SUCCESS:
                        record["error"] = execution.error_message or "Execution failed"; task_results.append(record)
                        observations.append({"status": "execution_failed", **record})
                        if len(task_results) < max_iterations:
                            if controller.reflect(goal=user_request, decision=SPSDecision("reuse", "execution failed"), observation=observations[-1], current_code=current_code, remaining_tasks=[t.as_dict() for t in pending], iteration=len(task_results)).strategy == "create":
                                outcome = create_capability(task.instruction); observations.append({"event": "capability_created", **outcome})
                            plan = make_plan(); pending = list(plan.tasks); continue
                        break
                    current_code = result.modified_code
                    executed_changes.append({"task_id": task.id, "capability_id": task.capability_id, "change_id": execution.change_id})
                task_results.append(record)
                observations.append({"status": "completed", **record})
                reflection = controller.reflect(goal=user_request, decision=SPSDecision("reuse", "step completed"), observation=observations[-1], current_code=current_code, remaining_tasks=[t.as_dict() for t in pending], iteration=len(task_results))
                if reflection.strategy == "finish" and not pending:
                    break
                if reflection.strategy == "create" and len(task_results) < max_iterations:
                    outcome = create_capability(reflection.task_instruction or user_request); observations.append({"event": "capability_created", **outcome})
                    plan = make_plan(); pending = list(plan.tasks)
                elif reflection.strategy in {"replan", "adapt", "improve", "compose"} and len(task_results) < max_iterations:
                    plan = make_plan(); pending = list(plan.tasks)

            final_code = current_code
            composition = planner.compose_results(request=user_request, original_code=code, final_code=final_code, task_results=task_results)
            complete = not pending
            self.trace_store.complete_scenario(
                scenario_id, stage_after=stage, status="completed" if complete else "partial",
                analysis={"brain_plan": plan.as_dict() if plan else {}, "observations": observations},
                capability_search={"intent_class": plan.intent_class if plan else Brain.infer_intent_class(user_request, code, file_path), "multi_task": True, "task_count": len(task_results)},
                capability_generation={"required": any(o.get("event") == "capability_created" for o in observations), "multi_task": True},
                modification={"tasks": executed_changes}, result={"success": complete, "iterations": len(task_results), "composition": composition},
            )
            return {"scenario_id": scenario_id, "stage_before": stage, "stage_after": stage, "success": complete,
                    "brain_plan": plan.as_dict() if plan else {}, "task_results": task_results, "task_count": len(task_results),
                    "modified": bool(executed_changes), "modified_code": final_code if executed_changes else None,
                    "final_response": composition, "workspace": str(workspace),
                    "brain": {"provider": controller.provider_name, "closed_loop": True, "iterations": len(task_results), "observations": observations}}
        except Exception as exc:
            self.trace_store.complete_scenario(scenario_id, status="failed", result={"success": False, "error": str(exc), "observations": observations})
            return {"scenario_id": scenario_id, "success": False, "error": str(exc), "observations": observations}


__all__ = ["AutonomousSPSExecutionService"]
