"""SPS-CA research dashboard web UI.

Presentation-only Gradio application. The canonical SPS pipeline remains the
system of record; this module presents its ten-layer trace, Brain boundary,
capability state, feedback, and evolution history.
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import gradio as gr
import pandas as pd
import plotly.graph_objects as go

from core.canonical_sps_pipeline import CanonicalSPSPipeline
from layers.architecture import architecture_manifest

LANGUAGES = ["python", "java", "javascript", "typescript", "go", "csharp"]
LAYERS = architecture_manifest()["layers"]


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return default


def _state() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    registry = _read_json(REPO_ROOT / "capabilities/registry.json", {})
    trace = _read_json(REPO_ROOT / "experience/traces/evolution_history.json", [])
    stage = _read_json(REPO_ROOT / "experience/traces/stage_state.json", {"current_stage": 0})
    return registry, trace if isinstance(trace, list) else [], stage


def _capabilities(registry: dict[str, Any]) -> list[dict[str, Any]]:
    caps = registry.get("capabilities", [])
    return caps if isinstance(caps, list) else []


def _metrics() -> dict[str, Any]:
    registry, records, stage = _state()
    caps = _capabilities(registry)
    generated = sum(1 for cap in caps if cap.get("generated"))
    reused = sum(int(cap.get("reuse_count", 0) or 0) for cap in caps)
    completed = sum(1 for record in records if record.get("status") == "completed")
    successful = sum(1 for record in records if record.get("result", {}).get("success") is True)
    return {
        "stage": int(stage.get("current_stage", 0) or 0),
        "capabilities": len(caps),
        "generated": generated,
        "reused": reused,
        "scenarios": len(records),
        "success_rate": (successful / completed * 100.0) if completed else 0.0,
        "rollbacks": sum(1 for record in records if record.get("result", {}).get("rollback_triggered")),
    }


def _kpi_html(metrics: dict[str, Any]) -> str:
    cards = [
        ("CURRENT STAGE", metrics["stage"]),
        ("CAPABILITIES", metrics["capabilities"]),
        ("GENERATED", metrics["generated"]),
        ("REUSE EVENTS", metrics["reused"]),
        ("SCENARIOS", metrics["scenarios"]),
        ("SUCCESS RATE", f"{metrics['success_rate']:.1f}%"),
    ]
    inner = "".join(
        f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>'
        for label, value in cards
    )
    return f"<div class='kpi-grid'>{inner}</div>"


def _growth_figure() -> go.Figure:
    _, records, _ = _state()
    scenarios = []
    capability_count = 0
    generated_count = 0
    counts = []
    generated = []
    for index, record in enumerate(records, start=1):
        generation = record.get("capability_generation", {}) or {}
        if generation.get("registered"):
            capability_count += 1
            generated_count += 1
        scenarios.append(index)
        counts.append(capability_count)
        generated.append(generated_count)
    fig = go.Figure()
    if scenarios:
        fig.add_trace(go.Scatter(x=scenarios, y=counts, mode="lines+markers", name="Capabilities introduced"))
        fig.add_trace(go.Scatter(x=scenarios, y=generated, mode="lines+markers", name="Generated capabilities"))
    else:
        fig.add_trace(go.Bar(x=["Current"], y=[0], name="Capabilities"))
    fig.update_layout(height=360, margin=dict(l=20, r=20, t=45, b=20), title="Capability growth by scenario", xaxis_title="Scenario", yaxis_title="Count", template="plotly_white")
    return fig


def _reuse_figure() -> go.Figure:
    registry, _, _ = _state()
    caps = sorted(_capabilities(registry), key=lambda cap: int(cap.get("reuse_count", 0) or 0), reverse=True)[:12]
    fig = go.Figure(go.Bar(x=[cap.get("id", "?") for cap in caps], y=[int(cap.get("reuse_count", 0) or 0) for cap in caps]))
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=45, b=20), title="Capability reuse", xaxis_title="Capability", yaxis_title="Reuse count", template="plotly_white")
    return fig


def _capability_table() -> pd.DataFrame:
    registry, _, _ = _state()
    rows = []
    for cap in _capabilities(registry):
        rows.append({
            "ID": cap.get("id", ""),
            "Name": cap.get("name", ""),
            "Type": cap.get("type", ""),
            "Origin": "Generated" if cap.get("generated") else cap.get("origin", "Seed"),
            "Version": cap.get("version", ""),
            "Reuse": cap.get("reuse_count", 0),
            "Coverage": cap.get("test_coverage", 0.0),
            "Status": cap.get("status", ""),
        })
    return pd.DataFrame(rows, columns=["ID", "Name", "Type", "Origin", "Version", "Reuse", "Coverage", "Status"])


def _evolution_table() -> pd.DataFrame:
    _, records, _ = _state()
    rows = []
    for record in reversed(records):
        generation = record.get("capability_generation", {}) or {}
        search = record.get("capability_search", {}) or {}
        result = record.get("result", {}) or {}
        rows.append({
            "Scenario": record.get("scenario_id", ""),
            "Stage": f"{record.get('stage_before', 0)} → {record.get('stage_after', 0)}",
            "Status": record.get("status", ""),
            "Request": record.get("user_request", ""),
            "Capability": search.get("selected") or generation.get("capability_id", ""),
            "Generated": bool(generation.get("required")),
            "Result": result.get("status", result.get("success", "")),
        })
    return pd.DataFrame(rows, columns=["Scenario", "Stage", "Status", "Request", "Capability", "Generated", "Result"])


def _scenario_detail(scenario_id: str) -> str:
    _, records, _ = _state()
    matches = [record for record in records if record.get("scenario_id") == scenario_id.strip()]
    if not matches:
        return "Select a scenario ID from the Evolution table."
    return json.dumps(matches[-1], indent=2, ensure_ascii=False, default=str)


def _layer_html(pipeline: Optional[dict[str, Any]] = None) -> str:
    layers = (pipeline or {}).get("layers") if pipeline else None
    if not layers:
        layers = [
            {
                "number": item["number"],
                "name": item["name"],
                "status": "ready",
                "component": "",
                "artifact": "",
                "detail": item.get("purpose", ""),
            }
            for item in LAYERS
        ]
    items = []
    for item in layers:
        component = f" · {item.get('component')}" if item.get("component") else ""
        artifact = f"<div class='layer-artifact'>{item.get('artifact', '')}</div>" if item.get("artifact") else ""
        items.append(
            f'<div class="layer-row"><span class="layer-num">L{int(item.get("number", 0)):02d}</span>'
            f'<div><div class="layer-name">{item.get("name", "")} <span class="layer-status">{item.get("status", "")}</span></div>'
            f'<div class="layer-component">{component.lstrip(" ·")}</div>{artifact}'
            f'<div class="layer-detail">{item.get("detail", "")}</div></div></div>'
        )
    return "<div class='layer-list'>" + "".join(items) + "</div>"


def _experiment_table() -> pd.DataFrame:
    rows = []
    source = REPO_ROOT / "evaluation/scenarios.py"
    if source.exists():
        for line in source.read_text(encoding="utf-8").splitlines():
            text = line.strip()
            if text.startswith('{"id":'):
                rows.append({"Scenario": text.split('"id":', 1)[1].split(',', 1)[0].strip(' \"'), "Definition": text})
    return pd.DataFrame(rows or [{"Scenario": "S1–S25", "Definition": "See evaluation/scenarios.py"}])


def _guide_markdown() -> str:
    return """
