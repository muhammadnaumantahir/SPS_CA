from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from capabilities.base import CapabilityContext
from capabilities.seed_registry import load_entry_point, load_seed_capabilities
from layers.layer_02_cognitive_core import CognitiveCore
from layers.layer_06_validation import Validator
from layers.layer_07_governance import ChangeType, DecisionStatus, GovernanceGate
from layers.layer_09_capability_registry import CapabilityRegistryManager
from layers.layer_10_execution import Change, ExecutionEngine, ExecutionStatus, FileEdit


HELP_TEXT = """Commands:
  load <project_path>      Load a target project
  show project             Show current project context
  show registry            Show available capabilities
  show experience          Show recent recorded UI interactions
  help                     Show this help
  quit                     Exit SPS-CA

Any other input is treated as a natural-language coding request."""


class SPS_CA_Interface:
    """Prompt-based Phase 7 interface over the existing SPS layer packages.

    The UI is intentionally thin: it owns interaction, presentation and
    session history while delegating reasoning to Layer 2, validation to
    Layer 6, governance to Layer 7, registry lookup to Layer 9, and execution
    to Layer 10.
    """

    def __init__(
        self,
        history_path: str | Path = "ui/session_history.json",
        registry_path: str = "capabilities/registry.json",
    ) -> None:
        self.history_path = Path(history_path)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.core = CognitiveCore()
        self.registry = CapabilityRegistryManager(registry_path)
        self.execution = ExecutionEngine()
        self.project_context: Optional[Dict[str, Any]] = None
        self._history = self._load_history()

    # ------------------------------------------------------------------
    # Interactive session / commands
    # ------------------------------------------------------------------
    def start_interactive_session(self) -> None:
        print("Welcome to SPS-CA (Self-Programming Code Assistant)")
        print("Type 'help' for commands, 'quit' to exit")
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not user_input:
                continue
            response = self.handle_command(user_input)
            if response == "__QUIT__":
                break
            print(f"\nSPS-CA: {response}\n")

    def handle_command(self, user_input: str) -> str:
        command = user_input.strip()
        lowered = command.lower()
        if lowered == "quit":
            self._record_event("quit", command, "Session ended")
            return "__QUIT__"
        if lowered == "help":
            response = HELP_TEXT
            self._record_event("help", command, response)
            return response
        if lowered.startswith("load "):
            response = self.load_project(command[5:].strip())
            self._record_event("load", command, response)
            return response
        if lowered == "show project":
            response = self.show_context("project")
            self._record_event("show", command, response)
            return response
        if lowered == "show registry":
            response = self.show_context("registry")
            self._record_event("show", command, response)
            return response
        if lowered == "show experience":
            response = self.show_context("experience")
            self._record_event("show", command, response)
            return response
        if lowered.startswith("show "):
            response = self.show_context(command[5:].strip())
            self._record_event("show", command, response)
            return response
        response = self.process_request(command)
        self._record_event("request", command, response)
        return response

    # ------------------------------------------------------------------
    # Project context
    # ------------------------------------------------------------------
    def load_project(self, project_path: str) -> str:
        root = Path(project_path).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            return f"Error: project path does not exist or is not a directory: {project_path}"
        analysis = self.core.analyze_target_project(str(root))
        language = analysis.languages_detected[0] if analysis.languages_detected else "unknown"
        self.project_context = {
            "path": str(root),
            "language": language,
            "languages": list(analysis.languages_detected),
            "files": len(analysis.files),
            "functions": analysis.total_functions,
        }
        return (
            f"Loaded project: {root} (language: {language})\n"
            f"  Analyzed files: {len(analysis.files)}\n"
            f"  Functions discovered: {analysis.total_functions}"
        )

    def show_context(self, context_type: str) -> str:
        context_type = context_type.lower().strip()
        if context_type == "project":
            if not self.project_context:
                return "No project loaded. Use: load <project_path>"
            return (
                f"Current project: {self.project_context['path']}\n"
                f"Language: {self.project_context['language']}\n"
                f"Analyzed files: {self.project_context['files']}\n"
                f"Functions discovered: {self.project_context['functions']}"
            )
        if context_type == "registry":
            capabilities = self.registry.list_all_capabilities()
            if not capabilities:
                return "Available capabilities: none"
            lines = ["Available capabilities:"]
            for cap in capabilities:
                lines.append(
                    f"  {cap.id}: {cap.name} [{cap.status}] v{cap.version}"
                )
            return "\n".join(lines)
        if context_type == "experience":
            events = self._history.get("events", [])[-5:]
            if not events:
                return "Recent interactions: none"
            lines = ["Recent interactions:"]
            for event in events:
                lines.append(
                    f"  {event['timestamp']} | {event['kind']} | {event['command']}"
                )
            return "\n".join(lines)
        return "Unknown context. Use: project, registry, experience"

    # ------------------------------------------------------------------
    # Ten-layer-oriented request flow
    # ------------------------------------------------------------------
    def process_request(self, user_request: str) -> str:
        if not self.project_context:
            return "Error: no project loaded. Use: load <project_path>"

        try:
            project_path = self.project_context["path"]
            language = self.project_context["language"]

            # Layer 1: Software DNA boundary is enforced later by Layer 7,
            # while this interface keeps the request/project boundary explicit.
            request = self.core.receive_request(
                user_request,
                target_project=project_path,
                target_language=language,
            )

            # Layer 2: cognitive analysis + candidate capability selection.
            analysis = self.core.analyze_target_project(project_path)
            candidates = self.core.select_candidate_capabilities(
                analysis, user_request=user_request
            )
            plan = self.core.plan_modification_strategy(
                analysis, candidates, self.core.decompose_task(user_request)
            )
            if not plan.selected_capability_ids:
                return "Cognitive Core: no suitable capability found."

            selected = self._resolve_capability(plan.selected_capability_ids)
            if selected is None:
                return "Cognitive Core: selected capability could not be resolved."

            # Layers 3-5: current experience/meta-learning/adaptation state is
            # represented through the existing planning result; no UI-specific
            # learning logic is introduced here.
            capability_fn = load_entry_point(selected)
            target_file, code = self._choose_target_file(project_path, language, user_request)
            if target_file is None:
                return (
                    f"Analysis complete. Capability used: {selected.id}. "
                    "No supported source file was found for this request."
                )

            capability_result = capability_fn(
                CapabilityContext(
                    code=code,
                    language=language,
                    file_path=target_file,
                    project_path=project_path,
                    metadata={"request": user_request},
                )
            )

            if not capability_result.success:
                return f"Capability {selected.id} failed: {capability_result.error}"

            # Analysis-only capability: return findings without modifying user code.
            if capability_result.modified_code is None:
                return self._format_analysis_response(selected.id, capability_result)

            change_type = self._change_type_for_capability(selected.id)
            change = Change.new(
                capability_id=selected.id,
                description=user_request,
                edits=[FileEdit(file_path=target_file, new_content=capability_result.modified_code)],
                target_language=language,
                test_command="pytest -q",
            )

            # Layer 6: validate candidate in an isolated copy.
            validator = Validator(project_path)
            sandbox = validator.run_in_sandbox(
                capability_result.modified_code,
                change.change_id,
                target_file,
            )
            validation_ok = sandbox.status.value == "success"
            if not validation_ok:
                return (
                    f"Validation failed for {selected.id}.\n"
                    f"  Layer 6: {sandbox.status.value}\n"
                    f"  Change: {change.change_id}"
                )

            # Layer 7: governance gate and audit decision.
            governance = GovernanceGate()
            decision = governance.make_decision(
                change.change_id,
                change_type,
                change.description,
                [target_file],
                related_capabilities=[selected.id],
            )
            if decision.decision != DecisionStatus.AUTO_APPROVED:
                return (
                    f"Governance requires review for {selected.id}.\n"
                    f"  Decision: {decision.id}\n"
                    f"  Status: {decision.decision.value}\n"
                    f"  Reason: {decision.rationale}"
                )

            # Layer 8 is represented by generated capabilities entering the
            # registry before execution; normal seed use proceeds without creating
            # a new capability.
            execution = self.execution.execute_change(change, project_path)
            return self.format_response(
                execution,
                capability_id=selected.id,
                coverage=getattr(sandbox.metrics_after, "code_coverage_percent", None),
                validation_status=sandbox.status.value,
                governance_status=decision.decision.value,
            )
        except Exception as exc:  # UI must report failures, not terminate the REPL.
            return f"Error: {exc}"

    # ------------------------------------------------------------------
    # Formatting / helpers
    # ------------------------------------------------------------------
    def format_response(
        self,
        execution_result: Any,
        *,
        capability_id: str,
        coverage: Optional[float],
        validation_status: str,
        governance_status: str,
    ) -> str:
        status = execution_result.status.value
        coverage_text = "not reported" if coverage is None else f"{coverage:.1f}%"
        if status == ExecutionStatus.SUCCESS.value:
            return (
                "✓ Change applied successfully!\n"
                f"  Capability used: {capability_id}\n"
                f"  Validation: {validation_status}\n"
                f"  Governance: {governance_status}\n"
                f"  Tests passing: {execution_result.tests_passing}\n"
                f"  Tests failing: {execution_result.tests_failing}\n"
                f"  Code coverage: {coverage_text}\n"
                f"  Execution time: {execution_result.execution_time_ms}ms"
            )
        return (
            f"✗ Change {status}.\n"
            f"  Capability used: {capability_id}\n"
            f"  Validation: {validation_status}\n"
            f"  Governance: {governance_status}\n"
            f"  Error: {execution_result.error_message or 'unknown error'}"
        )

    def _format_analysis_response(self, capability_id: str, result: Any) -> str:
        lines = [
            f"✓ Analysis completed with {capability_id}.",
            f"  Summary: {result.summary}",
            f"  Findings: {len(result.findings)}",
        ]
        for finding in result.findings[:10]:
            detail = finding.get("detail", finding.get("issue", "finding"))
            lines.append(f"    - {detail}")
        return "\n".join(lines)

    def _resolve_capability(self, capability_id: str):
        for template in load_seed_capabilities():
            if template.id == capability_id:
                return template
        return None

    def _choose_target_file(
        self, project_path: str, language: str, user_request: str
    ) -> tuple[Optional[str], str]:
        suffixes = {
            "python": {".py"},
            "java": {".java"},
            "javascript": {".js", ".jsx"},
            "typescript": {".ts", ".tsx"},
            "go": {".go"},
            "csharp": {".cs"},
        }
        requested = user_request.lower()
        candidates = []
        for path in sorted(Path(project_path).rglob("*")):
            if not path.is_file() or path.suffix not in suffixes.get(language, set()):
                continue
            if any(part in str(path).lower() for part in requested.split() if len(part) > 3):
                candidates.insert(0, path)
            else:
                candidates.append(path)
        if not candidates:
            return None, ""
        target = candidates[0]
        return str(target.relative_to(Path(project_path))).replace("\\", "/"), target.read_text(encoding="utf-8")

    @staticmethod
    def _change_type_for_capability(capability_id: str) -> ChangeType:
        mapping = {
            "CAP-002": ChangeType.SYNTAX_FIX,
            "CAP-003": ChangeType.TEST_GENERATION,
            "CAP-004": ChangeType.REFACTORING,
            "CAP-005": ChangeType.LOGIC_FIX,
            "CAP-006": ChangeType.REFACTORING,
            "CAP-007": ChangeType.REFACTORING,
            "CAP-008": ChangeType.FEATURE_ADDITION,
            "CAP-009": ChangeType.LOGIC_FIX,
        }
        return mapping.get(capability_id, ChangeType.LOGIC_FIX)

    def _load_history(self) -> Dict[str, Any]:
        if not self.history_path.exists():
            return {"version": "1.0.0", "events": []}
        try:
            data = json.loads(self.history_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {"version": "1.0.0", "events": []}
        except json.JSONDecodeError:
            return {"version": "1.0.0", "events": []}

    def _record_event(self, kind: str, command: str, response: str) -> None:
        self._history.setdefault("events", []).append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "kind": kind,
                "command": command,
                "response": response,
            }
        )
        self.history_path.write_text(
            json.dumps(self._history, indent=2), encoding="utf-8"
        )


def main() -> None:
    interface = SPS_CA_Interface()
    interface.start_interactive_session()


if __name__ == "__main__":
    main()
