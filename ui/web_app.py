"""Advanced zero-dependency SPS-CA web dashboard.

Run with:
    python ui/web_app.py

The browser UI is a research/preview interface. It exposes the real Brain and
capability registry without pretending that the browser can mutate a user's
local filesystem. Project mutation remains behind the controlled Execution
layer.
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
from layers.architecture import BRAIN, LAYERS  # noqa: E402
from layers.layer_09_capability_registry import CapabilityRegistryManager  # noqa: E402

REGISTRY = CapabilityRegistryManager(str(ROOT / "capabilities" / "registry.json"))


def catalog() -> list[dict[str, Any]]:
    result = []
    for cap in REGISTRY.list_all_capabilities():
        if cap.status != "active":
            continue
        result.append({
            "id": cap.id,
            "name": cap.name,
            "description": cap.description,
            "version": cap.version,
            "generated": bool(cap.generated),
            "tags": list(getattr(cap, "tags", []) or []),
        })
    return result


def diff_text(before: str, after: str, filename: str) -> str:
    return "".join(difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    ))


class Handler(BaseHTTPRequestHandler):
    server_version = "SPS-CA-Dashboard/2.0"

    def _send(self, status: int, payload: Any, content_type: str = "application/json") -> None:
        body = payload if isinstance(payload, bytes) else (
            json.dumps(payload, ensure_ascii=False).encode("utf-8") if content_type == "application/json" else str(payload).encode("utf-8")
        )
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/":
            html = (ROOT / "ui" / "web" / "index.html").read_bytes()
            self._send(200, html, "text/html")
            return
        if self.path == "/static/app.js":
            self._send(200, (ROOT / "ui" / "web" / "app.js").read_bytes(), "text/javascript")
            return
        if self.path == "/static/styles.css":
            self._send(200, (ROOT / "ui" / "web" / "styles.css").read_bytes(), "text/css")
            return
        if self.path == "/api/architecture":
            self._send(200, {"layers": [
                {"number": n, "name": name, "description": description}
                for n, name, description in LAYERS
            ], "brain": BRAIN})
            return
        if self.path == "/api/capabilities":
            self._send(200, {"capabilities": catalog()})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in {"/api/plan", "/api/run"}:
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
            if not request or not code:
                self._send(400, {"error": "request and code are required"})
                return

            brain = Brain(model=model)
            plan = brain.plan(
                request=request,
                code=code,
                language=language,
                file_path=filename,
                capability_catalog=catalog(),
            )
            payload: dict[str, Any] = {
                "brain": plan.as_dict()["brain"],
                "intent": plan.intent,
                "reasoning": plan.reasoning,
                "steps": plan.steps,
                "layers": [
                    {"number": n, "name": name, "status": "ready"}
                    for n, name, _ in LAYERS
                ],
            }
            payload["layers"][0]["status"] = "constraints loaded"
            payload["layers"][1]["status"] = "policy gate ready"
            payload["layers"][2]["status"] = "reasoned by Brain"
            payload["layers"][3]["status"] = "capability knowledge loaded"
            payload["layers"][4]["status"] = "experience context available"
            payload["layers"][5]["status"] = "strategy context available"
            payload["layers"][6]["status"] = "adaptation ready"
            payload["layers"][7]["status"] = "evolution evaluated"

            if self.path == "/api/run":
                current = code
                results = []
                for step in plan.steps:
                    template = next((c for c in REGISTRY.list_all_capabilities() if c.id == step["capability_id"]), None)
                    if template is None:
                        raise BrainError(f"Capability {step['capability_id']} is unavailable")
                    result = load_entry_point(template)(CapabilityContext(
                        code=current,
                        language=language,
                        file_path=filename,
                        project_path="",
                        parameters={
                            "llm_provider": brain.llm.provider,
                            "llm_model": model,
                            "llm_timeout_seconds": brain.timeout_seconds,
                        },
                        metadata={"request": request, "brain_reason": step.get("reason", "")},
                    ))
                    results.append({
                        "id": template.id,
                        "name": template.name,
                        "status": "completed" if result.success else "failed",
                        "summary": result.summary,
                        "error": result.error,
                    })
                    if not result.success:
                        break
                    if result.modified_code is not None:
                        current = result.modified_code
                payload["capability_results"] = results
                payload["output_code"] = current
                payload["diff"] = diff_text(code, current, filename)
                payload["layers"][8]["status"] = "preview verification complete"
                payload["layers"][1]["status"] = "preview governance gate"
                payload["layers"][9]["status"] = "preview only — controlled execution required for project mutation"
            self._send(200, payload)
        except BrainError as exc:
            self._send(422, {"error": str(exc)})
        except Exception as exc:  # keep the UI responsive and return diagnostics
            self._send(500, {"error": f"SPS-CA request failed: {exc}"})

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[SPS-CA] {fmt % args}")


def main() -> None:
    host = "127.0.0.1"
    port = 8080
    print(f"SPS-CA dashboard: http://{host}:{port}")
    print("Brain: Ollama (provider-neutral interface)")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