# SPS-CA Run Guide

## Canonical user flow

1. **User** provides a prompt and source code or an uploaded file.
2. **Brain / Cognitive** understand the task, infer intent, and reason about the requested change.
3. **Knowledge / Experience / Meta-Learning / Adaptation** provide structured context and reuse evidence.
4. **Evolution** either reuses a registered capability or creates a new candidate when a governed capability gap exists.
5. **Validation** tests the proposed change in a sandbox.
6. **Governance** authorizes the proposed change.
7. **Software DNA** performs the final non-bypassable safety check.
8. **Execution** applies the approved change using a rollback-capable execution boundary.
9. The resulting outcome is persisted as trace/experience evidence for future learning.

The browser UI and model-backed scenario runner both call the same `CanonicalSPSPipeline` entry point.

## Google Colab

Use the Colab notebook to install requirements, prepare Ollama, choose and pull a model, run the deterministic routing contract, and run the model-backed ten-layer experiment.
"""


def _read_uploaded_file(uploaded: Any) -> tuple[str, str]:
    if uploaded is None:
        return "", ""
    path = Path(getattr(uploaded, "name", uploaded))
    try:
        return path.name, path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"Unable to read uploaded source file: {exc}") from exc


def _run_sps(request: str, code: str, language: str, uploaded: Optional[Any], target_project: str):
    request = (request or "").strip()
    code = code or ""
    language = (language or "python").strip().lower()
    target_project = (target_project or "").strip()
    uploaded_name = ""
    if uploaded is not None:
        uploaded_name, code = _read_uploaded_file(uploaded)
    if not request:
        raise gr.Error("Enter a coding request first.")
    if not code.strip():
        raise gr.Error("Paste code or upload a source file.")
    if language == "python":
        code = textwrap.dedent(code)
    result = CanonicalSPSPipeline().run_submission(
        user_request=request,
        code=code,
        language=language,
        file_path=uploaded_name,
        target_project=target_project or None,
    )
    modified = result.get("modified_code", code)
    brain = result.get("brain", {})
    summary = (
        f"Scenario {result.get('scenario_id', '-')}  |  Stage {result.get('stage_before', '-')} → {result.get('stage_after', '-')}\n"
        f"Brain: {brain.get('component', 'SPS-CA Brain')}  |  Intent: {brain.get('intent_signal', '-')}\n"
        f"Capability: {result.get('capability_id', '-')}  |  Generated: {result.get('generated', False)}\n"
        f"Validation: {result.get('validation', '-')}  |  Governance: {result.get('governance', '-')}  |  DNA: {(result.get('dna') or {}).get('allowed', '-')}  |  Execution: {result.get('execution', '-')}\n"
        f"Success: {result.get('success', False)}"
    )
    return summary, modified, json.dumps(result, indent=2, default=str), _layer_html(result.get("pipeline")), _kpi_html(_metrics()), _growth_figure(), _reuse_figure(), _capability_table(), _evolution_table()


def _refresh_dashboard():
    return _kpi_html(_metrics()), _growth_figure(), _reuse_figure(), _capability_table(), _evolution_table(), _layer_html()


def build_app() -> gr.Blocks:
    css = """
    .app-shell {max-width: 1500px !important; margin: auto;}
    .hero {padding: 8px 0 12px 0;}
    .hero h1 {font-size: 34px; margin-bottom: 4px;}
    .hero p {font-size: 15px; opacity: .78;}
    .kpi-grid {display:grid; grid-template-columns:repeat(6,minmax(110px,1fr)); gap:10px; margin:6px 0 16px;}
    .kpi {border:1px solid #ddd; border-radius:14px; padding:14px; background:rgba(255,255,255,.03);}
    .kpi-label {font-size:11px; letter-spacing:.08em; opacity:.65;}
    .kpi-value {font-size:26px; font-weight:700; margin-top:4px;}
    .layer-list {display:grid; gap:8px; margin-top:12px;}
    .layer-row {display:flex; gap:12px; align-items:flex-start; border:1px solid #ddd; border-radius:10px; padding:10px 12px;}
    .layer-num {font-family:monospace; opacity:.65; width:30px; padding-top:2px;}
    .layer-name {font-weight:700;}
    .layer-status {font-size:11px; margin-left:6px; opacity:.65; text-transform:uppercase;}
    .layer-component {font-size:12px; margin-top:3px; opacity:.8;}
    .layer-artifact {font-family:monospace; font-size:11px; margin-top:4px; opacity:.8;}
    .layer-detail {font-size:12px; margin-top:4px; opacity:.7;}
    @media(max-width:900px){.kpi-grid{grid-template-columns:repeat(3,minmax(100px,1fr));}}
    """
    with gr.Blocks(css=css, title="SPS-CA Research Dashboard") as app:
        with gr.Column(elem_classes="app-shell"):
            gr.HTML("<div class='hero'><h1>SPS-CA Research Dashboard</h1><p>Self-Programming Code Assistant · governed · traceable · reversible · research instrument</p></div>")
            kpis = gr.HTML(_kpi_html(_metrics()))
            refresh = gr.Button("Refresh Research Data", size="sm")

            with gr.Tabs():
                with gr.Tab("🧠 SPS-CA"):
                    with gr.Row():
                        with gr.Column(scale=5):
                            request = gr.Textbox(label="Task / Prompt", placeholder="Tell SPS-CA what should change…", lines=4)
                            with gr.Row():
                                language = gr.Dropdown(LANGUAGES, value="python", label="Language", scale=2)
                                upload = gr.File(label="Upload code", file_count="single", scale=2)
                            code = gr.Code(label="Source Code", language="python", lines=22)
                            target = gr.Textbox(label="Target project directory (optional)", placeholder="Leave empty for a safe SPS workspace")
                            run = gr.Button("Run SPS-CA", variant="primary")
                        with gr.Column(scale=5):
                            result_status = gr.Textbox(label="Execution Summary", lines=6)
                            layer_run_view = gr.HTML(_layer_html())
                            modified = gr.Code(label="Modified Code", language="python", lines=22)
                            result_json = gr.Code(label="Canonical Pipeline Result", language="json", lines=14)

                with gr.Tab("🧩 Capabilities"):
                    gr.Markdown("### Capability Registry")
                    cap_table = gr.Dataframe(value=_capability_table(), interactive=False, wrap=True)
                    gr.Markdown("Generated capabilities are first-class research artifacts with provenance, versioning, tests, and reuse history.")

                with gr.Tab("📈 Growth"):
                    with gr.Row():
                        growth_plot = gr.Plot(_growth_figure(), label="Capability Growth")
                        reuse_plot = gr.Plot(_reuse_figure(), label="Capability Reuse")
                    gr.Markdown("### Canonical Ten-Layer Architecture")
                    layer_view = gr.HTML(_layer_html())

                with gr.Tab("🔄 Evolution"):
                    evo_table = gr.Dataframe(value=_evolution_table(), interactive=False, wrap=True)
                    scenario_id = gr.Textbox(label="Scenario ID", placeholder="SC-001")
                    inspect = gr.Button("Inspect Scenario")
                    scenario_detail = gr.Code(label="WHY / WHAT / WHEN / HOW trace", language="json", lines=18)

                with gr.Tab("🧪 Experiments"):
                    gr.Markdown("### Reproducible Evaluation Catalog")
                    gr.Dataframe(value=_experiment_table(), interactive=False, wrap=True)
                    gr.Markdown("The deterministic 500-case contract and model-backed scenario runner are separate research measurements but share the same canonical execution service.")

                with gr.Tab("📖 Guide"):
                    gr.Markdown(_guide_markdown())

            run.click(_run_sps, [request, code, language, upload, target], [result_status, modified, result_json, layer_run_view, kpis, growth_plot, reuse_plot, cap_table, evo_table])
            refresh.click(_refresh_dashboard, outputs=[kpis, growth_plot, reuse_plot, cap_table, evo_table, layer_view])
            inspect.click(_scenario_detail, inputs=scenario_id, outputs=scenario_detail)
            language.change(lambda lang: gr.Code(language=lang or "python"), inputs=language, outputs=code)

    return app


def _running_in_colab() -> bool:
    try:
        import google.colab  # type: ignore  # noqa: F401
        return True
    except ImportError:
        return False


def launch(*, share: Optional[bool] = None, auth: Optional[Any] = None, debug: bool = False):
    """Launch the dashboard; Colab uses a share link by default."""
    app = build_app()
    if share is None:
        share = _running_in_colab()
    return app.launch(share=share, auth=auth, debug=debug)


if __name__ == "__main__":
    launch()
