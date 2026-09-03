"""SPS-CA scenario execution across validation, governance, and execution."""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from capabilities.base import CapabilityContext
from experience.evolution_trace import EvolutionTraceStore
from layers.layer_01_software_dna import SoftwareDNA
from layers.layer_09_validation import Validator
from layers.layer_02_governance import ChangeType, DecisionStatus, GovernanceGate
from layers.capability_registry import CapabilityRegistryManager
from layers.layer_10_execution import Change, ExecutionEngine, ExecutionStatus, FileEdit

from .sps_service import SPSAnalysisResult, SPSScenarioService


class SPSExecutionService:
    """Execute an SPS scenario after analysis, DNA, validation and governance."""

    def __init__(
        self,
        *,
        trace_history_path: str | Path = "experience/traces/evolution_history.json",
        trace_stage_path: str | Path = "experience/traces/stage_state.json",
        registry_path: str = "capabilities/registry.json",
        seeds_dir: str = "capabilities/seeds",
        generated_dir: str = "capabilities/generated",
        evolution_dir: str = "evaluation/evolution",
        workspace_root: str = "data/sps_workspaces",
    ) -> None:
        self.registry_path = registry_path
        self.workspace_root = Path(workspace_root)
        self.repo_root = Path(__file__).resolve().parents[1]
        self.trace_store = EvolutionTraceStore(trace_history_path, trace_stage_path)
        self.dna = SoftwareDNA()
        self.analysis_service = SPSScenarioService(
            trace_history_path=trace_history_path,
            trace_stage_path=trace_stage_path,
            registry_path=registry_path,
            seeds_dir=seeds_dir,
            generated_dir=generated_dir,
            evaluation_dir=evolution_dir,
        )

    def run_submission(
        self,
        *,
        user_request: str,
        code: str,
        language: str,
        file_path: str = "",
        target_project: Optional[str] = None,
    ) -> Dict[str, Any]:
        analysis: SPSAnalysisResult = self.analysis_service.analyze_submission(
            user_request=user_request,
            code=code,
            language=language,
            file_path=file_path,
            project_root=str(self.repo_root),
        )
        scenario_id = analysis.scenario_id
        generation = analysis.capability_generation
        cap_id = analysis.capability_search.get("selected") or generation.get("capability_id")
        if not cap_id:
            return self._fail(scenario_id, "No capability was selected or generated.")

        registry = CapabilityRegistryManager(self.registry_path)
        if generation.get("required"):
            self._canonicalize_generated_registration(generation, registry)
            registry = CapabilityRegistryManager(self.registry_path)
        capability = registry.get_capability(cap_id)
        if capability is None:
            return self._fail(scenario_id, f"Capability {cap_id} is not registered.")

        capability_fn = self._load_capability_fn(capability.entry_point, cap_id, generation)

        workspace, relative_file = self._prepare_workspace(
            scenario_id=scenario_id,
            code=code,
            language=language,
            file_path=file_path,
            target_project=target_project,
        )
        original = (workspace / relative_file).read_text(encoding="utf-8")
        capability_result = capability_fn(
            CapabilityContext(
                code=original,
                language=language.lower(),
                file_path=relative_file,
                project_path=str(workspace),
                metadata={"request": user_request, "scenario_id": scenario_id},
            )
        )
        if not capability_result.success or capability_result.modified_code is None:
            self.trace_store.complete_scenario(
                scenario_id,
                status="modification_failed",
                modification=self._modification_record(cap_id, relative_file, original, original, capability_result),
                result={"success": False, "error": capability_result.error or "Capability produced no modification."},
            )
            return {
                "scenario_id": scenario_id,
                "success": False,
                "capability_id": cap_id,
                "error": capability_result.error or "No modification produced.",
            }

        modified = capability_result.modified_code
        change = Change.new(
            capability_id=cap_id,
            description=user_request,
            edits=[FileEdit(file_path=relative_file, new_content=modified)],
            target_language=language.lower(),
            test_command=self._test_command(language, relative_file),
        )

        validator = Validator(str(workspace))
        validation = validator.run_in_sandbox(modified, change.change_id, relative_file)
        if validation.status.value != "success":
            self.trace_store.complete_scenario(
                scenario_id,
                status="validation_failed",
                modification=self._modification_record(cap_id, relative_file, original, modified, capability_result),
                validation={
                    "status": validation.status.value,
                    "exit_code": getattr(validation, "exit_code", None),
                    "exception": getattr(validation, "exception", None),
                },
                result={"success": False, "error": "Layer 6 rejected the proposed modification."},
            )
            return {
                "scenario_id": scenario_id,
                "success": False,
                "capability_id": cap_id,
                "validation": validation.status.value,
                "modified_code": modified,
            }

        decision = GovernanceGate().make_decision(
            change.change_id,
            self._change_type(generation, user_request),
            user_request,
            [relative_file],
            related_capabilities=[cap_id],
        )
        if decision.decision not in {DecisionStatus.AUTO_APPROVED, DecisionStatus.APPROVED}:
            self.trace_store.complete_scenario(
                scenario_id,
                status="governance_pending",
                modification=self._modification_record(cap_id, relative_file, original, modified, capability_result),
                validation={"status": validation.status.value},
                governance={
                    "decision_id": decision.id,
                    "decision": decision.decision.value,
                    "rationale": decision.rationale,
                },
                result={"success": False, "error": "Layer 7 requires human review before execution."},
            )
            return {
                "scenario_id": scenario_id,
                "success": False,
                "capability_id": cap_id,
                "governance": decision.decision.value,
                "modified_code": modified,
            }

        # Final, independent Layer-1 check immediately before execution. The
        # execution service supplies factual state: governance approved,
        # validation succeeded, sandbox workspace exists, and ExecutionEngine
        # will create a rollback snapshot. No caller-supplied rule IDs are
        # needed to activate the hard DNA constraints.
        dna_result = self.dna.check_action(
            user_request,
            affected_files=[relative_file],
            require_rollback=True,
            validated=True,
            governed=True,
            sandboxed=True,
            explicit_user_request=True,
        )
        self.trace_store.append_event(
            scenario_id,
            "software_dna_final_check",
            {
                "why": "Layer 1 is the final non-bypassable safety boundary before execution.",
                "what": "Re-check the proposed change using actual execution state.",
                "how": "SoftwareDNA independently evaluates the target path and required governance/validation/sandbox/rollback facts.",
                "allowed": dna_result.allowed,
                "checked_rule_ids": dna_result.checked_rule_ids,
                "hard_violations": [r.id for r in dna_result.violated_hard_rules],
                "warnings": dna_result.warnings,
            },
        )
        if not dna_result.allowed:
            error = "Execution blocked by Software DNA: " + "; ".join(r.id for r in dna_result.violated_hard_rules)
            self.trace_store.complete_scenario(
                scenario_id,
                status="dna_blocked",
                modification=self._modification_record(cap_id, relative_file, original, modified, capability_result),
                validation={"status": validation.status.value},
                governance={"decision_id": decision.id, "decision": decision.decision.value, "rationale": decision.rationale},
                result={"success": False, "error": error, "dna": {"checked_rule_ids": dna_result.checked_rule_ids, "warnings": dna_result.warnings}},
            )
            return {
                "scenario_id": scenario_id,
                "success": False,
                "capability_id": cap_id,
                "validation": validation.status.value,
                "governance": decision.decision.value,
                "dna": {"allowed": False, "hard_violations": [r.id for r in dna_result.violated_hard_rules]},
                "modified_code": modified,
                "error": error,
            }

        execution = ExecutionEngine(
            snapshot_dir=str(workspace / ".sps_snapshots"),
            log_path=str(workspace / "execution_log.json"),
            registry=registry,
        ).execute_change(change, str(workspace))

        stage_after = analysis.stage + (1 if generation.get("required") and generation.get("registered") else 0)
        self.trace_store.complete_scenario(
            scenario_id,
            stage_after=stage_after,
            status="completed" if execution.status == ExecutionStatus.SUCCESS else "execution_failed",
            analysis=analysis.analysis,
            capability_search=analysis.capability_search,
            capability_generation=analysis.capability_generation,
            modification=self._modification_record(cap_id, relative_file, original, modified, capability_result),
            validation={
                "status": validation.status.value,
                "metrics_before": getattr(validation.metrics_before, "__dict__", {}),
                "metrics_after": getattr(validation.metrics_after, "__dict__", {}),
            },
            governance={
                "decision_id": decision.id,
                "decision": decision.decision.value,
                "rationale": decision.rationale,
            },
            result={
                "success": execution.status == ExecutionStatus.SUCCESS,
                "status": execution.status.value,
                "change_id": execution.change_id,
                "tests_passing": execution.tests_passing,
                "tests_failing": execution.tests_failing,
                "execution_time_ms": execution.execution_time_ms,
                "rollback_triggered": execution.rollback_triggered,
                "error": execution.error_message,
                "workspace": str(workspace),
                "dna": {
                    "allowed": dna_result.allowed,
                    "checked_rule_ids": dna_result.checked_rule_ids,
                    "warnings": dna_result.warnings,
                },
            },
        )
        return {
            "scenario_id": scenario_id,
            "stage_before": analysis.stage,
            "stage_after": stage_after,
            "success": execution.status == ExecutionStatus.SUCCESS,
            "capability_id": cap_id,
            "generated": bool(generation.get("required")),
            "validation": validation.status.value,
            "governance": decision.decision.value,
            "dna": {"allowed": dna_result.allowed, "checked_rule_ids": dna_result.checked_rule_ids, "warnings": dna_result.warnings},
            "execution": execution.status.value,
            "modified_code": modified,
            "workspace": str(workspace),
        }

    def _canonicalize_generated_registration(self, generation: Dict[str, Any], registry: CapabilityRegistryManager) -> None:
        if not generation.get("required") or not generation.get("capability_id"):
            return
        cap_id = generation["capability_id"]
        module_dir = Path(
            generation.get("module_dir")
            or (self.repo_root / self.analysis_service.gap_planner.generated_dir / generation["capability_id"].lower().replace("-", "_"))
        )
        metadata_path = module_dir / "metadata.json"
        if not metadata_path.exists():
            cwd_module_dir = Path(self.analysis_service.gap_planner.generated_dir) / module_dir.name
            metadata_path = cwd_module_dir / "metadata.json"
            if metadata_path.exists():
                module_dir = cwd_module_dir
        if not metadata_path.exists():
            return
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        module_pkg = module_dir.name
        metadata["entry_point"] = f"{module_pkg}.capability.run"
        parent_str = str(module_dir.parent)
        if parent_str not in sys.path:
            sys.path.insert(0, parent_str)
        if generation.get("test_result", {}).get("coverage_percent") is not None:
            metadata["test_coverage"] = generation["test_result"]["coverage_percent"]
        registered = registry.register_from_dict(metadata)
        generation["registered"] = registered or registry.get_capability(cap_id) is not None

    def _prepare_workspace(self, *, scenario_id: str, code: str, language: str, file_path: str, target_project: Optional[str]) -> tuple[Path, str]:
        if target_project:
            workspace = Path(target_project).expanduser().resolve()
            if not workspace.is_dir():
                raise ValueError(f"Target project does not exist: {target_project}")
            relative_file = file_path or self._default_filename(language)
            target = workspace / relative_file
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text(code, encoding="utf-8")
            return workspace, relative_file

        workspace = self.workspace_root / scenario_id
        workspace.mkdir(parents=True, exist_ok=True)
        relative_file = Path(file_path).name if file_path else self._default_filename(language)
        target = workspace / relative_file
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(code, encoding="utf-8")
        if language.lower() == "python":
            (workspace / "test_sps_submission.py").write_text(
                "from pathlib import Path\n\n"
                f"def test_submitted_source_compiles():\n"
                f"    source = Path({relative_file!r}).read_text(encoding='utf-8')\n"
                f"    compile(source, {relative_file!r}, 'exec')\n",
                encoding="utf-8",
            )
        return workspace, relative_file

    def _load_capability_fn(self, entry_point: str, cap_id: str, generation: Dict[str, Any]):
        module_name, _, function_name = entry_point.rpartition(".")
        try:
            return getattr(importlib.import_module(module_name), function_name)
        except (ModuleNotFoundError, AttributeError):
            pass
        cap_dir_name = cap_id.lower().replace("-", "_")
        for candidate_dir in [
            Path(generation.get("module_dir", "")),
            Path(self.analysis_service.gap_planner.generated_dir) / cap_dir_name,
            Path.cwd() / str(self.analysis_service.gap_planner.generated_dir) / cap_dir_name,
            self.repo_root / str(self.analysis_service.gap_planner.generated_dir) / cap_dir_name,
        ]:
            if not candidate_dir.is_dir():
                continue
            parent_str = str(candidate_dir.parent)
            if parent_str not in sys.path:
                sys.path.insert(0, parent_str)
            try:
                return getattr(importlib.import_module(f"{candidate_dir.name}.capability"), function_name)
            except (ModuleNotFoundError, AttributeError):
                continue
        raise ImportError(f"Cannot load capability module for {cap_id} (entry_point: {entry_point})")

    @staticmethod
    def _default_filename(language: str) -> str:
        return {"python": "submitted.py", "java": "Submitted.java", "javascript": "submitted.js", "typescript": "submitted.ts", "go": "submitted.go", "csharp": "Submitted.cs"}.get(language.lower(), "submitted.txt")

    @staticmethod
    def _test_command(language: str, relative_file: str) -> str:
        return f"python -m py_compile {relative_file!r}" if language.lower() == "python" else "pytest -q"

    @staticmethod
    def _change_type(generation: Dict[str, Any], request: str) -> ChangeType:
        if generation.get("required"):
            return ChangeType.FEATURE_ADDITION
        return ChangeType.LOGIC_FIX if "fix" in request.lower() or "syntax" in request.lower() else ChangeType.FEATURE_ADDITION

    @staticmethod
    def _modification_record(capability_id: str, file_path: str, original: str, modified: str, result: Any) -> Dict[str, Any]:
        return {
            "capability_id": capability_id,
            "file_path": file_path,
            "summary": result.summary,
            "findings": result.findings,
            "original_sha256": hashlib.sha256(original.encode("utf-8")).hexdigest(),
            "modified_sha256": hashlib.sha256(modified.encode("utf-8")).hexdigest(),
            "original_length": len(original),
            "modified_length": len(modified),
            "changed": original != modified,
        }

    def _fail(self, scenario_id: str, error: str) -> Dict[str, Any]:
        self.trace_store.complete_scenario(scenario_id, status="failed", result={"success": False, "error": error})
        return {"scenario_id": scenario_id, "success": False, "error": error}
