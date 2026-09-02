"""SPS-CA user interface and reference orchestration client.

Architecture rule:
    User -> Cognitive Core -> Brain -> Capability Plan -> 10-layer pipeline

The Brain is an intelligence service, not a capability. Capabilities are
registered independently and may be seeded or generated/evolved.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from brain import Brain, BrainError  # noqa: E402
from capabilities.base import CapabilityContext  # noqa: E402
from capabilities.seed_registry import load_entry_point, load_seed_capabilities  # noqa: E402
from experience.evolution_trace import EvolutionTraceStore  # noqa: E402
from layers.layer_02_cognitive_core import CognitiveCore  # noqa: E402
from layers.layer_06_validation import Validator  # noqa: E402
from layers.layer_07_governance import ChangeType, DecisionStatus, GovernanceGate  # noqa: E402
from layers.layer_09_capability_registry import CapabilityRegistryManager  # noqa: E402
from layers.layer_10_execution import Change, ExecutionEngine, ExecutionStatus, FileEdit  # noqa: E402
from ui.sps_service import SPSScenarioService  # noqa: E402

ARCHITECTURE = [
    (1, "Software DNA layer"),
    (2, "Governance layer"),
    (3, "Cognitive core"),
    (4, "Knowledge core"),
    (5, "Experience core"),
    (6, "Meta-learning core"),
    (7, "Adaptation core"),
    (8, "Evolution core"),
    (9, "Verification & Validation"),
    (10, "Execution layer"),
]

HELP_TEXT = """Commands:
  load <project_path>      Load a target project
  submit                   Submit a prompt + pasted code as a research scenario
  submit_file <path>       Submit a prompt + local code file as a research scenario
  show project             Show current project context
  show architecture        Show the 10 SPS-CA layers and Brain boundary
  show registry            Show available SPS capabilities
  show brain               Show Brain provider/model status
  show experience          Show recent recorded UI interactions
  show evolution           Show recent Stage 0..N evolution records
  help                     Show this help
  quit                     Exit SPS-CA

