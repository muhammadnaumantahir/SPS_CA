from pathlib import Path

import pytest

from layers.layer_09_capability_registry import CapabilityRecord, CapabilityRegistry, RegistryError


def test_register_and_reload(tmp_path: Path) -> None:
    capability = tmp_path / "CAP-001"
    capability.mkdir()
    registry = CapabilityRegistry(str(tmp_path / "registry.json"))
    record = CapabilityRecord("CAP-001", "Example", "1.0.0", str(capability))

    assert registry.register(record) == record
    reloaded = CapabilityRegistry(str(tmp_path / "registry.json"))
    assert reloaded.get("CAP-001") == record


def test_duplicate_version_and_path_is_idempotent(tmp_path: Path) -> None:
    capability = tmp_path / "CAP-001"
    capability.mkdir()
    registry = CapabilityRegistry(str(tmp_path / "registry.json"))
    record = CapabilityRecord("CAP-001", "Example", "1.0.0", str(capability))

    registry.register(record)
    assert registry.register(record) == record


def test_duplicate_id_with_different_version_is_rejected(tmp_path: Path) -> None:
    capability = tmp_path / "CAP-001"
    capability.mkdir()
    registry = CapabilityRegistry(str(tmp_path / "registry.json"))
    registry.register(CapabilityRecord("CAP-001", "Example", "1.0.0", str(capability)))

    with pytest.raises(RegistryError):
        registry.register(CapabilityRecord("CAP-001", "Example", "2.0.0", str(capability)))


def test_missing_path_is_rejected(tmp_path: Path) -> None:
    registry = CapabilityRegistry(str(tmp_path / "registry.json"))
    with pytest.raises(RegistryError):
        registry.register(CapabilityRecord("CAP-001", "Example", "1.0.0", str(tmp_path / "missing")))
