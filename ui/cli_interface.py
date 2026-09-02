from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# Required for the documented `python ui/cli_interface.py` entrypoint.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from capabilities.base import CapabilityContext  # noqa: E402
from capabilities.seed_registry import load_entry_point, load_seed_capabilities  # noqa: E402
from experience.evolution_trace import EvolutionTraceStore  # noqa: E402
from layers.layer_02_cognitive_core import CognitiveCore  # noqa: E402
from layers.layer_06_validation import Validator  # noqa: E402
from layers.layer_07_governance import (  # noqa: E402
    ChangeType,
    DecisionStatus,
    GovernanceGate,
)
from layers.layer_09_capability_registry import CapabilityRegistryManager  # noqa: E402
from layers.layer_10_execution import (  # noqa: E402
    Change,
    ExecutionEngine,
    ExecutionStatus,
    FileEdit,
)

HELP_TEXT = """Commands:
  load <project_path>      Load a target project
  submit                   Submit a prompt + pasted code as a research scenario
  submit_file <path>      Submit a prompt + local code file as a research scenario
  show project             Show current project context
  show registry            Show available capabilities
  show experience          Show recent recorded UI interactions
  show evolution           Show recent Stage 0..N evolution records
  help                     Show this help
  quit                     Exit SPS-CA

Any other input is treated as a natural-language coding request for a loaded project."""


