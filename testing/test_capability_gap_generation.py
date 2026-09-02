from __future__ import annotations

import json

from layers.layer_08_evolution import EvolutionEngine


def test_gap_generation_creates_executable_capability_and_metadata(tmp_path):
    engine = EvolutionEngine(
        generated_dir=str(tmp_path / "generated"),
        seeds_dir="capabilities/seeds",
        registry_path=str(tmp_path / "registry.json"),
        evaluation_dir=str(tmp_path / "evaluation"),
    )

    plan = engine.plan_capability_for_gap(
        task_description="Parameterize SQL queries",
        language="python",
        reason="No suitable registered capability was found",
        task_id="SC-001",
    )

    result = engine.develop_capability_for_gap(plan, project_root=str(tmp_path))

    assert result["capability_id"] == plan.capability_id
    assert result["implemented"] is True
    assert result["test_result"]["passed"] is True
    assert (tmp_path / "generated" / plan.capability_id.lower().replace("-", "_") / "capability.py").exists()
    assert (tmp_path / "generated" / plan.capability_id.lower().replace("-", "_") / "tests.py").exists()


def test_gap_generation_persists_registration_when_quality_gates_pass(tmp_path):
    registry_path = tmp_path / "registry.json"
    engine = EvolutionEngine(
        generated_dir=str(tmp_path / "generated"),
        seeds_dir="capabilities/seeds",
        registry_path=str(registry_path),
        evaluation_dir=str(tmp_path / "evaluation"),
    )

    plan = engine.plan_capability_for_gap(
        task_description="Add request logging",
        language="python",
        reason="No suitable logging capability was found",
        task_id="SC-002",
    )
    result = engine.develop_capability_for_gap(plan, project_root=str(tmp_path))

    assert result["registered"] is True
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert plan.capability_id in registry
    assert registry[plan.capability_id]["generated"] is True
