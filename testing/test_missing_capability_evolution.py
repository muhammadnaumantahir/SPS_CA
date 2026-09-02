from __future__ import annotations

from layers.layer_08_evolution import EvolutionEngine


def test_missing_capability_can_be_planned_without_repeated_failures(tmp_path):
    engine = EvolutionEngine(
        generated_dir=str(tmp_path / "generated"),
        seeds_dir="capabilities/seeds",
        registry_path=str(tmp_path / "registry.json"),
        evaluation_dir=str(tmp_path / "evaluation"),
    )

    plan = engine.plan_capability_for_gap(
        task_description="Add input validation before calculating age",
        language="python",
        reason="No registered capability covers input validation",
    )

    assert plan.capability_id.startswith("CAP-")
    assert plan.trigger_pattern == "input_validation"
    assert "input validation" in plan.description.lower()


def test_capability_gap_plan_records_research_provenance(tmp_path):
    engine = EvolutionEngine(
        generated_dir=str(tmp_path / "generated"),
        seeds_dir="capabilities/seeds",
        registry_path=str(tmp_path / "registry.json"),
        evaluation_dir=str(tmp_path / "evaluation"),
    )

    plan = engine.plan_capability_for_gap(
        task_description="Parameterize SQL queries",
        language="python",
        reason="No suitable SQL parameterization capability exists",
    )

    assert plan.provenance["why"] == "No suitable SQL parameterization capability exists"
    assert plan.provenance["what"] == "Parameterize SQL queries"
    assert plan.provenance["language"] == "python"
    assert plan.provenance["trigger"] == "capability_gap"
