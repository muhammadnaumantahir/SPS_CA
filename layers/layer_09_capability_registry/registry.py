"""Layer 9: capability registry.

Provides a small persistent registry for promoted capabilities. Layer 8 owns
creation and governance; this layer owns discovery and registration.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


class RegistryError(RuntimeError):
    """Raised when a capability cannot be registered or resolved."""


@dataclass(frozen=True)
class CapabilityRecord:
    capability_id: str
    name: str
    version: str
    path: str
    entry_point: str = "run"
    trigger_pattern: str = ""
    parent_capabilities: Optional[List[str]] = None
    model_provider: str = ""
    model: str = ""


class CapabilityRegistry:
    """Persistent JSON-backed registry of active generated capabilities."""

    def __init__(self, registry_path: str = "capabilities/registry.json") -> None:
        self.registry_path = Path(registry_path)
        self._records: Dict[str, CapabilityRecord] = {}
        self._load()

    def register(self, record: CapabilityRecord) -> CapabilityRecord:
        if not record.capability_id.strip():
            raise RegistryError("capability_id must be non-empty")
        existing = self._records.get(record.capability_id)
        if existing and existing.version == record.version and existing.path == record.path:
            return existing
        if existing:
            raise RegistryError(f"Capability already registered: {record.capability_id}")
        if not Path(record.path).exists():
            raise RegistryError(f"Capability path does not exist: {record.path}")
        self._records[record.capability_id] = record
        self._save()
        return record

    def get(self, capability_id: str) -> Optional[CapabilityRecord]:
        return self._records.get(capability_id)

    def list(self) -> List[CapabilityRecord]:
        return sorted(self._records.values(), key=lambda item: item.capability_id)

    def contains(self, capability_id: str) -> bool:
        return capability_id in self._records

    def _load(self) -> None:
        if not self.registry_path.exists():
            return
        payload = json.loads(self.registry_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RegistryError("Registry must contain a JSON object")
        for capability_id, data in payload.get("capabilities", {}).items():
            if isinstance(data, dict):
                self._records[capability_id] = CapabilityRecord(**data)

    def _save(self) -> None:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        payload: Dict[str, Any] = {
            "version": "1.0",
            "capabilities": {key: asdict(value) for key, value in self._records.items()},
        }
        self.registry_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
