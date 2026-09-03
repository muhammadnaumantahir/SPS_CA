"""AI-Brain orchestration over the canonical SPS capability execution boundary."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from brain import Brain
from brain.task_planner import BrainTaskPlanner
from capabilities.base import CapabilityContext
from layers.capability_registry import CapabilityRegistryManager
from layers.layer_09_validation import Validator
from layers.layer_02_governance import DecisionStatus, GovernanceGate
from layers.layer_10_execution import Change, ExecutionEngine, ExecutionStatus, FileEdit

from .sps_execution import SPSExecutionService


class BrainOrchestratedExecutionService(SPSExecutionService):
    """Let the AI Brain decompose and orchestrate compound capability workflows."""

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
            metadata={"source": "brain_orchestrated_execution"},
        )
        scenario_id = scenario["scenario_id"]
        stage = int(scenario["stage_before"])
        registry = CapabilityRegistryManager(self.registry_path)
        catalog = [
            {
                "id": cap.id,
                "status": cap.status,
                "generated": bool(cap.generated),
                "allowed_intents": list(getattr(cap, "allowed_intents", []) or []),
                "forbidden_intents": list(getattr(cap, "forbidden_intents", []) or []),
                "supported_languages": list(getattr(cap, "supported_languages", []) or []),
            }
            for cap in registry.list_all_capabilities()
        ]
        intent_class = Brain.infer_intent_class(user_request, code, file_path)

        try:
            planner = BrainTaskPlanner()
            plan = planner.plan(
                request=user_request,
                code=code,
                language=language.lower(),
                file_path=file_path,
                capability_catalog=catalog,
                intent_class=intent_class,
            )
        except Exception as exc:
            self.trace_store.complete_scenario(scenario_id, status="failed", result={"success": False, "error": str(exc)})
            return {"scenario_id": scenario_id, "success": False, "error": str(exc)}

        workspace, relative_file = self._prepare_workspace(
            scenario_id=scenario_id,
            code=code,
            language=language,
            file_path=file_path,
            target_project=target_project,
        )
        current_code = (workspace / relative_file).read_text(encoding="utf-8")
        task_results: list[dict[str, Any]] = []
        executed_changes: list[dict[str, Any]] = []

        for task in plan.tasks:
            capability = registry.get_capability(task.capability_id)
            if capability is None:
                return self._orchestration_fail(scenario_id, task_results, task.id, f"Capability {task.capability_id} is not registered.")
            dependencies = [item for item in task_results if item.get("task_id") in set(task.depends_on)]
            dependency_text = ""
            if dependencies:
                dependency_text = "\n\nDEPENDENCY TASK OUTPUTS (use these as factual context):\n" + json.dumps(dependencies, ensure_ascii=False, default=str)
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
                        "brain_plan": plan.as_dict(),
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
                return self._orchestration_fail(scenario_id, task_results, task.id, result.error or "Capability failed.")

            modified = result.modified_code
            if modified is None:
                task_results.append(task_record)
                continue

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
            task_results.append(task_record)
            if execution.status != ExecutionStatus.SUCCESS:
                return self._orchestration_fail(scenario_id, task_results, task.id, execution.error_message or "Execution failed.")
            current_code = modified
            executed_changes.append({"task_id": task.id, "capability_id": task.capability_id, "change_id": execution.change_id})

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
            status="completed",
            analysis={"brain_task_plan": plan.as_dict()},
            capability_search={
                "selected": plan.tasks[0].capability_id,
                "intent_class": plan.intent_class,
                "multi_task": True,
                "task_count": len(plan.tasks),
            },
            capability_generation={"required": False, "multi_task": True},
            modification={"tasks": executed_changes},
            result={"success": True, "task_count": len(task_results), "composition": composition},
        )
        return {
            "scenario_id": scenario_id,
            "stage_before": stage,
            "stage_after": stage,
            "success": True,
            "brain_plan": plan.as_dict(),
            "task_results": task_results,
            "task_count": len(plan.tasks),
            "modified": bool(executed_changes),
            "modified_code": final_code if executed_changes else None,
            "final_response": composition,
            "workspace": str(workspace),
        }

    def _orchestration_fail(self, scenario_id: str, task_results: list[dict[str, Any]], task_id: str, error: str) -> Dict[str, Any]:
        self.trace_store.complete_scenario(
            scenario_id,
            status="failed",
            result={"success": False, "failed_task_id": task_id, "error": error, "task_results": task_results},
        )
        return {"scenario_id": scenario_id, "success": False, "failed_task_id": task_id, "error": error, "task_results": task_results}
