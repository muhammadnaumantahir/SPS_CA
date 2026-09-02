from __future__ import annotations

import json

from layers.layer_08_evolution import EvolutionEngine


def _bootstrap_isolated_capabilities(tmp_path):
    package = tmp_path / "capabilities"
    generated = package / "generated"
    package.mkdir()
    generated.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (generated / "__init__.py").write_text("", encoding="utf-8")
    (package / "base.py").write_text(
        "from dataclasses import dataclass, field\n"
        "from typing import Any, Dict, Optional\n\n"
        "@dataclass\n"
        "class CapabilityContext:\n"
        "    code: str\n"
        "    language: str\n"
        "    file_path: str = ''\n"
        "    project_path: str = ''\n"
        "    parameters: Dict[str, Any] = field(default_factory=dict)\n"
        "    metadata: Dict[str, Any] = field(default_factory=dict)\n\n"
        "@dataclass\n"
        "class CapabilityResult:\n"
        "    success: bool\n"
        "    modified_code: Optional[str] = None\n"
        "    summary: str = ''\n"
        "    findings: list = field(default_factory=list)\n"
        "    error: Optional[str] = None\n\n"
        "    @classmethod\n"
        "    def ok(cls, summary, modified_code=None, findings=None):\n"
        "        return cls(True, modified_code, summary, findings or [], None)\n\n"
        "    @classmethod\n"
        "    def fail(cls, error, summary=''):\n"
        "        return cls(False, None, summary, [], error)\n",
        encoding="utf-8",
    )
    return generated


def _engine(tmp_path):
    generated_dir = _bootstrap_isolated_capabilities(tmp_path)
    return EvolutionEngine(
        generated_dir=str(generated_dir),
        seeds_dir="capabilities/seeds",
        registry_path=str(tmp_path / "registry.json"),
        evaluation_dir=str(tmp_path / "evaluation"),
    )


def test_gap_generation_creates_executable_capability_and_metadata(tmp_path):
    engine = _engine(tmp_path)

    plan = engine.plan_capability_for_gap(
        task_description="Parameterize SQL queries",
        language="python",
        reason="No suitable registered capability was found",
        task_id="SC-001",
    )

    result = engine.develop_capability_for_gap(plan, project_root=str(tmp_path))

    module_dir = tmp_path / "capabilities" / "generated" / plan.capability_id.lower().replace("-", "_")
    assert result["capability_id"] == plan.capability_id
    assert result["implemented"] is True
    assert result["test_result"]["passed"] is True
    assert (module_dir / "capability.py").exists()
    assert (module_dir / "tests.py").exists()


def test_gap_generation_persists_registration_when_quality_gates_pass(tmp_path):
    engine = _engine(tmp_path)
    registry_path = tmp_path / "registry.json"

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
