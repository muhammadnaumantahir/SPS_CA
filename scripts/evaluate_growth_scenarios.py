import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCENARIO_FILE = REPO / "evaluation/scenarios/growth_1000.json"
GENERATOR = REPO / "scripts/generate_growth_scenarios.py"


def run_generator():
    result = subprocess.run([sys.executable, str(GENERATOR)], cwd=REPO, text=True, capture_output=True)
    print(result.stdout)
    if result.returncode:
        print(result.stderr)
        raise SystemExit(result.returncode)


def load():
    with SCENARIO_FILE.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 1000:
        raise AssertionError("expected exactly 1000 scenarios")
    return scenarios


def validate_structure(scenarios):
    required = {"id", "scenario_type", "request", "code", "language", "filename", "expected", "feedback"}
    for item in scenarios:
        missing = required - set(item)
        if missing:
            raise AssertionError(f"{item.get('id')}: missing {sorted(missing)}")
    assert sum(s["scenario_type"] == "capability_routing" for s in scenarios) == 500
    assert sum(s["scenario_type"] == "autonomous_evolution" for s in scenarios) == 500


def validate_routing(scenarios):
    from brain import Brain

    brain = Brain()
    failures = []
    for scenario in scenarios:
        if scenario["scenario_type"] != "capability_routing":
            continue
        detected = brain.detect_language(scenario["code"], scenario["request"], scenario["filename"])
        language = detected[0] if isinstance(detected, tuple) else detected
        intent = brain.infer_intent_class(scenario["request"], scenario["code"], scenario["filename"])
        if language != scenario["language"] or intent != scenario["expected"]["intent"]:
            failures.append({"id": scenario["id"], "language": (language, scenario["language"]), "intent": (intent, scenario["expected"]["intent"])})
    assert not failures, json.dumps(failures[:20], indent=2)
    print("Brain routing validated: 500 scenarios")


def validate_evolution_contracts(scenarios):
    from brain.sps_controller import SPSBrainController, SPSDecision
    from brain.evolution_designer import AICapabilityDesigner

    strategy_counts = {}
    evolution_cases = [s for s in scenarios if s["scenario_type"] == "autonomous_evolution"]
    for scenario in evolution_cases:
        strategy = scenario["expected"]["strategy"]
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        expected = scenario["expected"]
        assert expected["status"] == "success"
        assert expected["output_required"] is True
        assert isinstance(scenario["context"]["evidence"], str) and scenario["context"]["evidence"]

    assert strategy_counts == {"create": 100, "improve": 100, "adapt": 100, "replan": 100, "compose": 100}
    create_cases = [s for s in evolution_cases if s["expected"]["strategy"] == "create"]
    assert all(s["expected"]["capability_creation_expected"] for s in create_cases)
    assert all(s["expected"]["evolution_required"] for s in create_cases)

    decision = SPSBrainController._decision({"strategy": "create", "task_instruction": "create a reusable capability", "success_criteria": ["tested", "registered"]})
    assert isinstance(decision, SPSDecision)
    assert decision.strategy == "create"

    sample_source = "from capabilities.base import CapabilityContext, CapabilityResult\n\ndef run(context: CapabilityContext) -> CapabilityResult:\n    return CapabilityResult.ok(summary='ok')\n"
    sample_tests = "def test_generated_capability():\n    assert True\n"
    assert AICapabilityDesigner._require_source(sample_source)
    assert AICapabilityDesigner._require_tests(sample_tests)
    print("Autonomous evolution scenarios validated: 500 scenarios")
    print("  create: 100")
    print("  improve: 100")
    print("  adapt: 100")
    print("  replan: 100")
    print("  compose: 100")


def main():
    print("=" * 70)
    print("SPS-CA — GROWTH EVALUATION")
    print("=" * 70)
    print("\n[1] Generating growth scenarios...")
    run_generator()
    scenarios = load()
    print(f"[2] Loaded {len(scenarios)} scenarios")
    validate_structure(scenarios)
    print("✓ Structure: PASS")
    validate_routing(scenarios)
    validate_evolution_contracts(scenarios)
    print("\n✓ Growth routing: PASS")
    print("✓ Autonomous evolution contracts: PASS")
    print("=" * 70)


if __name__ == "__main__":
    main()
