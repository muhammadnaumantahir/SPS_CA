from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from capabilities.base import CapabilityContext  # noqa: E402
from capabilities.seed_registry import load_entry_point, load_seed_capabilities  # noqa: E402
from layers.layer_02_cognitive_core import CognitiveCore  # noqa: E402
from layers.layer_06_validation import Validator  # noqa: E402
from layers.layer_07_governance import ChangeType, DecisionStatus, GovernanceGate  # noqa: E402
from layers.layer_09_capability_registry import CapabilityRegistryManager  # noqa: E402
from layers.layer_10_execution import Change, ExecutionEngine, ExecutionStatus, FileEdit  # noqa: E402

HELP_TEXT = """Commands:
  load <project_path>      Load a target project
  show project             Show current project context
  show registry            Show available capabilities
  show experience          Show recent recorded UI interactions
  help                     Show this help
  quit                     Exit SPS-CA

Any other input is treated as a natural-language coding request."""


class SPS_CA_Interface:
    """Prompt interface with a strict CAP-001 -> capability pipeline.

    CAP-001 is always the first capability. It uses Ollama as the reasoning
    brain and returns an allowlisted, ordered capability plan. The UI then
    executes that plan sequentially; it never hard-codes intent selection.
    """

    def __init__(
        self,
        history_path: str | Path = "ui/session_history.json",
        registry_path: str = "capabilities/registry.json",
        llm_provider: Optional[Any] = None,
        llm_model: str = "",
    ) -> None:
        self.history_path = Path(history_path)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.core = CognitiveCore()
        self.registry = CapabilityRegistryManager(registry_path)
        self.execution = ExecutionEngine()
        self.project_context: Optional[Dict[str, Any]] = None
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self._history = self._load_history()

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
        if lowered.startswith("show "):
            response = self.show_context(command[5:].strip())
            self._record_event("show", command, response)
            return response
        response = self.process_request(command)
        self._record_event("request", command, response)
        return response

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
            return "\n".join(
                ["Available capabilities:"]
                + [f"  {cap.id}: {cap.name} [{cap.status}] v{cap.version}" for cap in capabilities]
            )
        if context_type == "experience":
            events = self._history.get("events", [])[-5:]
            if not events:
                return "Recent interactions: none"
            return "\n".join(
                ["Recent interactions:"]
                + [f"  {event['timestamp']} | {event['kind']} | {event['command']}" for event in events]
            )
        return "Unknown context. Use: project, registry, experience"

    def process_request(self, user_request: str) -> str:
        if not self.project_context:
            return "Error: no project loaded. Use: load <project_path>"

        try:
            project_path = self.project_context["path"]
            language = self.project_context["language"]
            analysis = self.core.analyze_target_project(project_path)

            # CAP-001 is the mandatory first stage. Ollama is the brain.
            templates = self.registry.list_all_capabilities()
            catalog = [
                {
                    "id": cap.id,
                    "name": cap.name,
                    "description": cap.description,
                    "tags": getattr(cap, "tags", []) or [],
                }
                for cap in templates
                if cap.id != "CAP-001" and cap.status == "active"
            ]
            prompt_template = self._resolve_template("CAP-001")
            if prompt_template is None:
                return "Pipeline error: CAP-001 Prompt Processing is not registered."

            target_file, code = self._choose_target_file(project_path, language, user_request)
            if target_file is None:
                return "Pipeline error: no supported source file was found."

            prompt_result = load_entry_point(prompt_template)(
                CapabilityContext(
                    code=code,
                    language=language,
                    file_path=target_file,
                    project_path=project_path,
                    parameters={
                        "capability_catalog": catalog,
                        "llm_provider": self.llm_provider,
                        "llm_model": self.llm_model,
                        "llm_timeout_seconds": 120.0,
                    },
                    metadata={"request": user_request},
                )
            )
            if not prompt_result.success:
                return "✗ CAP-001 Prompt Processing failed.\n  Brain: Ollama\n  Error: " + str(prompt_result.error)

            brain_plan = prompt_result.findings[0] if prompt_result.findings else {}
            steps = brain_plan.get("steps", [])
            intent = brain_plan.get("intent", "")
            stage_lines = [
                "Pipeline:",
                "  CAP-001 Prompt Processing → Ollama brain ✓",
            ]
            if not steps:
                stage_lines.append(f"  Result: no downstream capability selected. Intent: {intent or 'n/a'}")
                return "\n".join(stage_lines)

            # CAP-002+ execute exactly what the brain selected, in order.
            current_code = code
            used_ids: list[str] = []
            last_result: Any = None
            final_modified_code: Optional[str] = None

            for step in steps:
                capability_id = str(step["capability_id"])
                selected = self._resolve_template(capability_id)
                if selected is None or selected.id == "CAP-001":
                    return f"Pipeline error: Ollama selected unavailable capability {capability_id}."
                stage_lines.append(f"  {selected.id} {selected.name} → running")
                result = load_entry_point(selected)(
                    CapabilityContext(
                        code=current_code,
                        language=language,
                        file_path=target_file,
                        project_path=project_path,
                        parameters={
                            "llm_provider": self.llm_provider,
                            "llm_model": self.llm_model,
                            "llm_timeout_seconds": 120.0,
                        },
                        metadata={
                            "request": user_request,
                            "brain_reason": step.get("reason", ""),
                        },
                    )
                )
                last_result = result
                if not result.success:
                    stage_lines[-1] = stage_lines[-1].replace("running", f"failed: {result.error}")
                    return "\n".join(stage_lines)
                used_ids.append(selected.id)
                if result.modified_code is not None:
                    current_code = result.modified_code
                    final_modified_code = current_code
                stage_lines[-1] = stage_lines[-1].replace("running", "completed ✓")

            if final_modified_code is None:
                stage_lines.append(f"  Result: analysis complete ({used_ids[-1] if used_ids else 'none'}).")
                if last_result is not None:
                    stage_lines.append(f"  Summary: {last_result.summary}")
                return "\n".join(stage_lines)

            change = Change.new(
                capability_id=used_ids[-1],
                description=user_request,
                edits=[FileEdit(file_path=target_file, new_content=final_modified_code)],
                target_language=language,
                test_command="pytest -q",
            )
            validator = Validator(project_path)
            sandbox = validator.run_in_sandbox(final_modified_code, change.change_id, target_file)
            if sandbox.status.value != "success":
                return "\n".join(stage_lines) + f"\n  Layer 6 Validation: {sandbox.status.value} ✗"
            stage_lines.append("  Layer 6 Validation → sandbox passed ✓")

            decision = GovernanceGate().make_decision(
                change.change_id,
                self._change_type_for_capability(used_ids[-1]),
                change.description,
                [target_file],
                related_capabilities=used_ids,
            )
            stage_lines.append(f"  Layer 7 Governance → {decision.decision.value}")
            if decision.decision != DecisionStatus.AUTO_APPROVED:
                return "\n".join(stage_lines) + f"\n  Reason: {decision.rationale}"

            execution = self.execution.execute_change(change, project_path)
            stage_lines.append(f"  Layer 10 Execution → {execution.status.value}")
            stage_lines.append(
                f"  Brain: Ollama | Intent: {intent or 'n/a'} | Capabilities: {', '.join(used_ids)}"
            )
            return "\n".join(stage_lines)
        except Exception as exc:
            return f"Error: {exc}"

    def format_response(self, execution_result: Any, *, capability_id: str, coverage: Optional[float], validation_status: str, governance_status: str) -> str:
        coverage_text = "not reported" if coverage is None else f"{coverage:.1f}%"
        if execution_result.status == ExecutionStatus.SUCCESS:
            return ("✓ Change applied successfully!\n" f"  Capability used: {capability_id}\n" f"  Validation: {validation_status}\n" f"  Governance: {governance_status}\n" f"  Tests passing: {execution_result.tests_passing}\n" f"  Tests failing: {execution_result.tests_failing}\n" f"  Code coverage: {coverage_text}\n" f"  Execution time: {execution_result.execution_time_ms}ms")
        return (f"✗ Change {execution_result.status.value}.\n" f"  Capability used: {capability_id}\n" f"  Validation: {validation_status}\n" f"  Governance: {governance_status}\n" f"  Error: {execution_result.error_message or 'unknown error'}")

    def _resolve_template(self, capability_id: str):
        for template in self.registry.list_all_capabilities():
            if template.id == capability_id:
                return template
        for template in load_seed_capabilities():
            if template.id == capability_id:
                return template
        return None

    @staticmethod
    def _change_type_for_capability(capability_id: str) -> ChangeType:
        return {
            "CAP-002": ChangeType.LOGIC_FIX,
            "CAP-003": ChangeType.SYNTAX_FIX,
            "CAP-004": ChangeType.TEST_GENERATION,
            "CAP-005": ChangeType.REFACTORING,
            "CAP-006": ChangeType.LOGIC_FIX,
            "CAP-007": ChangeType.REFACTORING,
            "CAP-008": ChangeType.REFACTORING,
            "CAP-009": ChangeType.FEATURE_ADDITION,
            "CAP-010": ChangeType.LOGIC_FIX,
            "CAP-011": ChangeType.FEATURE_ADDITION,
        }.get(capability_id, ChangeType.LOGIC_FIX)

    @staticmethod
    def _choose_target_file(project_path: str, language: str, user_request: str) -> tuple[Optional[str], str]:
        suffixes = {"python": {".py"}, "java": {".java"}, "javascript": {".js", ".jsx"}, "typescript": {".ts", ".tsx"}, "go": {".go"}, "csharp": {".cs"}}
        requested = user_request.lower()
        candidates = []
        for path in sorted(Path(project_path).rglob("*")):
            if not path.is_file() or path.suffix not in suffixes.get(language, set()):
                continue
            score = sum(1 for token in requested.split() if len(token) > 3 and token in str(path).lower())
            candidates.append((score, path))
        if not candidates:
            return None, ""
        candidates.sort(key=lambda item: (-item[0], str(item[1])))
        target = candidates[0][1]
        return str(target.relative_to(Path(project_path))).replace("\\", "/"), target.read_text(encoding="utf-8")

    def _load_history(self) -> Dict[str, Any]:
        if not self.history_path.exists():
            return {"version": "1.0.0", "events": []}
        try:
            data = json.loads(self.history_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {"version": "1.0.0", "events": []}
        except json.JSONDecodeError:
            return {"version": "1.0.0", "events": []}

    def _record_event(self, kind: str, command: str, response: str) -> None:
        self._history.setdefault("events", []).append({"timestamp": datetime.now(timezone.utc).isoformat(), "kind": kind, "command": command, "response": response})
        self.history_path.write_text(json.dumps(self._history, indent=2), encoding="utf-8")


def main() -> None:
    SPS_CA_Interface().start_interactive_session()


if __name__ == "__main__":
    main()
