"""SPS-CA conversational web dashboard.

Run with: python ui/web_app.py

The top page behaves like a coding-assistant chat. Each turn carries the
current working source plus recent conversation context into the separate
Brain service. A later user message can therefore provide feedback on the
previous result without starting a new task.
"""

from __future__ import annotations

import difflib
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brain import Brain, BrainError  # noqa: E402
from capabilities.base import CapabilityContext  # noqa: E402
from capabilities.seed_registry import load_entry_point  # noqa: E402
from layers.architecture import architecture_manifest  # noqa: E402
from layers.layer_09_capability_registry import CapabilityRegistryManager  # noqa: E402

REGISTRY = CapabilityRegistryManager(str(ROOT / "capabilities" / "registry.json"))


def catalog() -> list[dict[str, Any]]:
    return [
        {"id": cap.id, "name": cap.name, "description": cap.description,
         "version": cap.version, "generated": bool(cap.generated),
         "tags": list(getattr(cap, "tags", []) or [])}
        for cap in REGISTRY.list_all_capabilities()
        if cap.status == "active"
    ]


def diff_text(before: str, after: str, filename: str) -> str:
    return "".join(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile=f"a/{filename}", tofile=f"b/{filename}",
    ))


def assistant_summary(intent: str, reasoning: str, results: list[dict[str, Any]], changed: bool) -> str:
    names = ", ".join(r["name"] for r in results if r.get("name"))
    if names:
        prefix = "Applied" if changed else "Analyzed with"
        return f"{prefix} {names}. {reasoning or intent}".strip()
    return reasoning or intent or "I analyzed the request but no capability was required."


class Handler(BaseHTTPRequestHandler):
    server_version = "SPS-CA-Chat/3.0"

    def _send(self, status: int, payload: Any, content_type: str = "application/json") -> None:
        body = payload if isinstance(payload, bytes) else (
            json.dumps(payload, ensure_ascii=False).encode("utf-8")
            if content_type == "application/json" else str(payload).encode("utf-8")
        )
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        routes = {
            "/": ("ui/web/index.html", "text/html"),
            "/static/app.js": ("ui/web/app.js", "text/javascript"),
            "/static/styles.css": ("ui/web/styles.css", "text/css"),
        }
        if self.path in routes:
            relative, content_type = routes[self.path]
            self._send(200, (ROOT / relative).read_bytes(), content_type)
            return
        if self.path == "/api/architecture":
            self._send(200, architecture_manifest())
            return
        if self.path == "/api/capabilities":
            self._send(200, {"capabilities": catalog()})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in {"/api/plan", "/api/run", "/api/chat"}:
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

            brain = Brain(model=model)
            plan = brain.plan(
                request=request, code=code, language=language, file_path=filename,
                capability_catalog=catalog(), conversation=conversation,
            )
            manifest = architecture_manifest()
            payload: dict[str, Any] = {
                "brain": plan.as_dict()["brain"], "intent": plan.intent,
                "reasoning": plan.reasoning, "steps": plan.steps,
                "assistant_message": "",
                "layers": [{**layer, "status": "ready"} for layer in manifest["layers"]],
            }
            statuses = {
                1: "constraints loaded", 2: "policy context ready", 3: "reasoned by Brain",
                4: "knowledge context available", 5: "experience context available",
                6: "learning context available", 7: "adaptation ready", 8: "evolution evaluated",
            }
            for layer in payload["layers"]:
                layer["status"] = statuses.get(layer["number"], layer["status"])

            current = code
            results: list[dict[str, Any]] = []
            if self.path in {"/api/run", "/api/chat"}:
                for step in plan.steps:
                    template = next((c for c in REGISTRY.list_all_capabilities()
                                     if c.id == step["capability_id"]), None)
                    if template is None:
                        raise BrainError(f"Capability {step['capability_id']} is unavailable")
                    result = load_entry_point(template)(CapabilityContext(
                        code=current, language=language, file_path=filename, project_path="",
                        parameters={"llm_provider": brain.llm.provider, "llm_model": model,
                                    "llm_timeout_seconds": brain.timeout_seconds},
                        metadata={"request": request, "brain_reason": step.get("reason", ""),
                                  "conversation": conversation},
                    ))
                    results.append({"id": template.id, "name": template.name,
                                   "status": "completed" if result.success else "failed",
                                   "summary": result.summary, "error": result.error,
                                   "reason": step.get("reason", "")})
                    if not result.success:
                        break
                    if result.modified_code is not None:
                        current = result.modified_code
                payload["capability_results"] = results
                payload["output_code"] = current
                payload["diff"] = diff_text(code, current, filename)
                payload["layers"][8]["status"] = "verification preview complete"
                payload["layers"][1]["status"] = "governance preview"
                payload["layers"][9]["status"] = "execution preview — controlled action boundary"
                payload["assistant_message"] = assistant_summary(
                    plan.intent, plan.reasoning, results, current != code
                )

            payload["conversation"] = [*conversation[-12:],
                                       {"role": "user", "content": request},
                                       {"role": "assistant", "content": payload["assistant_message"]}]
            self._send(200, payload)
        except BrainError as exc:
            self._send(422, {"error": str(exc)})
        except Exception as exc:
            self._send(500, {"error": f"SPS-CA request failed: {exc}"})

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[SPS-CA] {fmt % args}")


def main() -> None:
    host, port = "127.0.0.1", 8080
    print(f"SPS-CA dashboard: http://{host}:{port}")
    print("Conversational mode: enabled")
    print("Brain: Ollama (provider-neutral interface)")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
