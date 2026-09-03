"""Run a JSON-defined SPS-CA scenario suite and persist every result."""
from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.assistant_service import SpsAssistantService
from layers.layer_08_evolution.evolution_evidence import EvolutionEvidenceStore

DEFAULT_SUITE = "evaluation/scenarios/default_120.json"
DEFAULT_RESULTS_DIR = "evaluation/results/scenario_runs"
REGISTRY_PATH = "capabilities/registry.json"
EVOLUTION_PATH = "runtime/evolution_events.json"


def expand_suite(data: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = list(data.get("scenarios", []))
    for group in data.get("groups", []):
        template = str(group.get("template", ""))
        variants = list(group.get("variants", []))
        base_expected = dict(group.get("expected", {}))
        for index, variant in enumerate(variants, 1):
            if isinstance(variant, dict):
                request = str(variant.get("request", ""))
                if "{variant}" in template:
                    request = template.format(variant=variant.get("variant", request))
                expected = {**base_expected, **dict(variant.get("expected", {}))}
                code = str(variant.get("code", group.get("code", "")))
                language = str(variant.get("language", group.get("language", "python")))
                filename = str(variant.get("filename", group.get("filename", "main.py")))
                feedback = variant.get("feedback", group.get("feedback"))
            else:
                value = str(variant)
                request = template.format(variant=value)
                expected = base_expected
                code = str(group.get("code", ""))
                language = str(group.get("language", "python"))
                filename = str(group.get("filename", "main.py"))
                feedback = group.get("feedback")
            scenarios.append({
                "id": f"{group.get('id', 'group')}-{index:03d}",
                "request": request,
                "code": code,
                "language": language,
                "filename": filename,
                "expected": expected,
                "feedback": feedback,
            })
    return scenarios


def _match_expected(turn: Any, expected: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    intent = str(turn.intent or "")
    capability_ids = [str(x.get("capability_id") or x.get("id") or "") for x in turn.capability_results]
    status = "success" if turn.success else ("blocked" if "blocked" in str(turn.trace.get("status", "")) else "failure")
    expected_intent = expected.get("intent")
    if expected_intent and intent != expected_intent:
        failures.append(f"intent={intent!r}, expected={expected_intent!r}")
    expected_capability = expected.get("capability_id")
    if expected_capability and expected_capability not in capability_ids:
        failures.append(f"capability={capability_ids!r}, expected={expected_capability!r}")
    expected_status = expected.get("status")
    if expected_status and status != expected_status:
        failures.append(f"status={status!r}, expected={expected_status!r}")
    for fragment in expected.get("output_contains", []) or []:
        if str(fragment) not in str(turn.output_code or ""):
            failures.append(f"output missing {fragment!r}")
    if expected.get("output_required") and not str(turn.output_code or "").strip():
        failures.append("output_code is empty")
    return (not failures, failures)


def _record_feedback(evolution: EvolutionEvidenceStore, result: dict[str, Any], feedback: str | None) -> None:
    if feedback not in {"agree", "disagree"}:
        return
    common = {
        "session_id": result["run_id"],
        "turn_id": result["index"],
        "request": result["request"],
        "language": result["language"],
        "capability_id": result["capability_id"],
        "code": result.get("output_code", ""),
    }
    if feedback == "agree":
        evolution.record_agreement(**common)
        return
    event = evolution.record_disagreement(
        session_id=common["session_id"], turn_id=common["turn_id"], request=common["request"],
        language=common["language"], language_confidence=float(result.get("language_confidence", 0.0)),
        previous_capability_id=common["capability_id"], code=common["code"],
    )
    analysis = evolution.analyze(event)
    if analysis.get("decision") == "create":
        evolution.record_creation(analysis)


def run_suite(path: str | Path, *, model: str = "", live_evolve: bool = False, max_scenarios: int | None = None, results_dir: str | Path = DEFAULT_RESULTS_DIR) -> dict[str, Any]:
    suite_path = Path(path)
    data = json.loads(suite_path.read_text(encoding="utf-8"))
    scenarios = expand_suite(data)
    if max_scenarios is not None:
        scenarios = scenarios[:max(0, max_scenarios)]
    if live_evolve:
        os.environ["SPS_CA_AUTO_EVOLVE"] = "true"
    else:
        os.environ.setdefault("SPS_CA_AUTO_EVOLVE", "false")

    run_id = f"suite_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:6]}"
    root = Path(results_dir)
    root.mkdir(parents=True, exist_ok=True)
    output = {
        "run_id": run_id,
        "suite": str(suite_path),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "live_evolution": live_evolve,
        "total": len(scenarios),
        "passed": 0,
        "failed": 0,
        "scenarios": [],
    }
    evolution = EvolutionEvidenceStore(EVOLUTION_PATH, REGISTRY_PATH)
    for index, scenario in enumerate(scenarios, 1):
        request = str(scenario.get("request", "")).strip()
        service = SpsAssistantService(registry_path=REGISTRY_PATH, model=model)
        start = time.monotonic()
        turn = service.run_turn(
            request=request,
            code=str(scenario.get("code", "")),
            language=str(scenario.get("language", "python")),
            filename=str(scenario.get("filename", "main.py")),
            conversation=[],
        )
        passed, failures = _match_expected(turn, dict(scenario.get("expected", {})))
        capability_id = (turn.capability_results[-1].get("capability_id") if turn.capability_results else "")
        result = {
            "run_id": run_id,
            "index": index,
            "scenario_id": str(scenario.get("id", f"scenario-{index:03d}")),
            "request": request,
            "language": str(scenario.get("language", "python")),
            "filename": str(scenario.get("filename", "main.py")),
            "expected": scenario.get("expected", {}),
            "actual": {
                "intent": turn.intent,
                "capability_id": capability_id,
                "status": "success" if turn.success else "failure",
                "elapsed_ms": turn.elapsed_ms,
            },
            "passed": passed,
            "assertion_failures": failures,
            "output_code": turn.output_code,
            "language_confidence": float((turn.brain or {}).get("language_confidence", 0.0) or 0.0),
            "trace": turn.trace,
            "learning_context": turn.learning_context,
        }
        _record_feedback(evolution, result, scenario.get("feedback"))
        output["scenarios"].append(result)
        if passed:
            output["passed"] += 1
        else:
            output["failed"] += 1
        (root / f"{run_id}.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[{index:03d}/{len(scenarios):03d}] {'PASS' if passed else 'FAIL'} {result['scenario_id']} · {turn.intent or 'unknown'} · {capability_id or 'none'}")

    output["finished_at"] = datetime.now(timezone.utc).isoformat()
    output["pass_rate"] = round(output["passed"] / output["total"], 4) if output["total"] else 0.0
    latest = root / "latest.json"
    latest.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SPS-CA JSON scenario suite")
    parser.add_argument("--file", default=DEFAULT_SUITE)
    parser.add_argument("--model", default="")
    parser.add_argument("--live-evolve", action="store_true", help="Allow threshold-triggered Evolution actions")
    parser.add_argument("--max-scenarios", type=int, default=None)
    parser.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR)
    args = parser.parse_args()
    result = run_suite(args.file, model=args.model, live_evolve=args.live_evolve, max_scenarios=args.max_scenarios, results_dir=args.results_dir)
    print(json.dumps({"run_id": result["run_id"], "total": result["total"], "passed": result["passed"], "failed": result["failed"], "pass_rate": result["pass_rate"]}, indent=2))
    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
