"""SPS-CA web UI.

Presentation-only layer built with Gradio. All SPS behavior remains in the
existing ten layers and supervisor services.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import gradio as gr

from layers.layer_09_capability_registry import CapabilityRegistryManager
from experience.evolution_trace import EvolutionTraceStore
from .supervisor_execution import SupervisorExecutionService


def _read_uploaded_file(uploaded: Any) -> tuple[str, str]:
    if uploaded is None:
        return "", ""
    path = getattr(uploaded, "name", uploaded)
    path = Path(path)
    try:
        return path.name, path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"Unable to read uploaded source file: {exc}") from exc


def _run_supervisor(
    request: str,
    code: str,
    language: str,
    uploaded: Optional[Any],
    target_project: str,
) -> tuple[str, str, str, str, str]:
    request = (request or "").strip()
    language = (language or "python").strip().lower()
    code = code or ""
    target_project = (target_project or "").strip()

    uploaded_name = ""
    if uploaded is not None:
        uploaded_name, uploaded_code = _read_uploaded_file(uploaded)
        code = uploaded_code

    if not request:
        raise gr.Error("Enter a coding request first.")
    if not code.strip():
        raise gr.Error("Paste code or upload a source file.")

    service = SupervisorExecutionService()
    result = service.run_submission(
        user_request=request,
        code=code,
        language=language,
        file_path=uploaded_name,
        target_project=target_project or None,
    )

    trace_path = Path("experience/traces/evolution_history.json")
    stage_path = Path("experience/traces/stage_state.json")
    registry_path = Path("capabilities/registry.json")

    result_text = json.dumps(result, indent=2, default=str)
    modified = result.get("modified_code", code)
    summary = (
        f"Scenario: {result.get('scenario_id', '-') }\n"
        f"Stage: {result.get('stage_before', '-') } → {result.get('stage_after', '-') }\n"
        f"Capability: {result.get('capability_id', '-') }\n"
        f"Generated: {result.get('generated', False)}\n"
        f"Validation: {result.get('validation', '-') }\n"
        f"Governance: {result.get('governance', '-') }\n"
        f"Execution: {result.get('execution', '-') }\n"
        f"Success: {result.get('success', False)}"
    )

    trace = {}
    if trace_path.exists():
        try:
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            trace = {"error": "Trace JSON could not be parsed."}

    registry = {}
    if registry_path.exists():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            registry = {"error": "Registry JSON could not be parsed."}

    stage = ""
    if stage_path.exists():
        try:
            stage = stage_path.read_text(encoding="utf-8")
        except OSError:
            stage = ""

    return summary, modified, result_text, json.dumps(trace, indent=2), json.dumps(registry, indent=2) + (f"\n\nStage state:\n{stage}" if stage else "")


def build_app() -> gr.Blocks:
    with gr.Blocks(title="SPS-CA — Self-Programming Code Assistant") as app:
        gr.Markdown(
            """
# SPS-CA
### Self-Programming Code Assistant

**Prompt → Analyze → Find Capability → Grow Capability → Modify → Validate → Govern → Execute → Learn**

The interface is only the presentation layer. The ten SPS layers remain unchanged.
"""
        )

        with gr.Row():
            with gr.Column(scale=5):
                request = gr.Textbox(
                    label="What should SPS-CA do?",
                    placeholder="Example: add input validation to this function",
                    lines=3,
                )
                language = gr.Dropdown(
                    ["python", "java", "javascript", "typescript", "go", "csharp"],
                    value="python",
                    label="Language",
                )
                code = gr.Code(
                    label="Source Code",
                    language="python",
                    lines=18,
                )
                upload = gr.File(
                    label="Or upload a source file",
                    file_count="single",
                )
                target_project = gr.Textbox(
                    label="Target project directory (optional)",
                    placeholder="Leave empty to use a safe SPS workspace",
                )
                run = gr.Button("Run SPS Supervisor", variant="primary")

            with gr.Column(scale=5):
                status = gr.Textbox(label="Supervisor Result", lines=10)
                modified = gr.Code(label="Modified Code", language="python", lines=18)

        with gr.Accordion("Research Trace", open=False):
            raw_result = gr.Code(label="Scenario Result JSON", language="json", lines=12)
            trace = gr.Code(label="Evolution History", language="json", lines=16)
            registry = gr.Code(label="Capability Registry", language="json", lines=16)

        def language_changed(lang: str):
            return gr.Code(language=lang or "python")

        language.change(language_changed, inputs=language, outputs=code)
        run.click(
            _run_supervisor,
            inputs=[request, code, language, upload, target_project],
            outputs=[status, modified, raw_result, trace, registry],
        )

    return app


def launch(*, share: Optional[bool] = None, auth: Optional[Any] = None, debug: bool = False):
    """Launch the SPS-CA web UI; Colab can use the generated share link."""
    app = build_app()
    if share is None:
        # Gradio's notebook/Colab behavior can create a share link automatically.
        share = os.getenv("GRADIO_SHARE", "").lower() in {"1", "true", "yes"}
    return app.launch(share=share, auth=auth, debug=debug)


if __name__ == "__main__":
    launch()
