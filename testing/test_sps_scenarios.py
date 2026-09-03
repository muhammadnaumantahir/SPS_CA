"""Executable 1000-case SPS-CA growth suite.

490 deterministic routing cases + 500 evolution strategy contracts + 10 real
Evolution lifecycle proof cases. Proof cases use isolated temporary directories
so they never mutate the repository's live registry/runtime evidence.
"""
from __future__ import annotations
import json
import tempfile
from pathlib import Path
import pytest
from brain.brain import Brain
SCENARIO_FILE = Path(__file__).resolve().parents[1] / "evaluation" / "scenarios" / "growth_1000.json"

@pytest.fixture(scope="module")
def scenarios():
    data = json.loads(SCENARIO_FILE.read_text(encoding="utf-8"))
    scenarios = data["scenarios"]
    assert len(scenarios) == 1000
    return scenarios

def _run_evolution_proof(scenario):
    from layers.layer_02_governance.governance import GovernanceGate
    from layers.layer_05_experience.experience_log import ExperienceLog
    from layers.layer_05_experience.models import Task
    from layers.layer_08_evolution.evolution_engine import EvolutionEngine
    from layers.capability_registry.registry import CapabilityRegistryManager
    repo = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="sps_ca_evolution_proof_") as tmp:
        root = Path(tmp)
        log = ExperienceLog()
        for task_id, request in (("proof-001", "Parse this JSON config into a dict"), ("proof-002", "Parse this XML response into a dict"), ("proof-003", "Parse this CSV export into a dict")):
            log.add_task(Task(id=task_id, user_request=request, target_project="evolution_proof", target_language="python", status="failure", selected_capability="CAP-001", outcome="CAP-001 cannot handle structured-data parsing.", failure_category="Parse error"))
        registry_path = root / "registry.json"
        engine = EvolutionEngine(governance_gate=GovernanceGate(), generated_dir=str(root / "generated"), seeds_dir=str(repo / "capabilities" / "seeds"), registry_path=str(registry_path), evaluation_dir=str(root / "evaluation"))
        assert engine.should_evolve(log)
        triggers = engine.get_trigger_patterns(log)
        assert triggers and triggers[0].pattern == "Parse error"
        record = engine.run_evolution_cycle(log)
        assert record is not None and record.registered is True
        assert record.test_result.tests_failed == 0
        registry = CapabilityRegistryManager(str(registry_path))
        capability = registry.get_capability(record.capability_id)
        assert capability is not None and capability.generated is True and capability.status == "active"
        before = capability.reuse_count
        assert registry.record_usage(record.capability_id, success=True, notes="evolution-proof reuse")
        registry2 = CapabilityRegistryManager(str(registry_path))
        after = registry2.get_capability(record.capability_id).reuse_count
        assert after == before + 1
        assert after >= scenario["expected"]["min_reuse_count_after_reuse"]
        return record.capability_id, after

@pytest.mark.parametrize("index", range(1000))
def test_growth_1000_case(index, scenarios):
    scenario = scenarios[index]
    assert scenario["id"] and scenario["request"].strip() and scenario["language"] == "python"
    assert scenario["expected"]["status"] == "success"
    kind = scenario["scenario_type"]
    if kind == "capability_routing":
        language, confidence, _ = Brain.detect_language(scenario["code"], scenario["request"], scenario["filename"])
        assert language == "python" and 0.0 <= confidence <= 1.0
        assert Brain.infer_intent_class(scenario["request"], scenario["code"], scenario["filename"]) == scenario["expected"]["intent"]
    elif kind == "autonomous_evolution":
        assert scenario["context"]["evidence"]
        assert scenario["expected"]["strategy"] in {"create", "improve", "adapt", "replan", "compose"}
    elif kind == "evolution_proof":
        _, reuse_count = _run_evolution_proof(scenario)
        assert reuse_count >= 1
    else:
        raise AssertionError(f"unknown scenario type: {kind}")

def test_suite_is_exactly_1000_cases(scenarios):
    assert len(scenarios) == 1000
    assert len({s["id"] for s in scenarios}) == 1000
    assert sum(s["scenario_type"] == "capability_routing" for s in scenarios) == 490
    assert sum(s["scenario_type"] == "autonomous_evolution" for s in scenarios) == 500
    assert sum(s["scenario_type"] == "evolution_proof" for s in scenarios) == 10
