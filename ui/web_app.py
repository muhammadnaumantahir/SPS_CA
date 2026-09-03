"""SPS-CA web application API and static presentation server."""
from __future__ import annotations

import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brain import Brain
from core.assistant_service import SpsAssistantService
from layers.architecture import architecture_manifest
from layers.layer_08_evolution.evolution_evidence import EvolutionEvidenceStore
from ui.session_store import SessionStore

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


def extract_prompt_code(request: str) -> tuple[str, str]:
    matches = re.findall(r"```([\w+#.-]*)\s*\n([\s\S]*?)```", request or "", re.MULTILINE)
    if not matches:
        return "", ""
    lang, code = matches[0]
    return code.strip(), lang.strip().lower()


LANGUAGE_ALIASES = {
    "py": "python",
    "python": "python",
    "java": "java",
    "js": "javascript",
    "javascript": "javascript",
    "jsx": "javascript",
    "ts": "typescript",
    "typescript": "typescript",
    "tsx": "typescript",
    "go": "go",
    "golang": "go",
    "c#": "csharp",
    "csharp": "csharp",
    "cs": "csharp",
    "c++": "cpp",
    "cpp": "cpp",
    "rust": "rust",
}


def requested_target_language(request: str) -> str:
    """Find an explicit target language request without treating any mention as a target.

    Examples matched: 'generate code in JS', 'write this in JavaScript',
    'create a Python program', and 'convert this to Java'. Ordinary mentions
    such as 'explain Python' are deliberately ignored.
    """
    text = " ".join((request or "").lower().split())
    if not text:
        return ""
    language = r"(python|py|java|javascript|js|jsx|typescript|ts|tsx|go|golang|c#|csharp|cs|c\+\+|cpp|rust)"
    directive = r"(?:generate|write|create|build|make|develop|implement|rewrite|convert|translate|port|change)"
    patterns = (
        rf"\b{directive}\b.*?\b(?:in|to|using|with)\s+{language}\b",
        rf"\b{directive}\b.*?\b{language}\s+(?:code|program|script|function|application)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            raw = match.group(1) if match.lastindex == 1 else ""
            if raw:
                return LANGUAGE_ALIASES.get(raw, "")
            for group in reversed(match.groups()):
                normalized = LANGUAGE_ALIASES.get(group, "")
                if normalized:
                    return normalized
    return ""


class Handler(BaseHTTPRequestHandler):
    server_version = "SPS-CA/3.2"

    def _send(self, status: int, payload: Any, content_type: str = "application/json") -> None:
        body = (
            payload
            if isinstance(payload, bytes)
            else json.dumps(payload, ensure_ascii=False).encode()
            if content_type == "application/json"
            else str(payload).encode()
        )
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
        }
        if path in routes:
            p, ct = routes[path]
            self._send(200, p.read_bytes(), ct)
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
            s = sessions.get(path.rsplit("/", 1)[-1])
            self._send(200, s) if s else self._send(404, {"error": "session not found"})
            return
        if path == "/api/evolution":
            self._send(200, {"events": evolution.list_events(200)})
            return
        if path.startswith("/api/evolution/capability/"):
            self._send(200, evolution.get_capability_lineage(path.rsplit("/", 1)[-1]))
            return
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:
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
        except Exception as exc:
            self._send(500, {"error": f"SPS-CA request failed: {exc}"})

    def do_PUT(self) -> None:
        path = urlparse(self.path).path
        if not path.startswith("/api/sessions/"):
            self._send(404, {"error": "not found"})
            return
        try:
            sid = path.rsplit("/", 1)[-1]
            data = self._json_body()
            cur = sessions.get(sid)
            if not cur:
                self._send(404, {"error": "session not found"})
                return
            saved = sessions.save(
                sid,
                data.get("conversation", cur.get("conversation", [])),
                str(data.get("code", cur.get("code", ""))),
                str(data.get("filename", cur.get("filename", "main.py"))),
                str(data.get("detected_language", cur.get("detected_language", "unknown"))),
                float(data.get("language_confidence", cur.get("language_confidence", 0.0))),
                str(data.get("model", cur.get("model", ""))),
                str(data.get("title", cur.get("title", "New chat"))),
            )
            self._send(200, saved)
        except Exception as exc:
            self._send(400, {"error": str(exc)})

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        if not path.startswith("/api/sessions/"):
            self._send(404, {"error": "not found"})
            return
        deleted = sessions.delete(path.rsplit("/", 1)[-1])
        self._send(200 if deleted else 404, {"deleted": True})

    def _handle_chat(self, data: dict[str, Any]) -> None:
        request = str(data.get("request", "")).strip()
        if not request:
            self._send(400, {"error": "request is required"})
            return
        sid = str(data.get("session_id", ""))
        if not sid:
            sid = sessions.create(request[:60])["id"]
        session = sessions.get(sid)
        if not session:
            self._send(404, {"error": "session not found"})
            return

        explicit_code = str(data.get("code", session.get("code", "")))
        prompt_code, prompt_tag = extract_prompt_code(request)
        code = explicit_code.strip() or prompt_code
        filename = str(data.get("filename", session.get("filename", "main.py")))
        model = str(data.get("model", session.get("model", "qwen2.5-coder:7b")))
        conversation = data.get("conversation", session.get("conversation", []))
        if not isinstance(conversation, list):
            self._send(400, {"error": "conversation must be a list"})
            return

        detected, confidence, evidence = Brain.detect_language(code, request, filename)
        if prompt_tag in Brain.SUPPORTED and prompt_tag != detected:
            detected, confidence, evidence = prompt_tag, 0.99, "explicit fenced-code language tag in prompt"

        target_language = requested_target_language(request)
        intent_class = Brain.infer_intent_class(request, code, filename)
        if target_language:
            detected, confidence, evidence = target_language, 0.99, "explicit target language in current request"

        # A new code-generation request should not accidentally operate on the
        # previous turn's working source. Modifications/conversions still retain it.
        turn_code = "" if target_language and intent_class == "code_generation" else code

        service = service_for(model)
        original_detect_language = service.brain.detect_language
        if target_language:
            service.brain.detect_language = lambda _code, _request, _filename: (
                target_language,
                0.99,
                "explicit target language in current request",
            )

        turn = service.run_turn(
            request=request,
            code=turn_code,
            language=detected,
            filename=filename,
            conversation=conversation,
        )
        service.brain.detect_language = original_detect_language

        payload = turn.as_dict()
        payload.update(
            {
                "session_id": sid,
                "language": detected,
                "language_confidence": confidence,
                "language_evidence": evidence,
                "capabilities": service.capability_catalog(),
            }
        )
        if turn.success:
            updated = turn.conversation
            payload["session"] = sessions.save(
                sid,
                updated,
                turn.output_code or turn_code,
                filename,
                detected,
                confidence,
                model,
            )
        self._send(200 if turn.success else 422, payload)

    def _handle_feedback(self, data: dict[str, Any]) -> None:
        feedback = str(data.get("feedback", "agree")).lower()
        if feedback not in {"agree", "disagree"}:
            self._send(400, {"error": "feedback must be agree or disagree"})
            return
        if feedback == "agree":
            self._send(
                200,
                {
                    "status": "recorded",
                    "feedback": "agree",
                    "evolution": {
                        "decision": "none",
                        "reasoning": "User accepted the result; no evolution analysis was required.",
                    },
                },
            )
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
    print("Persistent Chat | Brain Auto Language | Explainable Evolution")
    ReusableHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
