"""Google Colab runner for the canonical SPS-CA scenario suite.

Run from Colab after cloning the repository. The default path executes the
single 500-case routing test file with live progress, then optionally runs the
model-backed growth suite so Layer-8 evidence is persisted for the dashboard.

Environment:
  SPS_CA_MODEL=qwen2.5-coder:7b        Ollama model for the growth run
  SPS_CA_RUN_GROWTH_E2E=true           also run the model-backed 500 scenarios
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(os.environ.get("SPS_CA_REPO", "/content/SPS_CA")).resolve()
SCENARIO_TEST = REPO / "testing" / "test_sps_scenarios.py"
SCENARIO_FILE = REPO / "evaluation" / "scenarios" / "growth_500.json"
METRICS_FILE = REPO / "test_metrics.json"
MODEL = os.environ.get("SPS_CA_MODEL", "qwen2.5-coder:7b")
RUN_GROWTH_E2E = os.environ.get("SPS_CA_RUN_GROWTH_E2E", "true").lower() in {"1", "true", "yes", "on"}

os.chdir(REPO)
sys.path.insert(0, str(REPO))


def run_command(command: list[str], *, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=REPO, text=True, capture_output=True, timeout=timeout)


def print_pytest_progress(output: str) -> tuple[int, int, int, list[str]]:
    total = passed = failed = skipped = 0
    failures: list[str] = []
    for line in output.splitlines():
        match = re.search(r"(PASSED|FAILED|SKIPPED).*::([^\s]+)$", line)
        if not match:
            continue
        status, test_name = match.groups()
        total += 1
        if status == "PASSED":
            passed += 1
            print(f"  ✓ [{total:03d}] {test_name} ... PASSED")
        elif status == "FAILED":
            failed += 1
            failures.append(test_name)
            print(f"  ✗ [{total:03d}] {test_name} ... FAILED")
        else:
            skipped += 1
            print(f"  ⊘ [{total:03d}] {test_name} ... SKIPPED")
    return total, passed, failed, skipped, failures


def load_capability_snapshot() -> dict:
    path = REPO / "capabilities" / "registry.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"capabilities": []}
    return data if isinstance(data, dict) else {"capabilities": []}


def load_growth_snapshot() -> dict:
    path = REPO / "runtime" / "evolution_events.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = []
    events = data if isinstance(data, list) else []
    return {
        "events": len(events),
        "agreements": sum(1 for event in events if event.get("event_type") == "agreement"),
        "disagreements": sum(1 for event in events if event.get("event_type") == "disagreement"),
        "creations": sum(1 for event in events if event.get("event_type") == "creation"),
    }


def run_500_contract_tests() -> dict:
    print("\n" + "=" * 75)
    print("SPS-CA TEST SUITE -- 500 SCENARIOS -- LIVE PROGRESS")
    print("=" * 75)
    print(f"Test file: {SCENARIO_TEST.relative_to(REPO)}")
    print(f"Scenario file: {SCENARIO_FILE.relative_to(REPO)}\n")

    if not SCENARIO_TEST.exists():
        raise FileNotFoundError(f"Missing canonical scenario test: {SCENARIO_TEST}")
    if not SCENARIO_FILE.exists():
        raise FileNotFoundError(f"Missing scenario data: {SCENARIO_FILE}")

    install = run_command([sys.executable, "-m", "pip", "install", "-q", "pytest", "pytest-json-report"])
    if install.returncode != 0:
        raise RuntimeError(f"pytest installation failed:\n{install.stderr}")

    report_path = Path("/tmp/spsca_scenario_report.json")
    result = run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            str(SCENARIO_TEST),
            "-v",
            "--tb=short",
            "-p",
            "no:cacheprovider",
            f"--json-report",
            f"--json-report-file={report_path}",
        ],
        timeout=300,
    )

    total, passed, failed, skipped, failures = print_pytest_progress(result.stdout + "\n" + result.stderr)
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "test_run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "suite": "canonical-scenario-suite",
        "scenario_file": str(SCENARIO_FILE.relative_to(REPO)),
        "test_file": str(SCENARIO_TEST.relative_to(REPO)),
        "summary": {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": round((passed / total) * 100, 2) if total else 0.0,
        },
        "capabilities": load_capability_snapshot(),
        "growth": load_growth_snapshot(),
        "failures": failures,
    }
    METRICS_FILE.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("\n" + "-" * 75)
    print("500-SCENARIO TEST SUMMARY")
    print("-" * 75)
    print(f"Total Tests:     {total}")
    print(f"  ✓ Passed:      {passed}")
    print(f"  ✗ Failed:      {failed}")
    print(f"  ⊘ Skipped:     {skipped}")
    print(f"Success Rate:    {metrics['summary']['success_rate']}%")
    print(f"Metrics:         {METRICS_FILE.relative_to(REPO)}")
    return metrics


def run_growth_suite() -> dict | None:
    if not RUN_GROWTH_E2E:
        print("\nGrowth E2E run disabled (SPS_CA_RUN_GROWTH_E2E=false).")
        return None

    print("\n" + "-" * 75)
    print("[GROWTH] Running model-backed 500-scenario evaluation")
    print("-" * 75)
    print(f"Model: {MODEL}")
    print("This run records real Layer-8 evidence into runtime/evolution_events.json.")

    command = [
        sys.executable,
        "-m",
        "evaluation.scenario_runner",
        "--file",
        str(SCENARIO_FILE.relative_to(REPO)),
        "--model",
        MODEL,
        "--live-evolve",
    ]
    process = subprocess.Popen(command, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    output_lines: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        output_lines.append(line.rstrip())
        print(line.rstrip())
    return_code = process.wait()

    growth = load_growth_snapshot()
    print("\n" + "-" * 75)
    print("GROWTH SNAPSHOT")
    print("-" * 75)
    print(json.dumps(growth, indent=2))
    if return_code != 0:
        raise RuntimeError(f"Model-backed growth suite exited with code {return_code}")
    return {"return_code": return_code, "growth": growth, "output": output_lines[-25:]}


print("\n" + "=" * 75)
print("SPS-CA COLAB TEST RUNNER")
print("=" * 75)
contract_metrics = run_500_contract_tests()
growth_result = run_growth_suite()

print("\n" + "=" * 75)
print("WEB UI / GROWTH ARTIFACTS")
print("=" * 75)
print(f"✓ Test metrics: {METRICS_FILE.relative_to(REPO)}")
print(f"✓ Capability registry: capabilities/registry.json")
print(f"✓ Evolution evidence: runtime/evolution_events.json")
print(f"✓ Evolution trace: experience/traces/evolution_history.json")
print("Refresh the Growth tab after the dashboard is running.")

if contract_metrics["summary"]["failed"]:
    raise SystemExit(contract_metrics["summary"]["failed"])
