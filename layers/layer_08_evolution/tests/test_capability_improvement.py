from pathlib import Path

from layers.layer_08_evolution.capability_improvement import (
    CapabilityImprovementEngine,
    ImprovementDecision,
)


def test_improvement_requires_a_measurable_gain_and_preserves_the_source():
    engine = CapabilityImprovementEngine()
    decision = engine.compare(
        capability_id="CAP-005",
        baseline_score=62.0,
        candidate_score=81.0,
        minimum_gain=10.0,
    )

    assert decision.decision is ImprovementDecision.PROMOTE
    assert decision.score_delta == 19.0
    assert decision.source_version == "active"
    assert decision.candidate_version == "candidate"


def test_non_improving_candidate_is_rejected():
    engine = CapabilityImprovementEngine()
    decision = engine.compare(
        capability_id="CAP-005",
        baseline_score=82.0,
        candidate_score=81.0,
        minimum_gain=10.0,
    )

    assert decision.decision is ImprovementDecision.REJECT
    assert decision.score_delta == -1.0


def test_promote_creates_versioned_lineage_without_overwriting_source(tmp_path: Path):
    engine = CapabilityImprovementEngine(
        root=tmp_path,
        registry_path=tmp_path / "registry.json",
    )
    engine.seed_active_capability(
        capability_id="CAP-005",
        version="1.0.0",
        source="return 'baseline'\n",
    )

    result = engine.promote_candidate(
        capability_id="CAP-005",
        candidate_source="return 'improved'\n",
        baseline_score=62.0,
        candidate_score=81.0,
        minimum_gain=10.0,
    )

    assert result["promoted"] is True
    assert result["version"] == "1.1.0"
    assert result["parent_version"] == "1.0.0"
    assert "CAP-005" in result["lineage"]["capability_id"]
    assert (tmp_path / "capabilities" / "cap_005" / "v1_0_0" / "capability.py").read_text() == "return 'baseline'\n"
    assert (tmp_path / "capabilities" / "cap_005" / "v1_1_0" / "capability.py").read_text() == "return 'improved'\n"


def test_improvement_candidate_can_be_rejected_without_mutating_active_version(tmp_path: Path):
    engine = CapabilityImprovementEngine(
        root=tmp_path,
        registry_path=tmp_path / "registry.json",
    )
    engine.seed_active_capability(
        capability_id="CAP-005",
        version="1.0.0",
        source="return 'baseline'\n",
    )

    result = engine.promote_candidate(
        capability_id="CAP-005",
        candidate_source="return 'worse'\n",
        baseline_score=82.0,
        candidate_score=75.0,
        minimum_gain=10.0,
    )

    assert result["promoted"] is False
    assert result["decision"] == "reject"
    assert result["active_version"] == "1.0.0"
    assert not (tmp_path / "capabilities" / "cap_005" / "v1_1_0").exists()
