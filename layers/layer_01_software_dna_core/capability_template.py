"""Capability versioning model.

A ``Capability`` is the unit of executable, versioned functionality that
SPS-CA either ships with (a "seed" capability) or generates for itself
(an "evolved" capability, see Layer 8). ``CapabilityTemplate`` defines the
metadata shape shared by both, including a semantic-versioning scheme.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal, Optional

_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_CAP_ID_RE = re.compile(r"^CAP-\d{3,}$")

CapabilityOrigin = Literal["seed", "generated"]
CapabilityStatus = Literal["draft", "active", "deprecated", "rejected"]


@dataclass
class CapabilityTemplate:
    """Metadata describing a single versioned capability.

    Attributes:
        id: Stable capability identifier, e.g. ``"CAP-001"``.
        name: Human-readable name.
        version: Semantic version string ``MAJOR.MINOR.PATCH``.
        description: What the capability does.
        entry_point: Dotted path to the callable that implements the
            capability, e.g. ``"capabilities.seeds.cap_001_bug_detection.run"``.
        origin: ``"seed"`` (shipped) or ``"generated"`` (produced by Evolution).
        status: Lifecycle status.
        target_languages: Languages this capability can operate on.
        parent_capability_id: For generated capabilities, the capability
            (if any) this one was derived from. ``None`` for seeds.
        tags: Free-form classification tags.
    """

    id: str
    name: str
    version: str
    description: str
    entry_point: str
    origin: CapabilityOrigin = "seed"
    status: CapabilityStatus = "draft"
    target_languages: list = field(default_factory=list)
    parent_capability_id: Optional[str] = None
    tags: list = field(default_factory=list)

    def __post_init__(self) -> None:
        if not _CAP_ID_RE.match(self.id):
            raise ValueError(f"Capability id must look like 'CAP-001', got {self.id!r}")
        if not _SEMVER_RE.match(self.version):
            raise ValueError(
                f"Capability version must be MAJOR.MINOR.PATCH, got {self.version!r}"
            )

    def next_version(self, bump: Literal["major", "minor", "patch"] = "patch") -> str:
        """Return the next semantic version string for a given bump level."""
        major, minor, patch = (int(part) for part in self.version.split("."))
        if bump == "major":
            major, minor, patch = major + 1, 0, 0
        elif bump == "minor":
            minor, patch = minor + 1, 0
        elif bump == "patch":
            patch += 1
        else:
            raise ValueError(f"Unknown bump level: {bump!r}")
        return f"{major}.{minor}.{patch}"

    @classmethod
    def from_dict(cls, data: dict) -> "CapabilityTemplate":
        return cls(
            id=data["id"],
            name=data["name"],
            version=data.get("version", "0.1.0"),
            description=data.get("description", ""),
            entry_point=data["entry_point"],
            origin=data.get("origin", "seed"),
            status=data.get("status", "draft"),
            target_languages=list(data.get("target_languages", [])),
            parent_capability_id=data.get("parent_capability_id"),
            tags=list(data.get("tags", [])),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "entry_point": self.entry_point,
            "origin": self.origin,
            "status": self.status,
            "target_languages": self.target_languages,
            "parent_capability_id": self.parent_capability_id,
            "tags": self.tags,
        }
