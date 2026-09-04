from evaluation.scenario_runner import _growth_evidence_from_scenario


def test_create_scenario_evidence_produces_real_capability_gap_signal():
    scenario = {
        "id": "evolution-create-001",
        "scenario_type": "autonomous_evolution",
        "request": "The existing catalog cannot satisfy this requirement for data import: CSV schema inference.",
        "context": {
            "gap_name": "CSV schema inference",
            "evidence": "No reusable capability estimates column types from inconsistent CSV samples.",
            "available_capabilities": ["CAP-001", "CAP-002"],
        },
    }

    evidence = _growth_evidence_from_scenario(scenario)

    assert evidence["capability_match"] is False
    assert evidence["capability_fitness"] < 50
    assert evidence["creation_need"] >= 90
    assert evidence["confidence_score"] >= 90
    assert evidence["recurrence_score"] >= 70


def test_non_creation_scenario_does_not_invent_a_capability_gap():
    scenario = {
        "id": "evolution-improve-001",
        "scenario_type": "autonomous_evolution",
        "request": "For reporting, an existing generated capability has this weakness: clearer errors.",
        "context": {
            "gap_name": "clearer errors",
            "evidence": "Existing generated conversion errors are vague for malformed records.",
        },
    }

    evidence = _growth_evidence_from_scenario(scenario)

    assert evidence["capability_match"] is True
    assert evidence["creation_need"] == 0
    assert evidence["improvement_viability"] >= 80
