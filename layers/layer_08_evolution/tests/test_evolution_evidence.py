import json

import pytest

from layers.layer_08_evolution.evolution_evidence import EvolutionEvidenceStore


def _store(tmp_path):
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps({"version": "1.0.0", "capabilities": [], "usage_history": []}),
        encoding="utf-8",
    )
    return EvolutionEvidenceStore(tmp_path / "events.json", registry)


def test_disagreement_evidence_can_progress_to_create(tmp_path):
    store = _store(tmp_path)
    decisions = []
    evidence = [
        dict(capability_match=True, capability_fitness=80, recurrence_score=25, confidence_score=70, creation_need=10),
        dict(capability_match=True, capability_fitness=45, recurrence_score=50, confidence_score=85, adaptation_viability=90),
        dict(capability_match=False, capability_fitness=15, recurrence_score=80, confidence_score=95, creation_need=95),
    ]
    for n, metrics in enumerate(evidence, 1):
        event = store.record_disagreement(
            session_id="s1",
            turn_id=n,
            request="infer CSV schema from inconsistent samples",
            language="python",
            language_confidence=0.99,
            previous_capability_id="CAP-002",
            code="def parse(value): return value",
            **metrics,
        )
        analysis = store.analyze(event)
        decisions.append(analysis["decision"])

    assert decisions == ["defer", "adapt", "create"]


def test_unscored_repeated_unmet_requirement_can_create_from_accumulated_evidence(tmp_path):
    store = _store(tmp_path)
    decisions = []
    for n in range(1, 4):
        event = store.record_disagreement(
            session_id="s1",
            turn_id=n,
            request="Create a reusable capability for repeated structured-data parsing failures.",
            language="python",
            language_confidence=0.95,
            previous_capability_id="CAP-002",
            code="def parse(value): return value",
        )
        analysis = store.analyze(event)
        decisions.append(analysis["decision"])

    assert decisions[:2] == ["defer", "defer"]
    assert decisions[2] == "create"
    assert analysis["growth_decision"]["evidence"]["capability_match"] is False


def test_record_creation_requires_explicit_create(tmp_path):
    store = _store(tmp_path)
    with pytest.raises(ValueError, match="explicit CREATE"):
        store.record_creation(
            {
                "decision": "reuse",
                "request": "reuse this capability",
                "language": "python",
                "previous_capability_id": "CAP-002",
            }
        )


def test_create_decision_registers_generated_capability_with_lineage(tmp_path):
    store = _store(tmp_path)
    event = store.record_disagreement(
        session_id="s1",
        turn_id=3,
        request="Create a reusable CSV schema inference capability.",
        language="python",
        language_confidence=0.99,
        previous_capability_id="CAP-002",
        code="def parse(value): return value",
        capability_match=False,
        capability_fitness=10,
        recurrence_score=85,
        confidence_score=95,
        creation_need=95,
    )
    analysis = store.analyze(event)
    assert analysis["decision"] == "create"

    created = store.record_creation(analysis)
    assert created["event_type"] == "capability_created"
    cap_id = created["created_capability_id"]
    lineage = store.get_capability_lineage(cap_id)
    assert lineage["provenance"]["decision"] == "create"
    assert lineage["capability"]["generated"] is True
