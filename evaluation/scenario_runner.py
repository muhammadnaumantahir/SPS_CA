"""Run a JSON-defined SPS-CA scenario suite through the canonical SPS pipeline."""
from __future__ import annotations

import argparse
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical_sps_pipeline import CanonicalSPSPipeline
from layers.layer_08_evolution.evolution_evidence import EvolutionEvidenceStore

DEFAULT_SUITE = "evaluation/scenarios/default_120.json"
DEFAULT_RESULTS_DIR = "evaluation/results/scenario_runs"
REGISTRY_PATH = "capabilities/registry.json"
EVOLUTION_PATH = "runtime/evolution_events.json"


def expand_suite(data: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = list(data.get("scenarios", []))
    for group in data.get("groups", []):
        template = str(group.get("template", "")); variants = list(group.get("variants", [])); base_expected = dict(group.get("expected", {}))
        for index, variant in enumerate(variants, 1):
            if isinstance(variant, dict):
                request = str(variant.get("request", ""))
                if "{variant}" in template: request = template.format(variant=variant.get("variant", request))
                expected = {**base_expected, **dict(variant.get("expected", {}))}
                code = str(variant.get("code", group.get("code", ""))); language = str(variant.get("language", group.get("language", "python"))); filename = str(variant.get("filename", group.get("filename", "main.py"))); feedback = variant.get("feedback", group.get("feedback"))
            else:
                value = str(variant); request = template.format(variant=value); expected = base_expected; code = str(group.get("code", "")); language = str(group.get("language", "python")); filename = str(group.get("filename", "main.py")); feedback = group.get("feedback")
            scenarios.append({"id": f"{group.get('id', 'group')}-{index:03d}", "request": request, "code": code, "language": language, "filename": filename, "expected": expected, "feedback": feedback})
    return scenarios


def _growth_evidence_from_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """Translate observable scenario evidence into Layer-8 scoring inputs."""
    request = str(scenario.get("request", "")); context = scenario.get("context") or {}; evidence_text = str(context.get("evidence", "")); text = f"{request} {evidence_text}".lower()
    if "cannot satisfy" in text or "no capability" in text or "no reusable capability" in text:
        return {"capability_match": False, "capability_fitness": 10.0, "recurrence_score": 80.0, "confidence_score": 95.0, "creation_need": 95.0, "regression_risk": 5.0, "evidence_summary": evidence_text or request}
    if "existing generated" in text or "existing capability has this weakness" in text:
        return {"capability_match": True, "capability_fitness": 35.0, "recurrence_score": 70.0, "confidence_score": 90.0, "improvement_viability": 90.0, "regression_risk": 10.0, "evidence_summary": evidence_text or request}
    if "environmental mismatch" in text or "production input now" in text or "adapt processing" in text:
        return {"capability_match": True, "capability_fitness": 60.0, "recurrence_score": 70.0, "confidence_score": 85.0, "adaptation_viability": 90.0, "regression_risk": 10.0, "evidence_summary": evidence_text or request}
    if "requires coordinated" in text or "compose" in text or "dependent" in text:
        return {"capability_match": True, "capability_fitness": 80.0, "recurrence_score": 65.0, "confidence_score": 90.0, "composition_viability": 90.0, "regression_risk": 10.0, "evidence_summary": evidence_text or request}
    return {"capability_match": True, "capability_fitness": 50.0, "recurrence_score": 60.0, "confidence_score": 80.0, "evidence_summary": evidence_text or request}


def _match_expected(result: dict[str, Any], expected: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []; actual = result.get("actual", {}); intent = str(actual.get("intent") or ""); capability_ids = list(actual.get("capability_ids") or ([] if not actual.get("capability_id") else [actual.get("capability_id")])); status = str(actual.get("status") or "failure")
    if expected.get("intent") and intent != expected["intent"]: failures.append(f"intent={intent!r}, expected={expected['intent']!r}")
    if expected.get("capability_id") and expected["capability_id"] not in capability_ids: failures.append(f"capability={capability_ids!r}, expected={expected['capability_id']!r}")
    if expected.get("status") and status != expected["status"]: failures.append(f"status={status!r}, expected={expected['status']!r}")
    for fragment in expected.get("output_contains", []) or []:
        if str(fragment) not in str(result.get("output_code", "")): failures.append(f"output missing {fragment!r}")
    if expected.get("output_required") and not str(result.get("output_code", "")).strip(): failures.append("output_code is empty")
    if expected.get("capability_creation_expected") and result.get("growth_decision") != "create": failures.append(f"growth_decision={result.get('growth_decision')!r}, expected='create'")
    return (not failures, failures)


def _record_feedback(evolution: EvolutionEvidenceStore, result: dict[str, Any], feedback: str | None, *, live_evolve: bool = False, model: str = "") -> None:
    if feedback not in {"agree", "disagree"}: return
    common = {"session_id": result["run_id"], "turn_id": result["index"], "request": result["request"], "language": result["language"], "capability_id": result["capability_id"], "code": result.get("output_code", "")}
    if feedback == "agree": evolution.record_agreement(**common); result["feedback_recorded"] = "agree"; return
    scenario = result.get("scenario") or {}; growth_metrics = _growth_evidence_from_scenario(scenario) if scenario.get("scenario_type") == "autonomous_evolution" else {}
    event = evolution.record_disagreement(**common, language_confidence=0.0, previous_capability_id=common["capability_id"], **growth_metrics)
    analysis = evolution.analyze(event)
    result["growth_decision"] = analysis.get("decision"); result["growth_reason_code"] = analysis.get("reason_code"); result["growth_reasoning"] = analysis.get("reasoning"); result["growth_scores"] = analysis.get("growth_decision", {}).get("scores", {})
    if analysis.get("decision") == "create" and live_evolve:
        from brain.ai_evolution import AIEvolutionEngine
        from layers.layer_02_governance import GovernanceGate
        from layers.layer_08_evolution import EvolutionEngine
        evolution_engine = EvolutionEngine(governance_gate=GovernanceGate(), generated_dir="capabilities/generated", seeds_dir="capabilities/seeds", registry_path=REGISTRY_PATH, evaluation_dir="evaluation/evolution")
        ai_evolution = AIEvolutionEngine(evolution_engine, model=model)
        existing = [{"id": c.id, "name": c.name, "description": c.description, "status": c.status} for c in evolution.registry.list_all_capabilities()]
        generated = ai_evolution.create_from_gap(gap=result["request"], language=result["language"], scenario_id=result["scenario_id"], existing_capabilities=existing, observations=[analysis])
        result["generated_capability_id"] = generated.get("capability_id"); result["generated_capability"] = generated; result["experience_creation_trigger"] = True


def _generated_capability_count() -> int:
    registry = Path(REGISTRY_PATH)
    if not registry.exists(): return 0
    try: data = json.loads(registry.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return 0
    return sum(1 for item in data.get("capabilities", []) if item.get("generated") and item.get("origin") != "historical_migration")


def run_suite(path: str | Path, *, model: str = "", live_evolve: bool = False, max_scenarios: int | None = None, results_dir: str | Path = DEFAULT_RESULTS_DIR, record_feedback: bool = True) -> dict[str, Any]:
    suite_path = Path(path); data = json.loads(suite_path.read_text(encoding="utf-8")); scenarios = expand_suite(data)
    if max_scenarios is not None: scenarios = scenarios[:max(0, max_scenarios)]
    os.environ["SPS_CA_AUTO_EVOLVE"] = "true" if live_evolve else "false"
    run_id = f"suite_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:6]}"; root = Path(results_dir); root.mkdir(parents=True, exist_ok=True)
    output: dict[str, Any] = {"run_id": run_id, "suite": str(suite_path), "started_at": datetime.now(timezone.utc).isoformat(), "live_evolution": live_evolve, "total": len(scenarios), "passed": 0, "failed": 0, "generated_capabilities_at_start": _generated_capability_count(), "growth_decisions": {}, "scenarios": []}
    evolution = EvolutionEvidenceStore(EVOLUTION_PATH, REGISTRY_PATH); pipeline = CanonicalSPSPipeline(registry_path=REGISTRY_PATH)
    for index, scenario in enumerate(scenarios, 1):
        request = str(scenario.get("request", "")).strip()
        turn = pipeline.run_submission(user_request=request, code=str(scenario.get("code", "")), language=str(scenario.get("language", "python")), file_path=str(scenario.get("filename", "main.py")), source="scenario", run_id=run_id)
        capability_id = str(turn.get("capability_id") or ""); dna = turn.get("dna") or {}; governance = str(turn.get("governance") or "")
        actual_status = "success" if turn.get("success") else ("blocked" if governance and governance.lower() not in {"auto_approved", "approved"} else ("blocked" if dna.get("allowed") is False else "failure"))
        result = {"run_id": run_id, "index": index, "scenario_id": str(scenario.get("id", f"scenario-{index:03d}")), "request": request, "language": str(scenario.get("language", "python")), "filename": str(scenario.get("filename", "main.py")), "scenario": scenario, "expected": scenario.get("expected", {}), "actual": {"intent": turn.get("brain", {}).get("intent_signal", ""), "capability_id": capability_id, "capability_ids": [capability_id] if capability_id else [], "status": actual_status, "elapsed_ms": turn.get("elapsed_ms")}, "passed": False, "assertion_failures": [], "output_code": turn.get("modified_code", str(scenario.get("code", ""))), "language_confidence": 0.0, "trace": turn.get("pipeline") or {}, "brain": turn.get("brain") or {}, "experience": turn.get("experience") or {}}
        if scenario.get("scenario_type") == "autonomous_evolution": result["growth_evidence"] = _growth_evidence_from_scenario(scenario)
        if record_feedback: _record_feedback(evolution, result, scenario.get("feedback"), live_evolve=live_evolve, model=model)
        decision = result.get("growth_decision")
        if decision: output["growth_decisions"][decision] = output["growth_decisions"].get(decision, 0) + 1
        if result.get("generated_capability_id"): result["actual"]["capability_ids"].append(result["generated_capability_id"])
        passed, failures = _match_expected(result, dict(scenario.get("expected", {}))); result["passed"] = passed; result["assertion_failures"] = failures
        output["scenarios"].append(result); output["passed"] += int(passed); output["failed"] += int(not passed)
        (root / f"{run_id}.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[{index:03d}/{len(scenarios):03d}] {'PASS' if passed else 'FAIL'} {result['scenario_id']} · {result['actual']['intent'] or 'unknown'} · {capability_id or 'none'} · growth={result.get('growth_decision', 'none')}")
    output["finished_at"] = datetime.now(timezone.utc).isoformat(); output["pass_rate"] = round(output["passed"] / output["total"], 4) if output["total"] else 0.0; output["generated_capabilities_at_end"] = _generated_capability_count(); output["evolution_events"] = len(evolution.list_events(200))
    (root / f"{run_id}.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"); (root / "latest.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"); return output


def run_measurement(path: str | Path, *, model: str = "", max_scenarios: int | None = None, results_dir: str | Path = DEFAULT_RESULTS_DIR) -> dict[str, Any]:
    measurement_id = f"measurement_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:6]}"; baseline = run_suite(path, model=model, live_evolve=False, max_scenarios=max_scenarios, results_dir=results_dir, record_feedback=False); evolved = run_suite(path, model=model, live_evolve=True, max_scenarios=max_scenarios, results_dir=results_dir, record_feedback=True)
    result = {"measurement_id": measurement_id, "created_at": datetime.now(timezone.utc).isoformat(), "suite": str(path), "baseline_run_id": baseline["run_id"], "evolved_run_id": evolved["run_id"], "baseline_pass_rate": baseline.get("pass_rate", 0.0), "evolved_pass_rate": evolved.get("pass_rate", 0.0), "pass_rate_delta": round(evolved.get("pass_rate", 0.0) - baseline.get("pass_rate", 0.0), 4), "generated_capability_delta": int(evolved.get("generated_capabilities_at_end", 0)) - int(baseline.get("generated_capabilities_at_start", 0)), "evolution_events_at_end": evolved.get("evolution_events", 0), "evidence": {"baseline": {"total": baseline.get("total", 0), "passed": baseline.get("passed", 0), "failed": baseline.get("failed", 0)}, "evolved": {"total": evolved.get("total", 0), "passed": evolved.get("passed", 0), "failed": evolved.get("failed", 0)}}}; root = Path(results_dir); root.mkdir(parents=True, exist_ok=True); (root / f"{measurement_id}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8"); (root / "latest_measurement.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8"); return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SPS-CA JSON scenario suite"); parser.add_argument("--file", default=DEFAULT_SUITE); parser.add_argument("--model", default=""); parser.add_argument("--live-evolve", action="store_true"); parser.add_argument("--measure-improvement", action="store_true"); parser.add_argument("--max-scenarios", type=int, default=None); parser.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR); args = parser.parse_args()
    if args.measure_improvement:
        result = run_measurement(args.file, model=args.model, max_scenarios=args.max_scenarios, results_dir=args.results_dir); print(json.dumps(result, indent=2)); return 0 if result["evolved_pass_rate"] >= result["baseline_pass_rate"] else 1
    result = run_suite(args.file, model=args.model, live_evolve=args.live_evolve, max_scenarios=args.max_scenarios, results_dir=args.results_dir); print(json.dumps({"run_id": result["run_id"], "total": result["total"], "passed": result["passed"], "failed": result["failed"], "pass_rate": result["pass_rate"], "growth_decisions": result.get("growth_decisions", {})}, indent=2)); return 0 if result["failed"] == 0 else 1


if __name__ == "__main__": raise SystemExit(main())
