from layers.layer_08_evolution_core.growth_decision import GrowthDecision, GrowthDecisionEngine


def test_high_fitness_reuses_existing_capability():
    result = GrowthDecisionEngine().decide(
        existing_capability_id="CAP-005",
        capability_fitness=94.0,
        recurrence=20.0,
        adaptation_viability=30.0,
        improvement_viability=25.0,
        composition_viability=10.0,
        creation_need=5.0,
        confidence=95.0,
        regression_risk=5.0,
    )

    assert result.decision is GrowthDecision.REUSE
    assert result.scores["reuse"] >= 90.0


def test_weak_capability_with_high_improvement_score_is_improved():
    result = GrowthDecisionEngine().decide(
        existing_capability_id="CAP-005",
        capability_fitness=42.0,
        recurrence=80.0,
        adaptation_viability=20.0,
        improvement_viability=88.0,
        composition_viability=15.0,
        creation_need=65.0,
        confidence=90.0,
        regression_risk=20.0,
    )

    assert result.decision is GrowthDecision.IMPROVE
    assert result.scores["improve"] > result.scores["create"]


def test_high_creation_need_with_low_fitness_selects_create():
    result = GrowthDecisionEngine().decide(
        capability_fitness=15.0,
        recurrence=92.0,
        adaptation_viability=20.0,
        improvement_viability=18.0,
        composition_viability=10.0,
        creation_need=95.0,
        confidence=93.0,
        regression_risk=8.0,
    )

    assert result.decision is GrowthDecision.CREATE
    assert result.scores["create"] >= 70.0


def test_count_is_only_evidence_and_no_longer_forces_create():
    result = GrowthDecisionEngine().decide(
        existing_capability_id="CAP-005",
        disagreement_count=3,
        capability_fitness=78.0,
        recurrence=55.0,
        adaptation_viability=82.0,
        improvement_viability=30.0,
        composition_viability=15.0,
        creation_need=20.0,
        confidence=88.0,
        regression_risk=10.0,
    )

    assert result.decision is GrowthDecision.ADAPT
    assert result.reason_code != "persistent_capability_gap"
