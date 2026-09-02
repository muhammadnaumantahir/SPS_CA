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
FEEDBACK_PATH = str(ROOT / "experience" / "logs" / "feedback_log.json")


def service_for(model: str = "") -> SpsAssistantService:
    return SpsAssistantService(
        registry_path=REGISTRY_PATH,
        experience_path=EXPERIENCE_PATH,
        model=model,
    )


def capability_catalog() -> list[dict[str, Any]]:
    return service_for().capability_catalog()


def capability_directory() -> list[dict[str, Any]]:
    return service_for().capability_directory()


def _load_feedback_log() -> list[dict[str, Any]]:
    path = Path(FEEDBACK_PATH)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save_feedback_log(entries: list[dict[str, Any]]) -> None:
    path = Path(FEEDBACK_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def _get_growth_data() -> dict[str, Any]:
    """Build growth statistics from capabilities and experience."""
    directory = capability_directory()
    total = len(directory)
    seeds = sum(1 for c in directory if not c.get("generated", False))
    generated = total - seeds
    usable = sum(1 for c in directory if c.get("usable"))
    deprecated = total - usable

    feedback = _load_feedback_log()
    disagreements = sum(1 for f in feedback if f.get("feedback") == "disagree")
    agreements = sum(1 for f in feedback if f.get("feedback") == "agree")

    experience_path = Path(EXPERIENCE_PATH)
    tasks = []
    if experience_path.exists():
        try:
            exp = json.loads(experience_path.read_text(encoding="utf-8"))
            tasks = exp.get("tasks", [])
        except (json.JSONDecodeError, OSError):
            pass

    total_tasks = len(tasks)
    successes = sum(1 for t in tasks if t.get("status") == "success")
    success_rate = f"{successes / total_tasks * 100:.0f}%" if total_tasks > 0 else "—"

    timeline = []
    for f in feedback[-20:]:
        timeline.append({
            "event": f"User {f.get('feedback', 'unknown')}",
            "timestamp": f.get("timestamp", ""),
            "description": f"Turn {f.get('turn_id', '?')} — {f.get('request', '')[:80]}",
        })

    # A simple chartable series: seed capability count is fixed, so any
    # growth beyond it is capability creation triggered by disagreement.
    # Build a running total of generated capabilities over each recorded
    # disagreement event, seeded at the current generated count baseline.
    growth_series: list[dict[str, Any]] = []
    running = seeds
    for f in feedback:
        if f.get("feedback") == "disagree":
            running_note = running
            growth_series.append({
                "timestamp": f.get("timestamp", ""),
                "capabilities": running_note,
            })
    if not growth_series:
        growth_series = [{"timestamp": "", "capabilities": total}]
    else:
        growth_series.append({"timestamp": "now", "capabilities": total})

    return {
        "total_capabilities": total,
        "seed_capabilities": seeds,
        "generated_capabilities": generated,
        "usable_capabilities": usable,
        "deprecated_capabilities": deprecated,
        "total_disagreements": disagreements,
        "total_agreements": agreements,
        "total_tasks": total_tasks,
        "success_rate": success_rate,
        "timeline": timeline,
        "growth_series": growth_series,
    }


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
            self._send(200, {"capabilities": capability_directory()})
            return
        if self.path == "/api/growth":
            self._send(200, _get_growth_data())
            return
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in {"/api/chat", "/api/plan", "/api/run", "/api/feedback"}:
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")

            if self.path == "/api/feedback":
                self._handle_feedback(data)
                return

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

    def _handle_feedback(self, data: dict[str, Any]) -> None:
        """Handle agree/disagree feedback. Disagrees trigger evolution analysis."""
        from datetime import datetime, timezone

        turn_id = data.get("turn_id", 0)
        feedback = data.get("feedback", "agree")
        request_text = data.get("request", "")
        capability_id = data.get("capability_id", "")

        entry = {
            "turn_id": turn_id,
            "feedback": feedback,
            "request": request_text,
            "capability_id": capability_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        log = _load_feedback_log()
        log.append(entry)
        _save_feedback_log(log)

        evolution_result = None
        if feedback == "disagree":
            # Record as a failure in experience for evolution tracking
            service = service_for()
            service._record_experience(
                request=request_text,
                language=data.get("language", "python"),
                selected_capability=capability_id,
                success=False,
                outcome=f"User disagreed with the result for {capability_id}",
                elapsed=0.0,
                failure_category="UserDisagreement",
            )
            # Count disagreements for this capability
            disagree_count = sum(
                1 for f in log
                if f.get("feedback") == "disagree" and f.get("capability_id") == capability_id
            )
            evolution_result = {
                "disagreement_count": disagree_count,
                "threshold": 3,
                "capability_id": capability_id,
            }
            if disagree_count >= 3:
                evolution_result["message"] = (
                    f"3+ disagreements on {capability_id} — evolution will generate a new capability."
                )

        self._send(200, {
            "status": "recorded",
            "feedback": feedback,
            "evolution": evolution_result,
        })

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[SPS-CA] {fmt % args}")


class ReusableHTTPServer(ThreadingHTTPServer):
    """Allow address reuse so the server can restart on the same port."""
    allow_reuse_address = True


def main() -> None:
    host, port = "127.0.0.1", 8080
    print(f"SPS-CA dashboard: http://{host}:{port}")
    print("Conversational coding mode: enabled")
    print("Brain: provider-neutral; Ollama is the default provider")
    print("Tabs: Chat | Structure | Capabilities | Growth | Guide")
    ReusableHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
