"""SPS-CA conversational web interface.

The web layer is presentation-only. Conversation/session state is sent to the
shared ``SpsAssistantService`` so the Brain, capability system and Experience
core are exercised through one backend path.
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.assistant_service import SpsAssistantService  # noqa: E402
from layers.architecture import architecture_manifest  # noqa: E402

REGISTRY_PATH = str(ROOT / "capabilities" / "registry.json")
EXPERIENCE_PATH = str(ROOT / "experience" / "logs" / "experience_log.json")


def service_for(model: str = "") -> SpsAssistantService:
    return SpsAssistantService(
        registry_path=REGISTRY_PATH,
        experience_path=EXPERIENCE_PATH,
        model=model,
    )


def capability_catalog() -> list[dict[str, Any]]:
    return service_for().capability_catalog()


class Handler(BaseHTTPRequestHandler):
    server_version = "SPS-CA-Chat"

    def _send(self, status: int, payload: Any, content_type: str = "application/json") -> None:
        body = payload if isinstance(payload, bytes) else (
            json.dumps(payload, ensure_ascii=False).encode("utf-8")
            if content_type == "application/json"
            else str(payload).encode("utf-8")
        )
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        routes = {
            "/": (ROOT / "ui" / "web" / "index.html", "text/html"),
            "/static/app.js": (ROOT / "ui" / "web" / "app.js", "text/javascript"),
            "/static/styles.css": (ROOT / "ui" / "web" / "styles.css", "text/css"),
        }
        if self.path in routes:
            file_path, content_type = routes[self.path]
            self._send(200, file_path.read_bytes(), content_type)
            return
        if self.path == "/api/architecture":
            self._send(200, architecture_manifest())
            return
        if self.path == "/api/capabilities":
            self._send(200, {"capabilities": capability_catalog()})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in {"/api/chat", "/api/plan", "/api/run"}:
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")
            request = str(data.get("request", "")).strip()
            code = str(data.get("code", ""))
            language = str(data.get("language", "python"))
            filename = str(data.get("filename", "main.py"))
            model = str(data.get("model", ""))
            conversation = data.get("conversation", [])
            if not request or not code:
                self._send(400, {"error": "request and current working code are required"})
                return
            if not isinstance(conversation, list):
                self._send(400, {"error": "conversation must be a list"})
                return

            service = service_for(model)
            turn = service.run_turn(
                request=request,
                code=code,
                language=language,
                filename=filename,
                conversation=conversation,
            )
            payload = turn.as_dict()
            payload["capabilities"] = service.capability_catalog()
            if not turn.success and turn.error:
                self._send(422, payload)
                return
            self._send(200, payload)
        except Exception as exc:
            self._send(500, {"error": f"SPS-CA request failed: {exc}"})

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[SPS-CA] {fmt % args}")


def main() -> None:
    host, port = "127.0.0.1", 8080
    print(f"SPS-CA dashboard: http://{host}:{port}")
    print("Conversational coding mode: enabled")
    print("Brain: provider-neutral; Ollama is the default provider")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
