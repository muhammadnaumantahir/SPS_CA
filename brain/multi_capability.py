"""Intent-aware composition of canonical SPS-CA capabilities."""

from __future__ import annotations

import re
from typing import Any


_ACTIONS: tuple[tuple[str, str, int, tuple[str, ...]], ...] = (
    ("analysis", "CAP-003", 10, ("analy[sz]e", "explain", "understand", "walk me through", "review")),
    ("diagnosis", "CAP-004", 20, ("find", "detect", "diagnos", "debug", "identify")),
    ("generation", "CAP-001", 30, ("generate", "create", "write", "build", "develop", "make")),
    ("modification", "CAP-002", 40, ("add", "change", "modify", "update", "extend", "implement", "replace", "insert", "delete", "remove")),
    ("bug_fixing", "CAP-005", 50, ("fix", "repair", "resolve")),
    ("refactoring", "CAP-006", 60, ("refactor", "optim[iz]e", "cleanup", "clean up", "improve performance")),
    ("tests", "CAP-007", 70, ("test", "tests", "pytest", "unit test", "unit tests", "integration test", "integration tests")),
    ("documentation", "CAP-008", 80, ("document", "documentation", "docstring", "docstrings", "comment", "comments", "readme")),
    ("validation", "CAP-009", 90, ("validate", "validation", "check syntax", "check correctness", "code quality", "security review")),
    ("project_operations", "CAP-010", 100, ("create file", "add file", "delete file", "remove file", "move file", "rename file", "folder", "directory", "project structure")),
)

# Generation verbs are only a generation signal when the request actually talks
# about source/program/code/function creation. This prevents "write tests" from
# accidentally becoming CAP-001 + CAP-007.
_GENERATION_TARGET_RE = re.compile(r"\b(code|program|script|application|app|function|class|module|solution|implementation)\b", re.I)


def _position(request: str, patterns: tuple[str, ...]) -> int | None:
    matches = [re.search(rf"\b{pattern}\w*\b", request, re.I) for pattern in patterns]
    starts = [match.start() for match in matches if match]
    return min(starts) if starts else None


def compose_explicit_capabilities(
    request: str,
    *,
    has_code: bool,
    available_ids: set[str],
) -> list[dict[str, str]]:
    """Return a deterministic, explicit multi-capability chain.

    The function is deliberately conservative: a capability is added only when
    the user's wording contains a direct action signal. In particular, tests are
    never inferred from an ordinary code change.
    """
    req = " ".join((request or "").strip().split())
    if not req:
        return []
    hits: list[tuple[int, int, str, str, str]] = []
    for name, cid, rank, patterns in _ACTIONS:
        pos = _position(req, patterns)
        if pos is None:
            continue
        if cid == "CAP-001" and not _GENERATION_TARGET_RE.search(req):
            continue
        if cid == "CAP-002" and not has_code:
            continue
        if cid == "CAP-004" and not re.search(r"\b(bug|error|issue|exception|failure|problem|defect)\b", req, re.I):
            continue
        if cid == "CAP-005" and not re.search(r"\b(bug|error|issue|exception|failure|problem|defect)\b", req, re.I):
            continue
        if cid not in available_ids:
            continue
        hits.append((rank, pos, cid, name, patterns[0]))

    # Explicit combinations are dependency-aware; single-intent requests retain
    # exactly one capability. When several actions are present we execute in the
    # safe SPS order rather than letting provider wording reorder dependencies.
    unique: dict[str, tuple[int, int, str, str, str]] = {}
    for hit in hits:
        unique.setdefault(hit[2], hit)
    ordered = sorted(unique.values(), key=lambda item: (item[0], item[1]))
    if len(ordered) <= 1:
        return []

    return [
        {"capability_id": cid, "reason": f"explicit user action requires {name.replace('_', ' ')}"}
        for _, _, cid, name, _ in ordered
    ]


__all__ = ["compose_explicit_capabilities"]