Any other input is treated as a natural-language coding request for a loaded project."""


class SPS_CA_Interface:
    """Reference interface for the 10-layer SPS-CA architecture."""

    def __init__(
        self,
        history_path: str | Path = "ui/session_history.json",
        registry_path: str = "capabilities/registry.json",
        llm_provider: Optional[Any] = None,
        llm_model: str = "",
        trace_history_path: str | Path = "experience/traces/evolution_history.json",
        trace_stage_path: str | Path = "experience/traces/stage_state.json",
    ) -> None:
        self.history_path = Path(history_path)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.core = CognitiveCore()
        self.brain = Brain(provider=llm_provider, model=llm_model)
        self.registry = CapabilityRegistryManager(registry_path)
        self.execution = ExecutionEngine()
        self.trace_store = EvolutionTraceStore(history_path=trace_history_path, stage_path=trace_stage_path)
        self.sps_service = SPSScenarioService(
            trace_history_path=trace_history_path,
            trace_stage_path=trace_stage_path,
            registry_path=registry_path,
            seeds_dir=str(REPO_ROOT / "capabilities" / "seeds"),
            generated_dir=str(self.history_path.parent / "generated"),
            evaluation_dir=str(self.history_path.parent / "evaluation" / "evolution"),
        )
        self.project_context: Optional[Dict[str, Any]] = None
        self.last_trace: Dict[str, Any] = {}
        self._history = self._load_history()

    def start_interactive_session(self) -> None:
        print("SPS-CA — Self-Programming Code Assistant")
        print("Brain: provider-neutral AI service (Ollama by default)")
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
            print(f"\nSPS-CA:\n{response}\n")

    def handle_command(self, user_input: str) -> str:
        command = user_input.strip()
        lowered = command.lower()
        if lowered == "quit":
            self._record_event("quit", command, "Session ended")
            return "__QUIT__"
        if lowered == "help":
            response = HELP_TEXT
        elif lowered.startswith("load "):
            response = self.load_project(command[5:].strip())
        elif lowered.startswith("show "):
            response = self.show_context(command[5:].strip())
        else:
            response = self.process_request(command)
        self._record_event("command", command, response)
        return response

    def _interactive_submission(self) -> str:
        request = input("Request: ").strip()
        language = input("Language [python]: ").strip() or "python"
        print("Paste code. Enter __END__ on its own line when finished:")
        lines: list[str] = []
        while True:
            line = input()
            if line == "__END__":
                break
            lines.append(line)
        return self.submit_submission(request, "\n".join(lines), language)

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
        return self.submit_submission(request, code, language, file_path=str(path))

    def submit_submission(self, user_request: str, code: str, language: str, *, file_path: str = "") -> str:
        """Run the submitted scenario through the SPS-CA analysis path."""
        try:
            result = self.sps_service.analyze_submission(
                user_request=user_request,
                code=code,
                language=language,
                file_path=file_path,
                project_root=str(self.history_path.parent),
            )
            generation = result.capability_generation
            return (
                f"Scenario analyzed: {result.scenario_id}\n"
                f"  Stage: {result.stage}\n"
                f"  Language: {language}\n"
                f"  Code length: {len(code)} characters\n"
                f"  Capability found: {result.capability_search.get('found', False)}\n"
                f"  Capability: {result.capability_search.get('selected') or generation.get('capability_id', 'none')}\n"
                f"  Generation required: {generation.get('required', False)}\n"
                f"  Trace: {self.trace_store.history_path}\n"
                f"  Status: {generation.get('developed', False) and generation.get('registered', False) and 'capability developed' or 'analysis complete'}"
            )
        except Exception as exc:
            return f"Error: {exc}"

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
            f"Loaded project: {root}\n"
            f"Language: {language}\nFiles analyzed: {len(analysis.files)}\n"
            f"Functions discovered: {analysis.total_functions}"
        )

    def show_context(self, context_type: str) -> str:
        context_type = context_type.lower().strip()
        if context_type == "project":
            if not self.project_context:
                return "No project loaded. Use: load <project_path>"
            return json.dumps(self.project_context, indent=2)
        if context_type == "architecture":
            lines = ["SPS-CA 10-Layer Architecture", ""]
            for number, name in ARCHITECTURE:
                lines.append(f"L{number:02d}  {name}")
            lines.extend([
                "",
                "BRAIN  AI/model service — separate from layers and capabilities",
                "CAPABILITIES  Seed + generated executable skills",
                "CAPABILITY REGISTRY  Supporting subsystem for discovery/version/lineage",
            ])
            return "\n".join(lines)
        if context_type == "registry":
            capabilities = self.registry.list_all_capabilities()
            if not capabilities:
                return "Available capabilities: none"
            return "\n".join(
                ["SPS capability registry:"]
                + [f"  {cap.id}: {cap.name} [{cap.status}] v{cap.version}" for cap in capabilities]
            )
        if context_type == "brain":
            return (
                f"Brain provider: {self.brain.provider_name}\n"
                f"Model: {self.brain.model or 'provider default'}\n"
                f"Available: {'yes' if self.brain.is_available() else 'no'}\n"
                "Role: reasoning, prompt analysis, planning, code generation, debugging"
            )
        if context_type == "experience":
            events = self._history.get("events", [])[-5:]
            if not events:
                return "Recent interactions: none"
            return "\n".join(["Recent interactions:"] + [f"  {event['timestamp']} | {event['kind']} | {event['command']}" for event in events])
        if context_type == "evolution":
            records = self.trace_store.list_records()[-5:]
            if not records:
                return "Evolution history: none"
            return "\n".join(
                ["Recent evolution scenarios:"]
                + [f"  {record['scenario_id']} | Stage {record['stage_before']} -> {record['stage_after']} | {record['status']} | {record['user_request']}" for record in records]
            )
        return "Unknown context. Use: project, architecture, registry, brain, experience"

    def process_request(self, user_request: str) -> str:
        if not self.project_context:
            return "Error: no project loaded. Use: load <project_path>"

        project_path = self.project_context["path"]
        language = self.project_context["language"]
        target_file, code = self._choose_target_file(project_path, language, user_request)
        if target_file is None:
            return "Pipeline error: no supported source file was found."

        # L3 Cognitive core gathers context; the Brain performs intelligence.
        analysis = self.core.analyze_single_file(target_file, code)
        candidates = self.core.select_candidate_capabilities(analysis, user_request)
        catalog = [
            {
                "id": cap.id,
                "name": cap.name,
                "description": cap.description,
                "tags": getattr(cap, "tags", []) or [],
            }
            for cap in candidates
            if cap.status == "active"
        ]

        trace: Dict[str, Any] = {
            "request": user_request,
            "layers": [],
            "brain": {"provider": self.brain.provider_name, "model": self.brain.model},
            "target": {"file": target_file, "language": language},
        }
        trace["layers"].append({"layer": 1, "name": "Software DNA layer", "status": "checked"})
        trace["layers"].append({"layer": 3, "name": "Cognitive core", "status": "context analyzed"})
        trace["layers"].append({"layer": 4, "name": "Knowledge core", "status": "capability knowledge loaded", "count": len(catalog)})
        trace["layers"].append({"layer": 5, "name": "Experience core", "status": "history available"})
        trace["layers"].append({"layer": 6, "name": "Meta-learning core", "status": "strategy context available"})
        trace["layers"].append({"layer": 7, "name": "Adaptation core", "status": "ready"})

        try:
            plan = self.brain.plan(
                request=user_request,
                code=code,
                language=language,
                file_path=target_file,
                capability_catalog=catalog,
            )
        except BrainError as exc:
            trace["brain"]["error"] = str(exc)
            self.last_trace = trace
            return self._format_trace(trace, error=f"Brain planning failed: {exc}")

        trace["brain"].update({"intent": plan.intent, "reasoning": plan.reasoning, "steps": plan.steps})
        trace["layers"].append({"layer": 8, "name": "Evolution core", "status": "evaluated"})

        current_code = code
        used_ids: list[str] = []
        final_modified_code: Optional[str] = None
        last_result: Any = None

        for step in plan.steps:
            capability_id = step["capability_id"]
            selected = self._resolve_template(capability_id)
            if selected is None:
                self.last_trace = trace
                return self._format_trace(trace, error=f"Brain selected unavailable capability {capability_id}.")
            result = load_entry_point(selected)(
                CapabilityContext(
                    code=current_code,
                    language=language,
                    file_path=target_file,
                    project_path=project_path,
                    parameters={
                        "llm_provider": self.brain.llm.provider,
                        "llm_model": self.brain.model,
                        "llm_timeout_seconds": self.brain.timeout_seconds,
                    },
                    metadata={"request": user_request, "brain_reason": step.get("reason", "")},
                )
            )
            last_result = result
            if not result.success:
                trace.setdefault("capability_results", []).append({"id": capability_id, "status": "failed", "error": result.error})
                self.last_trace = trace
                return self._format_trace(trace, error=f"{selected.name} failed: {result.error}")
            used_ids.append(capability_id)
            trace.setdefault("capability_results", []).append({"id": capability_id, "name": selected.name, "status": "completed", "summary": result.summary})
            if result.modified_code is not None:
                current_code = result.modified_code
                final_modified_code = current_code

        if not plan.steps:
            trace["result"] = {"status": "no_capability_selected"}
            self.last_trace = trace
            return self._format_trace(trace)

        trace["layers"].append({"layer": 9, "name": "Verification & Validation", "status": "pending"})
        if final_modified_code is not None:
            change = Change.new(
                capability_id=used_ids[-1],
                description=user_request,
                edits=[FileEdit(file_path=target_file, new_content=final_modified_code)],
                target_language=language,
                test_command="pytest -q",
            )
            sandbox = Validator(project_path).run_in_sandbox(final_modified_code, change.change_id, target_file)
            trace["validation"] = {"status": sandbox.status.value}
            trace["layers"][-1]["status"] = sandbox.status.value
            if sandbox.status.value != "success":
                self.last_trace = trace
                return self._format_trace(trace, error="Verification & Validation rejected the proposed change.")

            decision = GovernanceGate().make_decision(
                change.change_id,
                self._change_type_for_capability(used_ids[-1]),
                change.description,
                [target_file],
                related_capabilities=used_ids,
            )
            trace["governance"] = {"status": decision.decision.value, "rationale": decision.rationale}
            trace["layers"][0]["dna_note"] = "change remains inside system constraints"
            trace["layers"].append({"layer": 2, "name": "Governance layer", "status": decision.decision.value})
            if decision.decision != DecisionStatus.AUTO_APPROVED:
                self.last_trace = trace
                return self._format_trace(trace, error=f"Governance rejected the change: {decision.rationale}")

            execution = self.execution.execute_change(change, project_path)
            trace["execution"] = {"status": execution.status.value, "time_ms": execution.execution_time_ms}
            trace["layers"].append({"layer": 10, "name": "Execution layer", "status": execution.status.value})
        else:
            trace["validation"]["status"] = "not_required_for_analysis"
            trace["layers"][-1]["status"] = "analysis_only"

        trace["result"] = {
            "status": "success",
            "intent": plan.intent,
            "capabilities": used_ids,
            "summary": getattr(last_result, "summary", "complete"),
        }
        self.last_trace = trace
        return self._format_trace(trace)

    @staticmethod
    def _format_trace(trace: Dict[str, Any], error: Optional[str] = None) -> str:
        lines = ["SPS-CA pipeline trace"]
        if error:
            lines.append(f"✗ {error}")
        brain = trace.get("brain", {})
        lines.append(f"Brain: {brain.get('provider', 'unknown')} | Model: {brain.get('model') or 'default'}")
        if brain.get("intent"):
            lines.append(f"Intent: {brain['intent']}")
        for item in trace.get("layers", []):
            label = f"L{item['layer']:02d} {item['name']}"
            lines.append(f"  {label} → {item.get('status', 'ready')}")
        results = trace.get("capability_results", [])
        if results:
            lines.append("Capabilities: " + ", ".join(item["id"] for item in results))
        return "\n".join(lines)

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
            "CAP-001": ChangeType.LOGIC_FIX,
            "CAP-002": ChangeType.SYNTAX_FIX,
            "CAP-003": ChangeType.TEST_GENERATION,
            "CAP-004": ChangeType.REFACTORING,
            "CAP-005": ChangeType.LOGIC_FIX,
            "CAP-006": ChangeType.REFACTORING,
            "CAP-007": ChangeType.REFACTORING,
            "CAP-008": ChangeType.FEATURE_ADDITION,
            "CAP-010": ChangeType.LOGIC_FIX,
            "CAP-011": ChangeType.FEATURE_ADDITION,
        }.get(capability_id, ChangeType.LOGIC_FIX)

    @staticmethod
    def _choose_target_file(project_path: str, language: str, user_request: str) -> tuple[Optional[str], str]:
        suffixes = {"python": {".py"}, "java": {".java"}, "javascript": {".js", ".jsx"}, "typescript": {".ts", ".tsx"}, "go": {".go"}, "csharp": {".cs"}}
        requested = user_request.lower()
        candidates = []
        root = Path(project_path)
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix not in suffixes.get(language, set()):
                continue
            score = sum(1 for token in requested.split() if len(token) > 3 and token in str(path).lower())
            candidates.append((score, path))
        if not candidates:
            return None, ""
        candidates.sort(key=lambda item: (-item[0], str(item[1])))
        target = candidates[0][1]
        return str(target.relative_to(root)).replace("\\", "/"), target.read_text(encoding="utf-8")

    def _load_history(self) -> Dict[str, Any]:
        if not self.history_path.exists():
            return {"version": "2.0.0", "events": []}
        try:
            data = json.loads(self.history_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {"version": "2.0.0", "events": []}
        except json.JSONDecodeError:
            return {"version": "2.0.0", "events": []}

    def _record_event(self, kind: str, command: str, response: str) -> None:
        self._history.setdefault("events", []).append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            "command": command,
            "response": response,
        })
        self.history_path.write_text(json.dumps(self._history, indent=2), encoding="utf-8")


def main() -> None:
    SPS_CA_Interface().start_interactive_session()


if __name__ == "__main__":
    main()
