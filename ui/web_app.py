"""SPS-CA web application API and static presentation server."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brain import Brain
from core.assistant_service import SpsAssistantService
from core.self_programming_service import SelfProgrammingService
from layers.architecture import architecture_manifest
from layers.layer_05_experience.long_term_learning import LongTermLearningStore
from layers.layer_08_evolution.evolution_evidence import EvolutionEvidenceStore
from experience.evolution_trace import EvolutionTraceStore
from ui.session_store import SessionStore

REGISTRY_PATH = str(ROOT / "capabilities" / "registry.json")
EXPERIENCE_PATH = str(ROOT / "experience" / "logs" / "experience_log.json")
SESSIONS_PATH = ROOT / "runtime" / "sessions.json"
EVOLUTION_PATH = ROOT / "runtime" / "evolution_events.json"
EVALUATION_RESULTS_DIR = ROOT / "evaluation" / "results" / "scenario_runs"
EVALUATION_LOG_DIR = ROOT / "runtime" / "evaluation_runs"

sessions = SessionStore(SESSIONS_PATH)
evolution = EvolutionEvidenceStore(EVOLUTION_PATH, REGISTRY_PATH)
trace_store = EvolutionTraceStore(ROOT / "experience" / "traces" / "evolution_history.json", ROOT / "experience" / "traces" / "stage_state.json")
self_programming = SelfProgrammingService(ROOT)
long_term = LongTermLearningStore(ROOT / "experience" / "logs" / "long_term_learning.json")


def service_for(model: str = "") -> SpsAssistantService:
    return SpsAssistantService(registry_path=REGISTRY_PATH, experience_path=EXPERIENCE_PATH, model=model)


def capability_directory() -> list[dict[str, Any]]:
    capabilities = service_for().capability_directory()
    generated_metadata: dict[str, dict[str, Any]] = {}
    for metadata_path in (ROOT / "capabilities" / "generated").glob("cap_*/metadata.json"):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if isinstance(metadata, dict) and metadata.get("id"):
                generated_metadata[str(metadata["id"])] = metadata
        except (OSError, json.JSONDecodeError):
            continue
    for capability in capabilities:
        metadata = generated_metadata.get(str(capability.get("id")))
        if metadata:
            capability["origin"] = metadata.get("origin", capability.get("origin"))
            capability["historical_id"] = metadata.get("historical_id")
            capability["created_date"] = metadata.get("created_date") or capability.get("created_date")
            capability["trigger_tasks"] = metadata.get("trigger_tasks", capability.get("trigger_tasks", []))
            extra = metadata.get("extra_metadata") or {}
            if extra.get("provenance"):
                capability["provenance"] = extra["provenance"]
        capability.setdefault("created_date", "")
        capability.setdefault("provenance", {})
    return capabilities


def growth_data() -> dict[str, Any]:
    caps = capability_directory()
    events = evolution.list_events(200)
    generated = sum(1 for c in caps if c.get("generated") and c.get("origin") != "historical_migration")
    historical = sum(1 for c in caps if c.get("origin") == "historical_migration")
    learning = long_term.context()
    return {
        "total_capabilities": len(caps),
        "seed_capabilities": len(caps) - generated - historical,
        "generated_capabilities": generated,
        "historical_capabilities": historical,
        "active_capabilities": sum(1 for c in caps if c.get("usable")),
        "disagreements": sum(1 for e in events if e.get("event_type") == "disagreement"),
        "agreements": sum(1 for e in events if e.get("event_type") == "agreement"),
        "evolution_events": len(events),
        "learning": learning,
        "timeline": events,
    }


def latest_evaluation() -> dict[str, Any]:
    latest = EVALUATION_RESULTS_DIR / "latest.json"
    if not latest.exists():
        return {"status": "not_run", "scenarios": []}
    try:
        value = json.loads(latest.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {"status": "invalid", "scenarios": []}
    except (OSError, json.JSONDecodeError):
        return {"status": "unavailable", "scenarios": []}


def evaluation_runs() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not EVALUATION_RESULTS_DIR.exists():
        return rows
    for path in sorted(EVALUATION_RESULTS_DIR.glob("suite_*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                rows.append({"run_id": data.get("run_id", path.stem), "total": data.get("total", 0), "passed": data.get("passed", 0), "failed": data.get("failed", 0), "pass_rate": data.get("pass_rate", 0.0), "finished_at": data.get("finished_at"), "suite": data.get("suite")})
        except (OSError, json.JSONDecodeError):
            continue
        if len(rows) >= 25:
            break
    return rows


def extract_prompt_code(request: str) -> tuple[str, str]:
    matches = re.findall(r"```([\w+#.-]*)\s*\n([\s\S]*?)```", request or "", re.MULTILINE)
    if not matches:
        return "", ""
    lang, code = matches[0]
    return code.strip(), lang.strip().lower()


LANGUAGE_ALIASES = {
    "py": "python", "python": "python", "java": "java", "js": "javascript", "javascript": "javascript",
    "jsx": "javascript", "ts": "typescript", "typescript": "typescript", "tsx": "typescript",
    "go": "go", "golang": "go", "c#": "csharp", "csharp": "csharp", "cs": "csharp",
    "c++": "cpp", "cpp": "cpp", "rust": "rust",
}


def requested_target_language(request: str) -> str:
    text = " ".join((request or "").lower().split())
    if not text:
        return ""
    language = r"(python|py|java|javascript|js|jsx|typescript|ts|tsx|go|golang|c#|csharp|cs|c\+\+|cpp|rust)"
    directive = r"(?:generate|write|create|build|make|develop|implement|rewrite|convert|translate|port|change|modify)"
    patterns = (
        rf"\b{directive}\b.*?\b(?:in|to|using|with)\s+{language}\b",
        rf"\b{directive}\b.*?\b{language}\s+(?:code|program|script|function|application)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            for group in reversed(match.groups()):
                normalized = LANGUAGE_ALIASES.get(group, "")
                if normalized:
                    return normalized
    return ""


def build_persisted_turn_data(payload: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(payload)
    metadata.pop("conversation", None)
    metadata.pop("session", None)
    return metadata


def internal_failure_scope(error_text: str) -> tuple[str, list[str]] | None:
    text = (error_text or "").lower()
    if any(token in text for token in ("provider unavailable", "timed out", "ollama", "model '")):
        return None
    mapping = (
        (("circular reference", "serialization", "json"), "chat persistence serialization", ["ui/web_app.py"]),
        (("routing", "intent classification", "test_generation"), "brain routing", ["brain/brain.py", "brain/routing_guard.py"]),
        (("trace", "audit trail", "evolution history"), "trace persistence", ["ui/web_app.py", "experience/evolution_trace.py"]),
        (("session", "conversation state", "state failure"), "session state", ["ui/session_store.py", "ui/web_app.py"]),
        (("validation", "validator", "regression"), "validation path", ["core/assistant_service.py"]),
        (("execution", "rollback", "sandbox"), "execution path", ["layers/layer_10_execution/execution_engine.py"]),
    )
    for tokens, component, files in mapping:
        if any(token in text for token in tokens):
            return component, files
    return None


def attempt_internal_repair(error_text: str, component: str, affected_files: list[str]) -> dict[str, Any] | None:
    scope = internal_failure_scope(error_text)
    if scope is None:
        return None
    chosen_component, chosen_files = scope
    try:
        return self_programming.repair(
            symptom=error_text,
            component=component or chosen_component,
            affected_files=chosen_files if chosen_files else affected_files,
            tests=["python -m pytest -q"],
        )
    except Exception as repair_error:  # noqa: BLE001
        return {"success": False, "error": str(repair_error), "attempted": True, "component": chosen_component}


class Handler(BaseHTTPRequestHandler):
    server_version = "SPS-CA/3.6"

    def _send(self, status: int, payload: Any, content_type: str = "application/json") -> None:
        body = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode() if content_type == "application/json" else str(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        data = json.loads(self.rfile.read(length) or b"{}")
        return data if isinstance(data, dict) else {}

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        routes = {
            "/": (ROOT / "ui" / "web" / "index.html", "text/html"),
            "/static/app.js": (ROOT / "ui" / "web" / "app.js", "text/javascript"),
            "/static/styles.css": (ROOT / "ui" / "web" / "styles.css", "text/css"),
            "/static/progress.js": (ROOT / "ui" / "web" / "progress.js", "text/javascript"),
        }
        if path in routes:
            p, ct = routes[path]
            self._send(200, p.read_bytes(), ct)
            return
        if path == "/api/architecture": self._send(200, architecture_manifest()); return
        if path == "/api/capabilities": self._send(200, {"capabilities": capability_directory()}); return
        if path == "/api/growth": self._send(200, growth_data()); return
        if path == "/api/learning": self._send(200, long_term.context()); return
        if path == "/api/evaluation/latest": self._send(200, latest_evaluation()); return
        if path == "/api/evaluation/runs": self._send(200, {"runs": evaluation_runs()}); return
        if path == "/api/sessions": self._send(200, {"sessions": sessions.list()}); return
        if path.startswith("/api/sessions/"):
            s = sessions.get(path.rsplit("/", 1)[-1]); self._send(200, s) if s else self._send(404, {"error": "session not found"}); return
        if path == "/api/evolution": self._send(200, {"events": evolution.list_events(200)}); return
        if path.startswith("/api/evolution/capability/"):
            self._send(200, evolution.get_capability_lineage(path.rsplit("/", 1)[-1])); return
        if path.startswith("/api/trace/"):
            scenario_id = path.rsplit("/", 1)[-1]
            records = trace_store.list_records()
            record = next((r for r in reversed(records) if r.get("scenario_id") == scenario_id), None)
            self._send(200, record or {"error": "trace not found", "scenario_id": scenario_id}); return
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            data = self._json_body()
            if path == "/api/sessions": self._send(201, sessions.create(str(data.get("title", "New chat")))); return
            if path == "/api/chat": self._handle_chat(data); return
            if path == "/api/chat/stream": self._handle_chat_stream(data); return
            if path == "/api/feedback": self._handle_feedback(data); return
            if path == "/api/evaluation/run": self._start_evaluation(data); return
            self._send(404, {"error": "not found"})
        except Exception as exc:
            self._send(500, {"error": f"SPS-CA request failed: {exc}"})

    def do_PUT(self) -> None:
        path = urlparse(self.path).path
        if not path.startswith("/api/sessions/"): self._send(404, {"error": "not found"}); return
        try:
            sid = path.rsplit("/", 1)[-1]; data = self._json_body(); cur = sessions.get(sid)
            if not cur: self._send(404, {"error": "session not found"}); return
            conversation = data.get("conversation", cur.get("conversation", []))
            saved = sessions.save(
                sid, conversation, str(data.get("code", cur.get("code", ""))),
                str(data.get("filename", cur.get("filename", "main.py"))),
                str(data.get("detected_language", cur.get("detected_language", "unknown"))),
                float(data.get("language_confidence", cur.get("language_confidence", 0.0))),
                str(data.get("model", cur.get("model", ""))), str(data.get("title", cur.get("title", "New chat"))),
            )
            self._send(200, saved)
        except Exception as exc: self._send(400, {"error": str(exc)})

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        if not path.startswith("/api/sessions/"): self._send(404, {"error": "not found"}); return
        deleted = sessions.delete(path.rsplit("/", 1)[-1]); self._send(200 if deleted else 404, {"deleted": True})

    def _handle_chat(self, data: dict[str, Any]) -> None:
        request = str(data.get("request", "")).strip()
        if not request: self._send(400, {"error": "request is required"}); return
        sid = str(data.get("session_id", ""))
        if not sid: sid = sessions.create(request[:60])["id"]
        session = sessions.get(sid)
        if not session: self._send(404, {"error": "session not found"}); return

        explicit_code = str(data.get("code", session.get("code", "")))
        prompt_code, prompt_tag = extract_prompt_code(request)
        code = explicit_code.strip() or prompt_code
        filename = str(data.get("filename", session.get("filename", "main.py")))
        model = str(data.get("model", session.get("model", "")))
        conversation = data.get("conversation", session.get("conversation", []))
        if not isinstance(conversation, list): self._send(400, {"error": "conversation must be a list"}); return

        detected, confidence, evidence = Brain.detect_language(code, request, filename)
        if prompt_tag in Brain.SUPPORTED and prompt_tag != detected: detected, confidence, evidence = prompt_tag, 0.99, "explicit fenced-code language tag in prompt"
        target_language = requested_target_language(request)
        intent_class = Brain.infer_intent_class(request, code, filename)
        if target_language: detected, confidence, evidence = target_language, 0.99, "explicit target language in current request"
        turn_code = "" if target_language and intent_class == "code_generation" else code

        service = service_for(model)
        original_detect_language = service.brain.detect_language
        if target_language: service.brain.detect_language = lambda _code, _request, _filename: (target_language, 0.99, "explicit target language in current request")
        try:
            turn = service.run_turn(request=request, code=turn_code, language=detected, filename=filename, conversation=conversation)
        except Exception as exc:  # noqa: BLE001
            repair = attempt_internal_repair(str(exc), "chat turn execution", ["core/assistant_service.py"])
            payload = {"success": False, "error": str(exc), "assistant_message": f"I could not complete this turn: {exc}", "self_programming": repair}
            self._send(500, payload)
            return
        finally:
            service.brain.detect_language = original_detect_language

        payload = turn.as_dict()
        payload.update({"session_id": sid, "language": detected, "language_confidence": confidence,
                        "language_evidence": evidence, "capabilities": service.capability_catalog(),
                        "model": turn.brain.get("model", service.brain.model)})
        if turn.success:
            persisted_conversation = list(turn.conversation)
            if persisted_conversation and persisted_conversation[-1].get("role") == "assistant":
                persisted_conversation[-1] = {**persisted_conversation[-1], "turnData": build_persisted_turn_data(payload)}
            payload["conversation"] = persisted_conversation
            try:
                payload["session"] = sessions.save(sid, persisted_conversation, turn.output_code or turn_code, filename, detected, confidence, payload["model"])
            except Exception as exc:  # noqa: BLE001
                repair = attempt_internal_repair(str(exc), "chat persistence", ["ui/web_app.py"])
                payload["self_programming"] = repair
                payload["persistence_error"] = str(exc)
                self._send(500, payload)
                return
        else:
            repair = attempt_internal_repair(turn.error or payload.get("error", ""), "failed SPS turn", ["core/assistant_service.py"])
            if repair: payload["self_programming"] = repair
        self._send(200 if turn.success else 422, payload)

    def _handle_chat_stream(self, data: dict[str, Any]) -> None:
        """Stream lifecycle updates while the real chat worker is executing."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        def emit(event: dict[str, Any]) -> None:
            self.wfile.write(("data: " + json.dumps(event, ensure_ascii=False) + "\n\n").encode("utf-8"))
            self.wfile.flush()

        captured: list[tuple[int, Any, str]] = []
        finished = threading.Event()
        original_send = self._send

        def capture(status: int, payload: Any, content_type: str = "application/json") -> None:
            captured.append((status, payload, content_type))

        self._send = capture  # type: ignore[method-assign]
        worker = threading.Thread(target=lambda: self._run_captured_chat(data, finished, original_send), daemon=True)
        worker.start()
        started = time.monotonic()
        emit({"type": "stage", "stage": "request_received", "progress": 8})
        while not finished.wait(0.8):
            elapsed = time.monotonic() - started
            progress = min(86, 18 + int(elapsed * 6))
            emit({"type": "stage", "stage": "running", "progress": progress, "elapsed_seconds": round(elapsed, 1)})
        self._send = original_send

        if captured:
            status, payload, _ = captured[-1]
            trace = payload.get("trace", {}) if isinstance(payload, dict) else {}
            for event in trace.get("events", []) if isinstance(trace, dict) else []:
                stage_name = str(event.get("stage", "")).lower()
                if "software dna" in stage_name:
                    key, pct = "rules_checked", 24
                elif "cognitive" in stage_name:
                    key, pct = "planning", 42
                elif "capability execution" in stage_name:
                    key, pct = "capability", 65
                elif "meta-learning" in stage_name:
                    key, pct = "learning", 82
                else:
                    continue
                emit({"type": "stage", "stage": key, "progress": pct})
            if isinstance(payload, dict):
                emit({"type": "result", "payload": payload, "status": status})
            else:
                emit({"type": "error", "message": "Invalid chat response."})
        else:
            emit({"type": "error", "message": "Chat worker ended without a response."})
        emit({"type": "stage", "stage": "complete", "progress": 100})

    def _run_captured_chat(self, data: dict[str, Any], finished: threading.Event, original_send: Any) -> None:
        try:
            self._handle_chat(data)
        except Exception as exc:  # noqa: BLE001
            original_send(500, {"success": False, "error": str(exc), "assistant_message": f"I could not complete this turn: {exc}"})
        finally:
            finished.set()

    def _start_evaluation(self, data: dict[str, Any]) -> None:
        EVALUATION_LOG_DIR.mkdir(parents=True, exist_ok=True)
        run_token = f"evaluation_{int(time.time())}"
        log_path = EVALUATION_LOG_DIR / f"{run_token}.log"
        cmd = [sys.executable, "-m", "evaluation.scenario_runner"]
        if bool(data.get("live_evolve")):
            cmd.append("--live-evolve")
        if bool(data.get("measure_improvement")):
            cmd.append("--measure-improvement")
        if data.get("max_scenarios") is not None:
            cmd.extend(["--max-scenarios", str(int(data["max_scenarios"]))])
        with log_path.open("wb") as log:
            process = subprocess.Popen(cmd, cwd=str(ROOT), stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        self._send(202, {"status": "started", "run_id": run_token, "pid": process.pid, "log": str(log_path.relative_to(ROOT))})

    def _handle_feedback(self, data: dict[str, Any]) -> None:
        feedback = str(data.get("feedback", "agree")).lower()
        if feedback not in {"agree", "disagree"}: self._send(400, {"error": "feedback must be agree or disagree"}); return
        common = {
            "session_id": str(data.get("session_id", "")), "turn_id": int(data.get("turn_id", 0)),
            "request": str(data.get("request", "")), "language": str(data.get("language", "unknown")),
            "capability_id": str(data.get("capability_id", "")), "code": str(data.get("code", "")),
        }
        if feedback == "agree":
            event = evolution.record_agreement(**common)
            self._send(200, {"status": "recorded", "feedback": "agree", "evolution": event}); return
        event = evolution.record_disagreement(
            session_id=common["session_id"], turn_id=common["turn_id"], request=common["request"],
            language=common["language"], language_confidence=float(data.get("language_confidence", 0.0)),
            previous_capability_id=common["capability_id"], code=common["code"],
        )
        analysis = evolution.analyze(event)
        if analysis.get("decision") == "create": analysis = evolution.record_creation(analysis)
        self._send(200, {"status": "recorded", "feedback": "disagree", "evolution": analysis})

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[SPS-CA] {fmt % args}")


class ReusableHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def main() -> None:
    host, port = "127.0.0.1", 5000
    print(f"SPS-CA dashboard: http://{host}:{port}")
    print("Persistent Chat | Brain Auto Language | Explainable Evolution | Ollama Auto Model")
    ReusableHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
