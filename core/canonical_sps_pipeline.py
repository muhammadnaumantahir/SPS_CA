"""Canonical SPS execution pipeline shared by UI and evaluation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from brain import Brain
from layers.architecture import architecture_manifest
from layers.layer_04_knowledge import KnowledgeCore
from layers.layer_05_experience import ExperienceLog, Task
from layers.layer_05_experience.execution_memory import ExecutionExperienceStore
from layers.layer_06_meta_learning import MetaLearner
from layers.layer_07_adaptation import Adaptation
from ui.sps_autonomous import AutonomousSPSExecutionService


class CanonicalSPSPipeline:
    """Run one submission through the canonical autonomous SPS boundary."""

    def __init__(self, *, registry_path: str = "capabilities/registry.json", experience_path: str = "experience/logs/experience_log.json") -> None:
        self.registry_path = registry_path
        self.execution = AutonomousSPSExecutionService(registry_path=registry_path)
        self.brain = Brain()
        self.knowledge = KnowledgeCore()
        self.meta_learning = MetaLearner()
        self.adaptation = Adaptation()
        self.experience_memory = ExecutionExperienceStore(experience_path)

    def run_submission(self, *, user_request: str, code: str, language: str, file_path: str = "", target_project: Optional[str] = None, source: str = "runtime", run_id: str = "", scenario_id: str = "", feedback: str = "") -> Dict[str, Any]:
        language = (language or "python").lower()
        file_path = file_path or self._default_filename(language)
        brain_intent = self.brain.infer_intent_class(user_request, code, file_path)
        experience = self.experience_memory.load()
        failure_patterns = self.meta_learning.analyze_failure_patterns(experience)
        knowledge = self.knowledge.build_snapshot(language=language, file_path=file_path, symbols=(), capabilities=(), facts={"experience_count": len(experience.tasks), "working_source_chars": len(code)})
        knowledge_valid = self.knowledge.validate(knowledge)
        current_task = Task(id="pipeline-current", user_request=user_request, target_project=target_project or "sps_workspace", target_language=language, status="partial")
        reusable_capabilities = []
        for past_task in reversed(experience.tasks[-8:]):
            if self.adaptation.can_reuse_capability(current_task, past_task):
                reusable_capabilities.append(past_task.selected_capability)
        reusable_capabilities = list(dict.fromkeys(reusable_capabilities))
        adaptation_params, adaptation_changes = self.adaptation.adjust_parameters({"language": language, "timeout_seconds": 5.0}, {"target_language": language, "complex": len(code) > 4000})
        adaptation_ok = self.adaptation.test_adaptation(adaptation_params, code)
        historical_context = self.experience_memory.find_relevant(user_request, language=language, limit=12)
        result = self.execution.run_submission(user_request=user_request, code=code, language=language, file_path=file_path, target_project=target_project)

        capability_id = str(result.get("capability_id") or "")
        task_results = result.get("task_results") or []
        if not capability_id and task_results:
            capability_id = str(task_results[0].get("capability_id") or "")
        success = bool(result.get("success"))
        status = "success" if success else "failure"
        error = result.get("error") or next((item.get("error") for item in reversed(task_results) if item.get("error")), None)
        experience_task = self.experience_memory.record_execution(
            request=user_request, language=language, status=status, capability_id=capability_id,
            outcome=str(result.get("final_response") or result.get("execution") or result.get("validation") or status),
            failure_category="execution_failure" if not success else None, source=source,
            scenario_id=scenario_id, run_id=run_id, feedback=feedback, error=str(error) if error else None,
            metadata={"brain_intent": brain_intent, "historical_matches": len(historical_context)},
            target_project=target_project or "sps_workspace",
        )
        result["experience"] = {"record_id": experience_task.id, "source": experience_task.source, "remembered": True, "history_matches_before_execution": len(historical_context), "status": experience_task.status, "capability_id": experience_task.selected_capability, "scenario_id": experience_task.scenario_id, "run_id": experience_task.run_id, "feedback": experience_task.feedback}
        pipeline = self._build_pipeline(result=result, brain_intent=brain_intent, knowledge_valid=knowledge_valid, experience=experience, failure_patterns=failure_patterns, reusable_capabilities=reusable_capabilities, adaptation_changes=adaptation_changes, adaptation_ok=adaptation_ok)
        result["brain"] = {"component": "SPS-CA Brain", "role": "autonomous AI reasoning, task decomposition, strategy selection, reflection, capability orchestration, evolution decisions and result composition", "intent_signal": brain_intent, "replaceable": True, "closed_loop": True, "historical_experience": {"matches": len(historical_context), "successes": sum(item.status == "success" for item in historical_context), "failures": sum(item.status == "failure" for item in historical_context)}}
        result["pipeline"] = pipeline
        return result

    @staticmethod
    def _build_pipeline(*, result: Dict[str, Any], brain_intent: str, knowledge_valid: bool, experience: ExperienceLog, failure_patterns: Dict[str, int], reusable_capabilities: list[str], adaptation_changes: Dict[str, str], adaptation_ok: bool) -> Dict[str, Any]:
        manifest = architecture_manifest(); dna = result.get("dna") or {}; validation = result.get("validation"); execution = result.get("execution")
        generated = bool(result.get("generated")) or any(o.get("event") == "capability_created" for o in (result.get("brain", {}).get("observations") or [])); growth_decision = "create" if generated else "brain_controlled"; growth_reason = "Brain selected runtime strategy; Layer 8 is invoked when the Brain identifies a reusable capability gap."
        def layer(number: int, status: str, component: str, artifact: str, detail: str = "") -> Dict[str, Any]:
            definition = next(item for item in manifest["layers"] if item["number"] == number); return {"number": number, "name": definition["name"], "status": status, "component": component, "artifact": artifact, "detail": detail}
        layers = [
            layer(1, "completed" if dna.get("allowed") is not False else "blocked", "SoftwareDNA", "DNA decision", "Final hard-boundary check uses actual execution state and cannot be overridden by Brain strategy."),
            layer(2, "completed" if result.get("governance") else "evaluated", "GovernanceGate", result.get("governance") or "task-level governance", "Brain can request work, but authorization remains deterministic."),
            layer(3, "completed", "CognitiveCore + Brain", f"intent={brain_intent}", "Brain is the autonomous controller; CognitiveCore supplies structured code/task context."),
            layer(4, "completed" if knowledge_valid else "blocked", "KnowledgeCore", f"experience_count={len(experience.tasks)}", "Structured knowledge is available as Brain context."),
            layer(5, "completed", "ExperienceLog + ExecutionExperienceStore", f"tasks={len(experience.tasks) + 1}", "Durable execution outcomes are recorded for future reasoning."),
            layer(6, "completed", "MetaLearner", f"failure_patterns={len(failure_patterns)}", "Failure evidence is available before replanning."),
            layer(7, "completed", "Adaptation", f"changed={len(adaptation_changes)}; precheck={adaptation_ok}", "Adaptation context is available to the closed loop."),
            layer(8, "completed", "EvolutionEngine + Capability Registry", growth_decision, growth_reason),
            layer(9, "completed" if validation else "evaluated", "Validator", str(validation or "task-level validation"), "Every code-changing task is validated before execution."),
            layer(10, "completed" if execution else "evaluated", "ExecutionEngine", str(execution or "task-level execution"), "Every applied code change uses the controlled execution boundary."),
        ]
        return {"name": "Canonical SPS Autonomous Execution Pipeline", "version": 4, "layers": layers, "brain": {"component": "SPS-CA Brain", "role": "autonomous controller", "replaceable": True, "intent_signal": brain_intent}, "growth_decision": {"decision": growth_decision, "reasoning": growth_reason}, "supporting_subsystems": manifest["supporting_subsystems"]}

    @staticmethod
    def _default_filename(language: str) -> str:
        return {"python": "submitted.py", "java": "Submitted.java", "javascript": "submitted.js", "typescript": "submitted.ts", "go": "submitted.go", "csharp": "Submitted.cs"}.get(language, "submitted.txt")


__all__ = ["CanonicalSPSPipeline"]
