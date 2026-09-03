"""SPS-CA web application API and static presentation server."""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brain import Brain  # noqa: E402
from core.assistant_service import SpsAssistantService  # noqa: E402
from layers.architecture import architecture_manifest  # noqa: E402
from layers.layer_08_evolution.evolution_evidence import EvolutionEvidenceStore  # noqa: E402
from ui.session_store import SessionStore  # noqa: E402

REGISTRY_PATH = str(ROOT / "capabilities" / "registry.json")
EXPERIENCE_PATH = str(ROOT / "experience" / "logs" / "experience_log.json")
SESSIONS_PATH = ROOT / "runtime" / "sessions.json"
EVOLUTION_PATH = ROOT / "runtime" / "evolution_events.json"

sessions = SessionStore(SESSIONS_PATH)
evolution = EvolutionEvidenceStore(EVOLUTION_PATH, REGISTRY_PATH)


def service_for(model: str = "") -> SpsAssistantService:
    return SpsAssistantService(registry_path=REGISTRY_PATH, experience_path=EXPERIENCE_PATH, model=model)


def capability_directory() -> list[dict[str, Any]]:
    return service_for().capability_directory()


def growth_data() -> dict[str, Any]:
    caps = capability_directory()
    events = evolution.list_events(200)
    generated = sum(1 for c in caps if c.get("generated"))
    return {
        "total_capabilities": len(caps),
        "seed_capabilities": len(caps) - generated,
        "generated_capabilities": generated,
        "active_capabilities": sum(1 for c in caps if c.get("usable")),
        "disagreements": sum(1 for e in events if e.get("event_type") == "disagreement"),
        "evolution_events": len(events),
        "timeline": events,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "SPS-CA/3.0"

    def _send(self, status: int, payload: Any, content_type: str = "application/json") -> None:
        if isinstance(payload, bytes):
            body = payload
        elif content_type == "application/json":
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        else:
            body = str(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) or b"{}"
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        routes = {
            "/": (ROOT / "ui" / "web" / "index.html", "text/html"),
            "/static/app.js": (ROOT / "ui" / "web" / "app.js", "text/javascript"),
            "/static/styles.css": (ROOT / "ui" / "web" / "styles.css", "text/css"),
        }
        if path in routes:
            file_path, content_type = routes[path]
            self._send(200, file_path.read_bytes(), content_type)
            return
        if path == "/api/architecture":
            self._send(200, architecture_manifest())
            return
        if path == "/api/capabilities":
            self._send(200, {"capabilities": capability_directory()})
            return
        if path == "/api/growth":
            self._send(200, growth_data())
            return
        if path == "/api/sessions":
            self._send(200, {"sessions": sessions.list()})
            return
        if path.startswith("/api/sessions/"):
            session_id = path.rsplit("/", 1)[-1]
            session = sessions.get(session_id)
            if not session:
                self._send(404, {"error": "session not found"})
            else:
                self._send(200, session)
            return
        if path == "/api/evolution":
            self._send(200, {"events": evolution.list_events(200)})
            return
        if path.startswith("/api/evolution/capability/"):
            capability_id = path.rsplit("/", 1)[-1]
            self._send(200, evolution.get_capability_lineage(capability_id))
            return
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            data = self._json_body()
            if path == "/api/sessions":
                self._send(201, sessions.create(str(data.get("title", "New chat"))))
                return
            if path == "/api/chat":
                self._handle_chat(data)
                return
            if path == "/api/feedback":
                self._handle_feedback(data)
                return
            self._send(404, {"error": "not found"})
        except Exception as exc:  # noqa: BLE001
            self._send(500, {"error": f"SPS-CA request failed: {exc}"})

    def do_PUT(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if not path.startswith("/api/sessions/"):
            self._send(404, {"error": "not found"})
            return
        try:
            session_id = path.rsplit("/", 1)[-1]
            data = self._json_body()
            current = sessions.get(session_id)
            if not current:
                self._send(404, {"error": "session not found"})
                return
            saved = sessions.save(
                session_id,
                data.get("conversation", current.get("conversation", [])),
                str(data.get("code", current.get("code", ""))),
                str(data.get("filename", current.get("filename", "main.py"))),
                str(data.get("detected_language", current.get("detected_language", "unknown"))),
                float(data.get("language_confidence", current.get("language_confidence", 0.0))),
                str(data.get("model", current.get("model", ""))),
                str(data.get("title", current.get("title", "New chat"))),
            )
            self._send(200, saved)
        except Exception as exc:  # noqa: BLE001
            self._send(400, {"error": str(exc)})

    def do_DELETE(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if not path.startswith("/api/sessions/"):
            self._send(404, {"error": "not found"})
            return
        session_id = path.rsplit("/", 1)[-1]
        self._send(200 if sessions.delete(session_id) else 404, {"deleted": True})

    def _handle_chat(self, data: dict[str, Any]) -> None:
        request = str(data.get("request", "")).strip()
        if not request:
            self._send(400, {"error": "request is required"})
            return
        session_id = str(data.get("session_id", ""))
        if not session_id:
            session = sessions.create(request[:60])
            session_id = session["id"]
        session = sessions.get(session_id)
        if not session:
            self._send(404, {"error": "session not found"})
            return

        code = str(data.get("code", session.get("code", "")))
        filename = str(data.get("filename", session.get("filename", "main.py")))
        model = str(data.get("model", session.get("model", "qwen2.5-coder:7b")))
        conversation = data.get("conversation", session.get("conversation", []))
        if not isinstance(conversation, list):
            self._send(400, {"error": "conversation must be a list"})
            return

        detected_language, confidence, evidence = Brain.detect_language(code, request, filename)
        service = service_for(model)
        turn = service.run_turn(request=request, code=code, language=detected_language, filename=filename, conversation=conversation)
        payload = turn.as_dict()
        payload.update({
            "session_id": session_id,
            "language": detected_language,
            "language_confidence": confidence,
            "language_evidence": evidence,
            "capabilities": service.capability_catalog(),
        })
        if turn.success:
            updated = conversation + [{"role": "user", "content": request}, {"role": "assistant", "content": turn.assistant_message}]
            saved = sessions.save(session_id, updated, turn.output_code or code, filename, detected_language, confidence, model)
            payload["session"] = saved
        self._send(200 if turn.success else 422, payload)

    def _handle_feedback(self, data: dict[str, Any]) -> None:
        feedback = str(data.get("feedback", "agree")).lower()
        if feedback not in {"agree", "disagree"}:
            self._send(400, {"error": "feedback must be agree or disagree"})
            return
        if feedback == "agree":
            self._send(200, {"status": "recorded", "feedback": "agree", "evolution": {"decision": "none", "reasoning": "User accepted the result; no evolution analysis was required."}})
            return
        event = evolution.record_disagreement(
            session_id=str(data.get("session_id", "")),
            turn_id=int(data.get("turn_id", 0)),
            request=str(data.get("request", "")),
            language=str(data.get("language", "unknown")),
            language_confidence=float(data.get("language_confidence", 0.0)),
            previous_capability_id=str(data.get("capability_id", "")),
            code=str(data.get("code", "")),
        )
        analysis = evolution.analyze(event)
        if analysis.get("decision") == "create":
            analysis = evolution.record_creation(analysis)
        self._send(200, {"status": "recorded", "feedback": "disagree", "evolution": analysis})

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[SPS-CA] {fmt % args}")


class ReusableHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def main() -> None:
    host, port = "127.0.0.1", 5000
    print(f"SPS-CA dashboard: http://{host}:{port}")
    print("Chat sessions: persistent | Language: Brain auto-detect | Evolution: explainable")
    ReusableHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