class SPS_CA_Interface:
    """Simple ChatGPT-like prompt interface for SPS-CA."""

    def __init__(
        self,
        history_path: str | Path = "ui/session_history.json",
        registry_path: str = "capabilities/registry.json",
        trace_history_path: str | Path = "experience/traces/evolution_history.json",
        trace_stage_path: str | Path = "experience/traces/stage_state.json",
    ) -> None:
        self.history_path = Path(history_path)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.core = CognitiveCore()
        self.registry = CapabilityRegistryManager(registry_path)
        self.execution = ExecutionEngine()
        self.trace_store = EvolutionTraceStore(
            history_path=trace_history_path,
            stage_path=trace_stage_path,
        )
        self.project_context: Optional[Dict[str, Any]] = None
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
        if lowered == "submit":
            response = self._interactive_submission()
            self._record_event("submit", command, response)
            return response
        if lowered.startswith("submit_file "):
            response = self._interactive_file_submission(command[12:].strip())
            self._record_event("submit_file", command, response)
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

    def _interactive_submission(self) -> str:
        """Collect a multi-line prompt + code submission in the CLI.

        The ``__END__`` marker keeps this usable in Colab and ordinary terminals
        without requiring a web UI or special terminal features.
        """
        request = input("Request: ").strip()
        language = input("Language [python]: ").strip() or "python"
        print("Paste code. Enter __END__ on its own line when finished:")
        lines: list[str] = []
        while True:
            line = input()
            if line == "__END__":
                break
            lines.append(line)
        code = "\n".join(lines)
        return self.submit_submission(request, code, language)

    def _interactive_file_submission(self, file_path: str) -> str:
        path = Path(file_path).expanduser().resolve()
        if not path.exists() or not path.is_file():
            return f"Error: code file does not exist: {file_path}"
        request = input("Request: ").strip()
        language = input(f"Language [{self._infer_language(path)}]: ").strip() or self._infer_language(path)
        try:
            code = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"Error: file is not UTF-8 text: {path}"
        return self.submit_submission(
            request,
            code,
            language,
            file_path=str(path),
        )

    def submit_submission(
        self,
        user_request: str,
        code: str,
        language: str,
        *,
        file_path: str = "",
    ) -> str:
        """Record a supervisor-facing scenario without running modification yet.

        The next implementation step will consume this exact scenario object
        and connect it to task analysis, capability search/generation, and the
        governed modification pipeline.
        """
        scenario = self.trace_store.start_scenario(
            user_request=user_request,
            code=code,
            language=language,
            file_path=file_path,
            metadata={"source": "cli_submission"},
        )
        self.trace_store.append_event(
            scenario["scenario_id"],
            "submission_received",
            {
                "why": "User supplied a coding task for SPS analysis.",
                "what": "Prompt + source code captured.",
                "how": "CLI submit/submit_file intake.",
                "language": language,
                "file_path": file_path,
            },
        )
        return (
            f"Scenario captured: {scenario['scenario_id']}\n"
            f"  Stage: {scenario['stage_before']}\n"
            f"  Language: {language}\n"
            f"  Code length: {len(code)} characters\n"
            "  Trace: experience/traces/evolution_history.json\n"
            "  Status: queued for SPS task/code analysis"
        )

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
        if context_type == "evolution":
            records = self.trace_store.list_records()[-5:]
            if not records:
                return "Evolution history: none"
            lines = ["Recent evolution scenarios:"]
            for record in records:
                lines.append(
                    f"  {record['scenario_id']} | Stage {record['stage_before']} -> "
                    f"{record['stage_after']} | {record['status']} | {record['user_request']}"
                )
            return "\n".join(lines)
        return "Unknown context. Use: project, registry, experience, evolution"

    def process_request(self, user_request: str) -> str:
        if not self.project_context:
            return "Error: no project loaded. Use: load <project_path>"
        try:
            project_path = self.project_context["path"]
            language = self.project_context["language"]
            self.core.receive_request(user_request, target_project=project_path, target_language=language)

            analysis = self.core.analyze_target_project(project_path)
            candidates = self.core.select_candidate_capabilities(analysis, user_request=user_request)
            plan = self.core.plan_modification_strategy(
                analysis, candidates, self.core.decompose_task(user_request)
            )
            selected = self._best_candidate(plan.selected_capability_ids, user_request)
            if selected is None:
                return "Cognitive Core: no suitable capability found."

            capability_fn = load_entry_point(selected)
            target_file, code = self._choose_target_file(project_path, language, user_request)
            if target_file is None:
                return f"Analysis complete. Capability used: {selected.id}. No supported source file was found."

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
            if capability_result.modified_code is None:
                return self._format_analysis_response(selected.id, capability_result)

            change = Change.new(
                capability_id=selected.id,
                description=user_request,
                edits=[FileEdit(file_path=target_file, new_content=capability_result.modified_code)],
                target_language=language,
                test_command="pytest -q",
            )

            validator = Validator(project_path)
            sandbox = validator.run_in_sandbox(
                capability_result.modified_code, change.change_id, target_file
            )
            if sandbox.status.value != "success":
                return (
                    f"Validation failed for {selected.id}.\n"
                    f"  Layer 6: {sandbox.status.value}\n"
                    f"  Change: {change.change_id}"
                )

            governance = GovernanceGate()
            decision = governance.make_decision(
                change.change_id,
                self._change_type_for_capability(selected.id),
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

            execution = self.execution.execute_change(change, project_path)
            return self.format_response(
                execution,
                capability_id=selected.id,
                coverage=getattr(sandbox.metrics_after, "code_coverage_percent", None),
                validation_status=sandbox.status.value,
                governance_status=decision.decision.value,
            )
        except Exception as exc:  # UI must not terminate the REPL.
            return f"Error: {exc}"

    def format_response(
        self,
        execution_result: Any,
        *,
        capability_id: str,
        coverage: Optional[float],
        validation_status: str,
        governance_status: str,
    ) -> str:
        coverage_text = "not reported" if coverage is None else f"{coverage:.1f}%"
        if execution_result.status == ExecutionStatus.SUCCESS:
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
            f"✗ Change {execution_result.status.value}.\n"
            f"  Capability used: {capability_id}\n"
            f"  Validation: {validation_status}\n"
            f"  Governance: {governance_status}\n"
            f"  Error: {execution_result.error_message or 'unknown error'}"
        )

    @staticmethod
    def _best_candidate(capability_ids: list[str], request: str):
        priority = (
            ("syntax", "CAP-002"),
            ("test", "CAP-003"),
            ("loop", "CAP-004"),
            ("exception", "CAP-005"),
            ("error handling", "CAP-005"),
            ("unused", "CAP-006"),
            ("annotation", "CAP-007"),
            ("type", "CAP-007"),
            ("doc", "CAP-008"),
            ("documentation", "CAP-008"),
            ("parse error", "CAP-009"),
        )
        lowered = request.lower()
        for keyword, capability_id in priority:
            if keyword in lowered and capability_id in capability_ids:
                return SPS_CA_Interface._resolve_template(capability_id)
        return SPS_CA_Interface._resolve_template(capability_ids[0]) if capability_ids else None

    @staticmethod
    def _resolve_template(capability_id: str):
        for template in load_seed_capabilities():
            if template.id == capability_id:
                return template
        return None

    @staticmethod
    def _change_type_for_capability(capability_id: str) -> ChangeType:
        return {
            "CAP-002": ChangeType.SYNTAX_FIX,
            "CAP-003": ChangeType.TEST_GENERATION,
            "CAP-004": ChangeType.REFACTORING,
            "CAP-005": ChangeType.LOGIC_FIX,
            "CAP-006": ChangeType.REFACTORING,
            "CAP-007": ChangeType.REFACTORING,
            "CAP-008": ChangeType.FEATURE_ADDITION,
            "CAP-009": ChangeType.LOGIC_FIX,
        }.get(capability_id, ChangeType.LOGIC_FIX)

    @staticmethod
    def _choose_target_file(project_path: str, language: str, user_request: str) -> tuple[Optional[str], str]:
        suffixes = {
            "python": {".py"}, "java": {".java"}, "javascript": {".js", ".jsx"},
            "typescript": {".ts", ".tsx"}, "go": {".go"}, "csharp": {".cs"},
        }
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

    @staticmethod
    def _infer_language(path: Path) -> str:
        return {
            ".py": "python",
            ".java": "java",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".go": "go",
            ".cs": "csharp",
        }.get(path.suffix.lower(), "unknown")

    @staticmethod
    def _format_analysis_response(capability_id: str, result: Any) -> str:
        lines = [
            f"✓ Analysis completed with {capability_id}.",
            f"  Summary: {result.summary}",
            f"  Findings: {len(result.findings)}",
        ]
        for finding in result.findings[:10]:
            lines.append(f"    - {finding.get('detail', finding.get('issue', 'finding'))}")
        return "\n".join(lines)

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
        self.history_path.write_text(json.dumps(self._history, indent=2), encoding="utf-8")


def main() -> None:
    SPS_CA_Interface().start_interactive_session()


if __name__ == "__main__":
    main()
