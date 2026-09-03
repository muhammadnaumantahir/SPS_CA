"""Intent-aware composition of canonical SPS-CA capabilities."""

from __future__ import annotations

import re


_ACTIONS: tuple[tuple[str, str, int, tuple[str, ...]], ...] = (
    ("analysis", "CAP-003", 10, ("analy[sz]e", "explain", "understand", "walk me through")),
    ("diagnosis", "CAP-004", 20, ("find", "detect", "diagnos", "debug", "identify", "investigate")),
    ("generation", "CAP-001", 30, ("generate", "create", "write", "build", "develop", "make")),
    ("modification", "CAP-002", 40, ("add", "change", "modify", "update", "extend", "implement", "replace", "insert", "delete", "remove")),
    ("bug_fixing", "CAP-005", 50, ("fix", "repair", "resolve", "patch")),
    ("refactoring", "CAP-006", 60, ("refactor", "optim[iz]e", "cleanup", "clean up", "improve performance")),
    ("tests", "CAP-007", 70, ("test", "tests", "pytest", "unit test", "unit tests", "integration test", "integration tests")),
    ("documentation", "CAP-008", 80, ("document", "documentation", "docstring", "docstrings", "comment", "comments", "readme", "changelog", "guide")),
    ("validation", "CAP-009", 90, ("validate", "validation", "review", "check syntax", "check correctness", "code quality", "security review")),
    ("project_operations", "CAP-010", 100, ("create file", "add file", "delete file", "remove file", "move file", "rename file", "folder", "directory", "project structure", "project operation", "set up", "configure", "workspace", "repo", "repository", "deployment layout", "directory convention")),
)

_GENERATION_TARGET_RE = re.compile(r"\b(code|program|script|application|app|function|class|module|solution|implementation|utility|validator)\b", re.I)
_MODIFICATION_TARGET_RE = re.compile(
    r"\b(add|change|modify|update|extend|implement|replace|insert|delete|remove)\b.{0,55}"
    r"\b(code|function|class|method|logic|source|implementation|behavior|validation|logging|annotation|docstrings?|comments?|guard|error handling|cache|parameter|argument|input|output)\b",
    re.I,
)
_PROJECT_ARTIFACT_ACTION_RE = re.compile(
    r"\b(?:create|add|delete|remove|move|rename)\s+"
    r"(?:a|an|the|new)?\s*(?:file|folder|directory|project|module|package|workspace|layout)\b"
    r"|\b(?:set\s+up|restructure|reorganize)\s+(?:the\s+)?(?:project|workspace|repo(?:sitory)?|directory|layout)\b"
    r"|\b(?:configure)\s+(?:the\s+)?(?:project|workspace|repo(?:sitory)?|environment)\b"
    r"|\b(?:project\s+operation|project\s+structure|deployment\s+layout|directory\s+convention)\b",
    re.I,
)


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
    """Return a conservative capability chain only for explicit user actions."""
    req = " ".join((request or "").strip().split())
    if not req:
        return []

    hits: list[tuple[int, int, str, str]] = []
    for name, cid, rank, patterns in _ACTIONS:
        pos = _position(req, patterns)
        if pos is None or cid not in available_ids:
            continue
        if cid == "CAP-001" and not _GENERATION_TARGET_RE.search(req):
            continue
        if cid == "CAP-002":
            if not has_code or not _MODIFICATION_TARGET_RE.search(req):
                continue
            if re.search(r"\b(add|write|create|generate)\s+(?:new\s+)?(?:\w+\s+){0,2}tests?\b", req, re.I):
                code_change_signal = re.search(
                    r"\b(add|change|modify|update|extend|implement|replace|insert|delete|remove)\b.{0,60}"
                    r"\b(function|class|method|code|logic|source|implementation)\b",
                    req,
                    re.I,
                )
                if not code_change_signal:
                    continue
        if cid in {"CAP-004", "CAP-005"}:
            if not re.search(r"\b(find|detect|diagnos\w*|debug\w*|identify|investigate|fix|repair|resolve|patch)\b", req, re.I):
                continue
        if cid == "CAP-006" and not re.search(
            r"\b(?:refactor|optimi[sz]e|improve\s+performance)\b|"
            r"\b(?:clean\s+up|cleanup)\s+(?:the\s+)?(?:code|implementation|logic|source|function|class|method)\b",
            req,
            re.I,
        ):
            continue
        if cid == "CAP-009" and not re.search(r"\b(?:validate|review|re-?validate|check)\b", req, re.I):
            continue
        if cid == "CAP-010" and not _PROJECT_ARTIFACT_ACTION_RE.search(req):
            continue
        hits.append((rank, pos, cid, name))

    unique: dict[str, tuple[int, int, str, str]] = {}
    for hit in hits:
        unique.setdefault(hit[2], hit)
    ordered = sorted(unique.values(), key=lambda item: (item[0], item[1]))
    if len(ordered) <= 1:
        return []

    return [
        {"capability_id": cid, "reason": f"explicit user action requires {name.replace('_', ' ')}"}
        for _, _, cid, name in ordered
    ]


__all__ = ["compose_explicit_capabilities"]
