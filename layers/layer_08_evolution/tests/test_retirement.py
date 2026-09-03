import json

from layers.capability_registry import CapabilityRegistryManager
from layers.layer_05_experience import ExperienceLog, Task
from layers.layer_08_evolution import GovernedRetirementManager


def _task(task_id, capability, status):
    return Task(
        id=task_id,
        user_request=f"request {task_id}",
        status=status,
        selected_capability=capability,
        time_taken_seconds=1.0,
    )


def test_retirement_requires_evidence_and_protects_canonical(tmp_path):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(json.dumps({"capabilities": [
        {"id": "CAP-010", "name": "canonical", "description": "", "type": "modification", "entry_point": "", "supported_languages": ["python"], "canonical": True, "generated": False},
        {"id": "CAP-011", "name": "generated", "description": "", "type": "modification", "entry_point": "", "supported_languages": ["python"], "generated": True, "status": "active"},
    ]}), encoding="utf-8")
    manager = GovernedRetirementManager(registry=CapabilityRegistryManager(str(registry_path)))
    no_data = manager.recommend(ExperienceLog(), "CAP-011")
    assert no_data.eligible is False
    canonical = manager.recommend(ExperienceLog(), "CAP-010")
    assert canonical.eligible is False
    assert canonical.reason == "canonical_capability_protected"


def test_retirement_uses_governance_before_deactivation(tmp_path):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(json.dumps({"capabilities": [
        {"id": "CAP-011", "name": "generated", "description": "", "type": "modification", "entry_point": "", "supported_languages": ["python"], "generated": True, "status": "active"},
    ]}), encoding="utf-8")
    registry = CapabilityRegistryManager(str(registry_path))
    manager = GovernedRetirementManager(registry=registry)
    log = ExperienceLog([
        _task("1", "CAP-011", "failure"),
        _task("2", "CAP-011", "failure"),
        _task("3", "CAP-011", "failure"),
        _task("4", "CAP-011", "failure"),
        _task("5", "CAP-011", "partial"),
    ])
    result = manager.retire(log, "CAP-011")
    assert result["governance"] in {"approved", "auto_approved"}
    assert result["retired"] is True
    assert registry.get_capability("CAP-011").status == "deprecated"
