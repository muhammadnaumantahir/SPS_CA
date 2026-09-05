"""Measured, versioned improvement of an existing SPS capability.

This component keeps the current capability immutable until a candidate proves a
measurable gain. Promotion creates a new version and records parent lineage;
rejected candidates never replace the active version.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class ImprovementDecision(str, Enum):
    PROMOTE = "promote"
    REJECT = "reject"


@dataclass(frozen=True)
class ImprovementComparison:
    capability_id: str
    decision: ImprovementDecision
    baseline_score: float
    candidate_score: float
    score_delta: float
    minimum_gain: float
    source_version: str
    candidate_version: str


class CapabilityImprovementEngine:
    """Manage evidence-based capability improvement and version lineage."""

    def __init__(self, root: str | Path = ".", registry_path: str | Path | None = None) -> None:
        self.root = Path(root)
        self.capabilities_root = self.root / "capabilities"
        self.registry_path = Path(registry_path) if registry_path else self.root / "capability_versions.json"

    @staticmethod
    def _score(value: float) -> float:
        return max(0.0, min(100.0, float(value)))

    def compare(
        self,
        *,
        capability_id: str,
        baseline_score: float,
        candidate_score: float,
        minimum_gain: float = 10.0,
        source_version: str = "active",
        candidate_version: str = "candidate",
    ) -> ImprovementComparison:
        if not capability_id:
            raise ValueError("capability_id must be non-empty")
        baseline = self._score(baseline_score)
        candidate = self._score(candidate_score)
        gain = float(minimum_gain)
        if gain < 0:
            raise ValueError("minimum_gain must be >= 0")
        delta = round(candidate - baseline, 2)
        decision = ImprovementDecision.PROMOTE if delta >= gain else ImprovementDecision.REJECT
        return ImprovementComparison(
            capability_id=capability_id,
            decision=decision,
            baseline_score=baseline,
            candidate_score=candidate,
            score_delta=delta,
            minimum_gain=gain,
            source_version=source_version,
            candidate_version=candidate_version,
        )

    def seed_active_capability(self, *, capability_id: str, version: str, source: str) -> dict[str, Any]:
        self._validate_capability_id(capability_id)
        self._validate_version(version)
        version_dir = self._version_dir(capability_id, version)
        version_dir.mkdir(parents=True, exist_ok=True)
        (version_dir / "capability.py").write_text(source, encoding="utf-8")
        state = self._load_state()
        capabilities = state.setdefault("capabilities", {})
        capabilities[capability_id] = {
            "active_version": version,
            "versions": [
                {
                    "version": version,
                    "status": "active",
                    "parent_version": None,
                    "score": None,
                }
            ],
            "lineage": [version],
        }
        self._save_state(state)
        return dict(capabilities[capability_id])

    def promote_candidate(
        self,
        *,
        capability_id: str,
        candidate_source: str,
        baseline_score: float,
        candidate_score: float,
        minimum_gain: float = 10.0,
    ) -> dict[str, Any]:
        self._validate_capability_id(capability_id)
        state = self._load_state()
        record = state.get("capabilities", {}).get(capability_id)
        if not record:
            raise ValueError(f"No active capability state found for {capability_id}")

        active_version = str(record["active_version"])
        comparison = self.compare(
            capability_id=capability_id,
            baseline_score=baseline_score,
            candidate_score=candidate_score,
            minimum_gain=minimum_gain,
            source_version=active_version,
            candidate_version=self._next_version(active_version),
        )
        if comparison.decision is ImprovementDecision.REJECT:
            return {
                "capability_id": capability_id,
                "decision": comparison.decision.value,
                "promoted": False,
                "active_version": active_version,
                "candidate_version": comparison.candidate_version,
                "baseline_score": comparison.baseline_score,
                "candidate_score": comparison.candidate_score,
                "score_delta": comparison.score_delta,
                "minimum_gain": comparison.minimum_gain,
                "lineage": {
                    "capability_id": capability_id,
                    "parent_version": active_version,
                    "candidate_version": comparison.candidate_version,
                    "status": "rejected",
                },
            }

        candidate_dir = self._version_dir(capability_id, comparison.candidate_version)
        candidate_dir.mkdir(parents=True, exist_ok=False)
        (candidate_dir / "capability.py").write_text(candidate_source, encoding="utf-8")
        lineage = list(record.get("lineage", [])) + [comparison.candidate_version]
        record["active_version"] = comparison.candidate_version
        record.setdefault("versions", []).append(
            {
                "version": comparison.candidate_version,
                "status": "active",
                "parent_version": active_version,
                "baseline_score": comparison.baseline_score,
                "candidate_score": comparison.candidate_score,
                "score_delta": comparison.score_delta,
                "minimum_gain": comparison.minimum_gain,
            }
        )
        for item in record["versions"][:-1]:
            item["status"] = "superseded"
        record["lineage"] = lineage
        state["capabilities"][capability_id] = record
        self._save_state(state)
        return {
            "capability_id": capability_id,
            "decision": comparison.decision.value,
            "promoted": True,
            "version": comparison.candidate_version,
            "parent_version": active_version,
            "active_version": comparison.candidate_version,
            "baseline_score": comparison.baseline_score,
            "candidate_score": comparison.candidate_score,
            "score_delta": comparison.score_delta,
            "minimum_gain": comparison.minimum_gain,
            "lineage": {"capability_id": capability_id, "versions": lineage},
        }

    def _version_dir(self, capability_id: str, version: str) -> Path:
        numeric = capability_id.lower().replace("-", "_")
        version_slug = "v" + version.replace(".", "_")
        return self.capabilities_root / numeric / version_slug

    def _load_state(self) -> dict[str, Any]:
        if not self.registry_path.exists():
            return {"version": 1, "capabilities": {}}
        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"version": 1, "capabilities": {}}
        return data if isinstance(data, dict) else {"version": 1, "capabilities": {}}

    def _save_state(self, state: dict[str, Any]) -> None:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.registry_path.with_suffix(self.registry_path.suffix + ".tmp")
        tmp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self.registry_path)

    @staticmethod
    def _validate_capability_id(capability_id: str) -> None:
        if not re.fullmatch(r"CAP-\d{3,}", capability_id):
            raise ValueError("capability_id must use CAP-NNN format")

    @staticmethod
    def _validate_version(version: str) -> None:
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            raise ValueError("version must use semantic version format")

    @staticmethod
    def _next_version(version: str) -> str:
        major, minor, patch = (int(part) for part in version.split("."))
        return f"{major}.{minor + 1}.0" if major == 0 else f"{major}.{minor + 1}.0"


__all__ = ["ImprovementDecision", "ImprovementComparison", "CapabilityImprovementEngine"]
