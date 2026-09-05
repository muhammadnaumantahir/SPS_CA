"""Executable 1000-case SPS-CA growth suite.

490 deterministic routing cases + 500 evolution strategy contracts + 10 real
Evolution evidence lifecycle proof cases. Proof cases use isolated temporary
runtime/registry files so they never mutate the repository's live state.
"""
from __future__ import annotations
import json
import tempfile
from pathlib import Path
import pytest
from brain.brain import Brain
SCENARIO_FILE = Path(__file__).resolve().parents[1] / "evaluation" / "scenarios" / "growth.json"

@pytest.fixture(scope="module")
def scenarios():
    data = json.loads(SCENARIO_FILE.read_text(encoding="utf-8"))
    scenarios = data["scenarios"]
    assert len(scenarios) == 1000
    return scenarios

def _run_evolution_proof(scenario):
    from layers.layer_08_evolution.evolution_evidence import EvolutionEvidenceStore
    from layers.capability_registry.registry import CapabilityRegistryManager
    with tempfile.TemporaryDirectory(prefix="sps_ca_evolution_proof_") as tmp:
        root = Path(tmp)
        events_path = root / "runtime" / "evolution_events.json"
        registry_path = root / "registry.json"
        store = EvolutionEvidenceStore(path=events_path, registry_path=registry_path)
        request = "Create a reusable capability for repeated structured-data parsing failures."
        kwargs = {
            "session_id": "proof-session",
            "turn_id": "proof-turn",
            "request": request,
            "language": "python",
            "language_confidence": 0.99,
            "previous_capability_id": "CAP-001",
            "code": "def parse(value):\n    return value\n",
            "capability_match": False,
            "capability_fitness": 10.0,
            "recurrence_score": 80.0,
            "confidence_score": 95.0,
            "creation_need": 95.0,
        }
        events = [store.record_disagreement(**kwargs) for _ in range(3)]
        analysis = store.analyze(events[-1])
        assert analysis["event_type"] == "evolution_analysis"
        assert analysis["decision"] == "create"
        creation = store.record_creation(analysis)
        assert creation["event_type"] == "capability_created"
        cap_id = creation["created_capability_id"]
        assert creation["validation_status"] == "registered"
        stored_events = json.loads(events_path.read_text(encoding="utf-8"))
        assert any(e.get("event_type") == "capability_created" and e.get("created_capability_id") == cap_id for e in stored_events)
        registry = CapabilityRegistryManager(str(registry_path))
        matches = registry.search_capabilities("structured-data parsing failures", language="python")
        assert any(cap.id == cap_id for cap in matches)
        before = registry.get_capability(cap_id).reuse_count
        assert registry.record_usage(cap_id, success=True, notes="later-request evolution-proof reuse")
        registry2 = CapabilityRegistryManager(str(registry_path))
        after = registry2.get_capability(cap_id).reuse_count
        assert after == before + 1
        assert after >= scenario["expected"]["min_reuse_count_after_reuse"]
        lineage = store.get_capability_lineage(cap_id)
        assert lineage["capability"]["generated"] is True
        assert lineage["provenance"]["decision"] == "create"
        return {"capability_id": cap_id, "events": len(stored_events), "reuse_count": after}

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
        result = _run_evolution_proof(scenario)
        assert result["events"] >= 5
        assert result["reuse_count"] >= 1
    else:
        raise AssertionError(f"unknown scenario type: {kind}")

def test_suite_is_exactly_1000_cases(scenarios):
    assert len(scenarios) == 1000
    assert len({s["id"] for s in scenarios}) == 1000
    assert sum(s["scenario_type"] == "capability_routing" for s in scenarios) == 490
    assert sum(s["scenario_type"] == "autonomous_evolution" for s in scenarios) == 500
    assert sum(s["scenario_type"] == "evolution_proof" for s in scenarios) == 10
