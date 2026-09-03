"""Closed-loop SPS execution controlled by the AI Brain."""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from brain import Brain
from brain.sps_controller import SPSBrainController, SPSDecision
from brain.task_planner import BrainTaskPlan, BrainTaskPlanner
from capabilities.base import CapabilityContext
from layers.capability_registry import CapabilityRegistryManager
from layers.layer_02_governance import DecisionStatus, GovernanceGate, ChangeType
from layers.layer_08_evolution import EvolutionEngine
from layers.layer_09_validation import Validator
from layers.layer_10_execution import Change, ExecutionEngine, ExecutionStatus, FileEdit

from .sps_execution import SPSExecutionService


class BrainOrchestratedExecutionService(SPSExecutionService):
    """Run SPS as an observe -> decide -> act -> validate -> reflect loop."""

    def run_submission(
        self,
        *,
        user_request: str,
        code: str,
        language: str,
        file_path: str = "",
        target_project: Optional[str] = None,
    ) -> Dict[str, Any]:
        scenario = self.trace_store.start_scenario(
            user_request=user_request,
            code=code,
            language=language,
            file_path=file_path,
            metadata={"source": "brain_closed_loop"},
        )
        scenario_id = scenario["scenario_id"]
        stage = int(scenario["stage_before"])
        workspace, relative_file = self._prepare_workspace(
            scenario_id=scenario_id,
            code=code,
            language=language,
            file_path=file_path,
            target_project=target_project,
        )
        current_code = (workspace / relative_file).read_text(encoding="utf-8")
        registry = CapabilityRegistryManager(self.registry_path)
        controller = SPSBrainController()
        planner = BrainTaskPlanner()
        evolution = EvolutionEngine(
            governance_gate=GovernanceGate(),
            generated_dir=self.analysis_service.gap_planner.generated_dir,
            seeds_dir=self.analysis_service.gap_planner.seeds_dir,
            registry_path=self.registry_path,
            evaluation_dir=self.analysis_service.evolution.evaluation_dir,
        )
        observations: list[dict[str, Any]] = []
        task_results: list[dict[str, Any]] = []
        executed_changes: list[dict[str, Any]] = []
        current_plan: Optional[BrainTaskPlan] = None
        iterations = 0
        max_iterations = 5

        def catalog() -> list[dict[str, Any]]:
            return [
                {
                    "id": cap.id,
                    "name": getattr(cap, "name", ""),
                    "status": cap.status,
                    "description": getattr(cap, "description", ""),
                    "generated": bool(cap.generated),
                    "allowed_intents": list(getattr(cap, "allowed_intents", []) or []),
                    "forbidden_intents": list(getattr(cap, "forbidden_intents", []) or []),
                    "supported_languages": list(getattr(cap, "supported_languages", []) or []),
                }
                for cap in registry.list_all_capabilities()
            ]

        def make_plan() -> BrainTaskPlan:
            nonlocal max_iterations
            intent = Brain.infer_intent_class(user_request, current_code, relative_file)
            decision = controller.decide(
                goal=user_request,
                current_code=current_code,
                task_plan=current_plan.as_dict() if current_plan else {},
                capabilities=catalog(),
                observations=observations,
                iteration=iterations,
            )
            max_iterations = max(max_iterations, decision.max_iterations)
            if decision.strategy == "create":
                self._create_capability_for_gap(
                    evolution=evolution,
                    registry=registry,
                    request=decision.task_instruction or user_request,
                    language=language,
                    scenario_id=scenario_id,
                )
            refreshed = catalog()
            plan = planner.plan(
                request=user_request,
                code=current_code,
                language=language.lower(),
                file_path=relative_file,
                capability_catalog=refreshed,
                intent_class=intent,
            )
            observations.append({"event": "brain_decision", "strategy": decision.strategy, "reason": decision.reason, "task_instruction": decision.task_instruction})
            return plan

        try:
            current_plan = make_plan()
        except Exception as exc:
            self.trace_store.complete_scenario(scenario_id, status="failed", result={"success": False, "error": str(exc)})
            return {"scenario_id": scenario_id, "success": False, "error": str(exc)}

        pending = list(current_plan.tasks)
        while iterations < max_iterations and pending:
            iterations += 1
            task = pending.pop(0)
            registry = CapabilityRegistryManager(self.registry_path)
            capability = registry.get_capability(task.capability_id)
            if capability is None:
                failure = {"task_id": task.id, "status": "missing_capability", "capability_id": task.capability_id}
                observations.append(failure)
                decision = controller.reflect(
                    goal=user_request, decision=SPSDecision("reuse", "missing capability"), observation=failure,
                    current_code=current_code, remaining_tasks=[item.as_dict() for item in pending], iteration=iterations,
                )
                if decision.strategy == "create":
                    self._create_capability_for_gap(evolution, registry, decision.task_instruction or task.instruction, language, scenario_id)
                    current_plan = make_plan()
                    pending = list(current_plan.tasks)
                    continue
                return self._orchestration_fail(scenario_id, task_results, task.id, f"Capability {task.capability_id} is not registered.")

            dependencies = [item for item in task_results if item.get("task_id") in set(task.depends_on)]
            dependency_text = ""
            if dependencies:
                dependency_text = "\n\nDEPENDENCY TASK OUTPUTS (use as factual evidence; do not invent findings):\n" + json.dumps(dependencies, ensure_ascii=False, default=str)
            instruction = task.instruction + dependency_text
            capability_fn = self._load_capability_fn(capability.entry_point, task.capability_id, {})
            result = capability_fn(
                CapabilityContext(
                    code=current_code,
                    language=language.lower(),
                    file_path=relative_file,
                    project_path=str(workspace),
                    metadata={
                        "request": instruction,
                        "task_instruction": task.instruction,
                        "scenario_id": scenario_id,
                        "task_id": task.id,
                        "depends_on": list(task.depends_on),
                        "dependency_results": dependencies,
                        "brain_plan": current_plan.as_dict(),
                    },
                )
            )
            task_record: dict[str, Any] = {
                "task_id": task.id,
                "instruction": task.instruction,
                "intent_class": task.intent_class,
                "capability_id": task.capability_id,
                "depends_on": list(task.depends_on),
                "success": result.success,
                "summary": result.summary,
                "findings": result.findings,
            }
            if not result.success:
                task_record["error"] = result.error or "Capability failed."
                task_results.append(task_record)
                observation = {"status": "failed", **task_record}
                observations.append(observation)
                decision = controller.reflect(
                    goal=user_request, decision=SPSDecision("reuse", "capability failed"), observation=observation,
                    current_code=current_code, remaining_tasks=[item.as_dict() for item in pending], iteration=iterations,
                )
                if decision.strategy in {"replan", "adapt", "improve", "compose", "create", "reuse"} and iterations < max_iterations:
                    if decision.strategy == "create":
                        self._create_capability_for_gap(evolution, registry, decision.task_instruction or task.instruction, language, scenario_id)
                    current_plan = make_plan()
                    pending = list(current_plan.tasks)
                    continue
                return self._orchestration_fail(scenario_id, task_results, task.id, result.error or "Capability failed.")

            modified = result.modified_code
            if modified is not None:
                change = Change.new(
                    capability_id=task.capability_id,
                    description=task.instruction,
                    edits=[FileEdit(file_path=relative_file, new_content=modified)],
                    target_language=language.lower(),
                    test_command=self._test_command(language, relative_file),
                )
                validation = Validator(str(workspace)).run_in_sandbox(modified, change.change_id, relative_file)
                task_record["validation"] = validation.status.value
                if validation.status.value != "success":
                    task_results.append(task_record)
                    observation = {"status": "validation_failed", **task_record}
                    observations.append(observation)
                    decision = controller.reflect(
                        goal=user_request, decision=SPSDecision("reuse", "validation failed"), observation=observation,
                        current_code=current_code, remaining_tasks=[item.as_dict() for item in pending], iteration=iterations,
                    )
                    if decision.strategy == "create" and iterations < max_iterations:
                        self._create_capability_for_gap(evolution, registry, decision.task_instruction or task.instruction, language, scenario_id)
                        current_plan = make_plan()
                        pending = list(current_plan.tasks)
                        continue
                    if iterations < max_iterations:
                        current_plan = make_plan()
                        pending = list(current_plan.tasks)
                        continue
                    return self._orchestration_fail(scenario_id, task_results, task.id, "Layer 6 rejected the proposed modification.")

                decision = GovernanceGate().make_decision(
                    change.change_id,
                    self._change_type({}, task.instruction),
                    task.instruction,
                    [relative_file],
                    related_capabilities=[task.capability_id],
                )
                task_record["governance"] = decision.decision.value
                if decision.decision not in {DecisionStatus.AUTO_APPROVED, DecisionStatus.APPROVED}:
                    task_results.append(task_record)
                    return self._orchestration_fail(scenario_id, task_results, task.id, "Layer 7 requires human review before execution.")

                dna_result = self.dna.check_action(
                    task.instruction,
                    affected_files=[relative_file],
                    require_rollback=True,
                    validated=True,
                    governed=True,
                    sandboxed=True,
                    explicit_user_request=True,
                )
                task_record["dna"] = {"allowed": dna_result.allowed, "checked_rule_ids": dna_result.checked_rule_ids, "warnings": dna_result.warnings}
                if not dna_result.allowed:
                    task_results.append(task_record)
                    return self._orchestration_fail(scenario_id, task_results, task.id, "Execution blocked by Software DNA.")

                execution = ExecutionEngine(
                    snapshot_dir=str(workspace / ".sps_snapshots"),
                    log_path=str(workspace / "execution_log.json"),
                    registry=registry,
                ).execute_change(change, str(workspace))
                task_record["execution"] = execution.status.value
                task_record["change_id"] = execution.change_id
                if execution.status != ExecutionStatus.SUCCESS:
                    task_results.append(task_record)
                    observation = {"status": "execution_failed", **task_record, "error": execution.error_message}
                    observations.append(observation)
                    decision = controller.reflect(
                        goal=user_request, decision=SPSDecision("reuse", "execution failed"), observation=observation,
                        current_code=current_code, remaining_tasks=[item.as_dict() for item in pending], iteration=iterations,
                    )
                    if iterations < max_iterations:
                        if decision.strategy == "create":
                            self._create_capability_for_gap(evolution, registry, decision.task_instruction or task.instruction, language, scenario_id)
                        current_plan = make_plan()
                        pending = list(current_plan.tasks)
                        continue
                    return self._orchestration_fail(scenario_id, task_results, task.id, execution.error_message or "Execution failed.")

                current_code = modified
                executed_changes.append({"task_id": task.id, "capability_id": task.capability_id, "change_id": execution.change_id})
            task_results.append(task_record)
            observation = {"status": "completed", **task_record}
            observations.append(observation)
            decision = controller.reflect(
                goal=user_request, decision=SPSDecision("reuse", "task completed"), observation=observation,
                current_code=current_code, remaining_tasks=[item.as_dict() for item in pending], iteration=iterations,
            )
            if decision.strategy == "finish" and not pending:
                break
            if decision.strategy == "create" and iterations < max_iterations:
                self._create_capability_for_gap(evolution, registry, decision.task_instruction or user_request, language, scenario_id)
                current_plan = make_plan()
                pending = list(current_plan.tasks)
            elif decision.strategy in {"replan", "adapt", "improve", "compose"} and iterations < max_iterations:
                current_plan = make_plan()
                pending = list(current_plan.tasks)

        final_code = current_code
        composition = planner.compose_results(
            request=user_request,
            original_code=code,
            final_code=final_code,
            task_results=task_results,
        )
        self.trace_store.complete_scenario(
            scenario_id,
            stage_after=stage,
            status="completed" if pending == [] or iterations >= max_iterations else "partial",
            analysis={"brain_task_plan": current_plan.as_dict() if current_plan else {}, "brain_observations": observations},
            capability_search={"intent_class": current_plan.intent_class if current_plan else Brain.infer_intent_class(user_request, code, file_path), "multi_task": True, "task_count": len(task_results)},
            capability_generation={"required": any(o.get("strategy") == "create" for o in observations), "multi_task": True},
            modification={"tasks": executed_changes},
            result={"success": True, "task_count": len(task_results), "iterations": iterations, "composition": composition},
        )
        return {
            "scenario_id": scenario_id,
            "stage_before": stage,
            "stage_after": stage,
            "success": True,
            "brain": {
                "controller": "SPSBrainController",
                "provider": controller.provider_name,
                "closed_loop": True,
                "iterations": iterations,
                "observations": observations,
            },
            "brain_plan": current_plan.as_dict() if current_plan else {},
            "task_results": task_results,
            "task_count": len(task_results),
            "modified": bool(executed_changes),
            "modified_code": final_code if executed_changes else None,
            "final_response": composition,
            "workspace": str(workspace),
        }

    def _create_capability_for_gap(self, evolution: EvolutionEngine, registry: CapabilityRegistryManager, request: str, language: str, scenario_id: str) -> None:
        plan = evolution.plan_capability_for_gap(
            task_description=request,
            language=language.lower(),
            reason="The AI Brain identified that the current capability set or strategy was insufficient for the goal.",
            task_id=scenario_id,
        )
        decision = GovernanceGate().make_decision(
            change_id=f"evolution_{plan.capability_id}",
            change_type=ChangeType.EVOLUTION,
            change_description=plan.description,
            affected_files=[
                str(evolution.generated_dir / plan.capability_id.lower().replace("-", "_") / name)
                for name in ("capability.py", "tests.py", "metadata.json")
            ],
            related_capabilities=[plan.capability_id],
        )
        if decision.decision not in {DecisionStatus.AUTO_APPROVED, DecisionStatus.APPROVED}:
            raise RuntimeError("Layer 7 rejected Brain-requested capability evolution.")
        result = evolution.develop_capability_for_gap(plan, project_root=str(self.repo_root), governance_decision_status=decision.decision)
        if not result.get("registered"):
            raise RuntimeError(f"Layer 8 created {plan.capability_id} but its quality gates did not register it.")
        registry._load()

    def _orchestration_fail(self, scenario_id: str, task_results: list[dict[str, Any]], task_id: str, error: str) -> Dict[str, Any]:
        self.trace_store.complete_scenario(
            scenario_id,
            status="failed",
            result={"success": False, "failed_task_id": task_id, "error": error, "task_results": task_results},
        )
        return {"scenario_id": scenario_id, "success": False, "failed_task_id": task_id, "error": error, "task_results": task_results}
