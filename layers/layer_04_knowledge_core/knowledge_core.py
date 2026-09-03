"""Structured knowledge services for canonical SPS-CA layer 4."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass(frozen=True)
class KnowledgeSnapshot:
    """Immutable knowledge projection supplied to the Cognitive Layer."""

    language: str
    file_path: str
    symbols: tuple[str, ...] = ()
    capabilities: tuple[dict[str, Any], ...] = ()
    facts: dict[str, Any] = field(default_factory=dict)


class KnowledgeCore:
    """Owns structured, reusable knowledge rather than task execution."""

    def build_snapshot(
        self,
        *,
        language: str,
        file_path: str,
        symbols: Iterable[str] = (),
        capabilities: Iterable[dict[str, Any]] = (),
        facts: dict[str, Any] | None = None,
    ) -> KnowledgeSnapshot:
        normalized_capabilities = tuple(
            {
                "id": str(item.get("id", "")),
                "name": str(item.get("name", "")),
                "description": str(item.get("description", "")),
                "tags": tuple(str(tag) for tag in item.get("tags", [])),
            }
            for item in capabilities
            if item.get("id")
        )
        return KnowledgeSnapshot(
            language=language,
            file_path=file_path,
            symbols=tuple(str(symbol) for symbol in symbols if str(symbol).strip()),
            capabilities=normalized_capabilities,
            facts=dict(facts or {}),
        )

    def validate(self, snapshot: KnowledgeSnapshot) -> bool:
        """Reject malformed knowledge snapshots before they enter reasoning."""
        if not snapshot.language.strip() or not snapshot.file_path.strip():
            return False
        return all(cap.get("id") and cap.get("name") for cap in snapshot.capabilities)
