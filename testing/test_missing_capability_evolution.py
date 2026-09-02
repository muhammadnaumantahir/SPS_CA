from __future__ import annotations

from layers.layer_08_evolution.gap_planner import CapabilityGapPlanner


def test_missing_capability_can_be_planned_without_repeated_failures(tmp_path):
    planner = CapabilityGapPlanner(
        seeds_dir="capabilities/seeds",
        generated_dir=str(tmp_path / "generated"),
    )

    plan = planner.plan(
        task_description="Add input validation before calculating age",
        language="python",
        reason="No registered capability covers input validation",
    )

    assert plan.capability_id.startswith("CAP-")
    assert plan.trigger_pattern == "input_validation"
    assert "input validation" in plan.description.lower()


def test_capability_gap_plan_records_research_provenance(tmp_path):
    planner = CapabilityGapPlanner(
        seeds_dir="capabilities/seeds",
        generated_dir=str(tmp_path / "generated"),
    )

    plan = planner.plan(
        task_description="Parameterize SQL queries",
        language="python",
        reason="No suitable SQL parameterization capability exists",
    )

    assert plan.provenance["why"] == "No suitable SQL parameterization capability exists"
    assert plan.provenance["what"] == "Parameterize SQL queries"
    assert plan.provenance["language"] == "python"
    assert plan.provenance["trigger"] == "capability_gap"
