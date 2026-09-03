from layers.layer_08_evolution.growth_decision import GrowthDecision, GrowthDecisionEngine


def test_disagreement_is_evidence_not_automatic_creation():
    decision = GrowthDecisionEngine().decide(
        existing_capability_id="CAP-005",
        disagreement_count=3,
        capability_match=True,
        repeated_pattern=True,
        adaptation_viable=True,
        composition_viable=False,
        improvement_viable=False,
    )
    assert decision.decision != GrowthDecision.CREATE
    assert decision.reason_code in {"adapt", "insufficient_gap"}


def test_genuine_gap_can_create_capability():
    decision = GrowthDecisionEngine().decide(
        existing_capability_id="",
        disagreement_count=0,
        capability_match=False,
        repeated_pattern=False,
        adaptation_viable=False,
        composition_viable=False,
        improvement_viable=False,
    )
    assert decision.decision == GrowthDecision.CREATE
    assert decision.reason_code == "capability_gap"


def test_existing_capability_is_reused_when_sufficient():
    decision = GrowthDecisionEngine().decide(
        existing_capability_id="CAP-005",
        disagreement_count=0,
        capability_match=True,
        repeated_pattern=False,
        adaptation_viable=False,
        composition_viable=False,
        improvement_viable=False,
    )
    assert decision.decision == GrowthDecision.REUSE


def test_repeated_composition_pattern_can_create_composite_growth():
    decision = GrowthDecisionEngine().decide(
        existing_capability_id="CAP-005",
        disagreement_count=2,
        capability_match=True,
        repeated_pattern=True,
        adaptation_viable=False,
        composition_viable=True,
        improvement_viable=False,
    )
    assert decision.decision == GrowthDecision.COMPOSE


def test_degraded_capability_can_be_improved_before_creation():
    decision = GrowthDecisionEngine().decide(
        existing_capability_id="CAP-005",
        disagreement_count=2,
        capability_match=True,
        repeated_pattern=True,
        adaptation_viable=False,
        composition_viable=False,
        improvement_viable=True,
    )
    assert decision.decision == GrowthDecision.IMPROVE
