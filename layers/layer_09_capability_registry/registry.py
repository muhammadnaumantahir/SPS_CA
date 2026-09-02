"""Layer 9: Capability Registry Manager.

Owns capability discovery, registration, reuse tracking, lifecycle state, and
persistence for both seed and Layer 8-generated capabilities.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import (
    CapabilityMetadata,
    CapabilityQuery,
    CapabilityQueryResult,
    CapabilityRegistry as CapabilityRegistryData,
    CapabilityReusageRecord,
    CapabilityType,
)

logger = logging.getLogger(__name__)


class CapabilityRegistryManager:
    """Manage the persistent Layer 9 capability registry."""

    def __init__(self, registry_path: str = "capabilities/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_data: CapabilityRegistryData = CapabilityRegistryData()
        self.capabilities_by_id: Dict[str, CapabilityMetadata] = {}
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        if not self.registry_path.exists():
            self.registry_data = CapabilityRegistryData()
            self.capabilities_by_id = {}
            return
        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8"))
            # Accept the legacy Layer 8 CAP-id -> metadata mapping and normalize
            # it into the canonical Layer 9 registry representation in memory.
            if "capabilities" not in data and any(str(key).startswith("CAP-") for key in data):
                raw_caps = []
                for metadata in data.values():
                    if not isinstance(metadata, dict):
                        continue
                    item = dict(metadata)
                    item.setdefault("type", CapabilityType.TRANSFORMATION.value)
                    item.setdefault("supported_languages", item.get("target_languages", ["python"]))
                    item.setdefault("generated", True)
                    item.setdefault("origin", "capability_evolution")
                    item.setdefault("status", "active")
                    item.setdefault("test_coverage", 0.0)
                    item.setdefault("documentation_path", "")
                    item.setdefault("metadata_path", "")
                    item["extra_metadata"] = {
                        **dict(item.get("extra_metadata") or {}),
                        "provenance": item.get("provenance", {}),
                        "tags": item.get("tags", []),
                    }
                    raw_caps.append(item)
                data = {
                    "version": "1.0.0",
                    "capabilities": raw_caps,
                    "usage_history": [],
                    "last_updated": datetime.utcnow().isoformat(),
                }
            self.registry_data = CapabilityRegistryData.from_dict(data)
            self.capabilities_by_id = {cap.id: cap for cap in self.registry_data.capabilities}
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to load registry: %s", exc)
            self.registry_data = CapabilityRegistryData()
            self.capabilities_by_id = {}

    def _save_to_disk(self) -> None:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_data.last_updated = datetime.utcnow().isoformat()
        self.registry_path.write_text(
            json.dumps(self.registry_data.to_dict(), indent=2, default=str) + "\n",
            encoding="utf-8",
        )

    def register(self, capability: CapabilityMetadata) -> bool:
        if capability.id in self.capabilities_by_id:
            return False
        self.registry_data.capabilities.append(capability)
        self.capabilities_by_id[capability.id] = capability
        self._save_to_disk()
        return True

    def register_from_dict(self, metadata: Dict[str, Any]) -> bool:
        normalized = dict(metadata)
        normalized.setdefault("type", CapabilityType.TRANSFORMATION.value)
        normalized.setdefault("supported_languages", normalized.get("target_languages", ["python"]))
        normalized.setdefault("status", "active")
        normalized.setdefault("generated", True)
        normalized.setdefault("origin", "capability_evolution")
        normalized.setdefault("test_coverage", 0.0)
        normalized.setdefault("documentation_path", "")
        normalized.setdefault("metadata_path", "")
        normalized["extra_metadata"] = {
            **dict(normalized.get("extra_metadata") or {}),
            "provenance": normalized.get("provenance", {}),
            "tags": normalized.get("tags", []),
        }
        capability = CapabilityMetadata.from_dict(normalized)
        return self.register(capability)

    def get_capability(self, capability_id: str) -> Optional[CapabilityMetadata]:
        return self.capabilities_by_id.get(capability_id)

    def list_all_capabilities(self) -> List[CapabilityMetadata]:
        return self.registry_data.capabilities.copy()

    def query(self, query: CapabilityQuery) -> CapabilityQueryResult:
        start_time = time.time()
        matches = self.registry_data.capabilities.copy()
        if query.capability_id:
            matches = [c for c in matches if c.id == query.capability_id]
        if query.capability_type:
            matches = [c for c in matches if c.type.value == query.capability_type or c.type == query.capability_type]
        if query.language:
            lang = query.language.lower()
            matches = [c for c in matches if lang in [item.lower() for item in c.supported_languages]]
        if query.name_contains:
            needle = query.name_contains.lower()
            matches = [c for c in matches if needle in c.name.lower()]
        if query.generated_only:
            matches = [c for c in matches if c.generated]
        if query.seed_only:
            matches = [c for c in matches if not c.generated]
        if query.status:
            matches = [c for c in matches if c.status == query.status]
        if query.min_test_coverage > 0:
            matches = [c for c in matches if c.test_coverage >= query.min_test_coverage]
        sort_key = {
            "id": lambda c: c.id,
            "reuse_count": lambda c: c.reuse_count,
            "test_coverage": lambda c: c.test_coverage,
            "created_date": lambda c: c.created_date,
            "name": lambda c: c.name,
        }.get(query.sort_by, lambda c: c.id)
        matches.sort(key=sort_key, reverse=query.sort_order == "desc")
        return CapabilityQueryResult(
            matched_count=len(matches),
            capabilities=matches,
            query_time_ms=(time.time() - start_time) * 1000,
        )

    def search_capabilities(self, request: str, language: Optional[str] = None) -> List[CapabilityMetadata]:
        """Return active capabilities with meaningful request-text evidence."""
        tokens = {token for token in request.lower().split() if len(token) >= 3}
        results = []
        for capability in self.registry_data.capabilities:
            if capability.status != "active":
                continue
            if language and language.lower() not in {item.lower() for item in capability.supported_languages}:
                continue
            extra = capability.extra_metadata or {}
            text = " ".join(
                [
                    capability.name,
                    capability.description,
                    capability.failure_pattern or "",
                    " ".join(map(str, extra.get("tags", []))),
                    json.dumps(extra.get("provenance", {}), sort_keys=True),
                ]
            ).lower()
            score = sum(1 for token in tokens if token in text)
            if score:
                results.append((score, capability))
        results.sort(key=lambda item: (-item[0], -item[1].reuse_count, item[1].id))
        return [capability for _, capability in results]

    def get_top_capabilities(self, count: int = 10, by: str = "reuse_count") -> List[CapabilityMetadata]:
        """Return the highest-ranked active capabilities by a supported metric."""
        valid_metrics = {
            "id": lambda c: c.id,
            "reuse_count": lambda c: c.reuse_count,
            "test_coverage": lambda c: c.test_coverage,
            "created_date": lambda c: c.created_date,
            "name": lambda c: c.name,
        }
        key = valid_metrics.get(by, valid_metrics["reuse_count"])
        capabilities = [c for c in self.registry_data.capabilities if c.status == "active"]
        capabilities.sort(key=key, reverse=True)
        return capabilities[: max(0, count)]

    def deprecate_capability(self, capability_id: str) -> bool:
        capability = self.capabilities_by_id.get(capability_id)
        if not capability:
            return False
        capability.status = "deprecated"
        capability.last_modified = datetime.utcnow().isoformat()
        self._save_to_disk()
        return True

    def activate_capability(self, capability_id: str) -> bool:
        capability = self.capabilities_by_id.get(capability_id)
        if not capability:
            return False
        capability.status = "active"
        capability.last_modified = datetime.utcnow().isoformat()
        self._save_to_disk()
        return True

    def get_statistics(self) -> Dict[str, Any]:
        capabilities = self.registry_data.capabilities
        total = len(capabilities)
        total_reuses = sum(cap.reuse_count for cap in capabilities)
        total_coverage = sum(cap.test_coverage for cap in capabilities)
        return {
            "total_capabilities": total,
            "seed_capabilities": sum(1 for cap in capabilities if not cap.generated),
            "generated_capabilities": sum(1 for cap in capabilities if cap.generated),
            "total_reuses": total_reuses,
            "average_reuse_count": (total_reuses / total) if total else 0.0,
            "average_test_coverage": (total_coverage / total) if total else 0.0,
            "active_count": sum(1 for cap in capabilities if cap.status == "active"),
            "deprecated_count": sum(1 for cap in capabilities if cap.status == "deprecated"),
            "experimental_count": sum(1 for cap in capabilities if cap.status == "experimental"),
        }

    def query_by_type(self, task_type: str) -> List[CapabilityMetadata]:
        return [cap for cap in self.registry_data.capabilities if cap.type.value == task_type or cap.type == task_type]

    def query_by_language(self, language: str) -> List[CapabilityMetadata]:
        lang = language.lower()
        return [cap for cap in self.registry_data.capabilities if lang in [item.lower() for item in cap.supported_languages]]

    def update_reuse_count(self, capability_id: str, increment: int = 1) -> bool:
        capability = self.capabilities_by_id.get(capability_id)
        if not capability:
            return False
        capability.reuse_count += increment
        capability.last_modified = datetime.utcnow().isoformat()
        self.registry_data.usage_history.append(CapabilityReusageRecord(capability_id=capability_id, success=True))
        self._save_to_disk()
        return True

    def record_usage(self, capability_id: str, success: bool = True, execution_time_ms: float = 0.0, notes: str = "") -> bool:
        capability = self.capabilities_by_id.get(capability_id)
        if not capability:
            return False
        if success:
            capability.reuse_count += 1
            capability.last_modified = datetime.utcnow().isoformat()
        self.registry_data.usage_history.append(
            CapabilityReusageRecord(
                capability_id=capability_id,
                success=success,
                execution_time_ms=execution_time_ms,
                notes=notes,
            )
        )
        self._save_to_disk()
        return True
