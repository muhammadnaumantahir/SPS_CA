"""Deterministic routing guard for the replaceable Brain.

The LLM may reason about a plan, but a clear user instruction must win over
keyword collisions. In particular, words such as "testing" or "test" inside
a modification request must not silently route the task to CAP-007.
"""

from __future__ import annotations

import re
from typing import Callable


_MODIFICATION = re.compile(
    r"\b(add|change|modify|update|extend|implement|replace|insert|delete|remove)\b"
)
_EXPLICIT_TEST = re.compile(
    r"\b(generate|write|create|add|update)\s+(?:new\s+)?(?:unit\s+|integration\s+|pytest\s+)?tests?\b"
    r"|\btests?\s+for\b|\bpytest\s+tests?\b|\bunit\s+tests?\b",
    re.IGNORECASE,
)


def _intent_signals(request: str, *, has_code: bool) -> list[str]:
    """Return distinct task-level intent signals in a stable capability order.

    The guard is deliberately clause-oriented: a request to "add a docstring"
    is one modification, while "fix the bug and document the fix" contains two
    explicit actions and must be classified as mixed.
    """
    req = " ".join((request or "").lower().split())
    signals: list[str] = []

    def add(intent: str, pattern: str) -> None:
        if intent not in signals and re.search(pattern, req, re.IGNORECASE):
            signals.append(intent)

    add(
        "code_generation",
        r"\b(generate|write|create|build|develop|make)\b.{0,80}\b(code|program|script|application|app|function|class|solution|utility)\b",
    )
    add("test_generation", _EXPLICIT_TEST.pattern)
    add(
        "bug_diagnosis",
        r"\b(find|detect|diagnos(?:e|is)|debug|identify|investigate)\w*\b(?:.{0,80}\b(root\s+cause|bug|error|issue|exception|failure|defect|problem|risk|race\s+condition|deadlock|memory\s+leak|vulnerability|corruption)\b)?",
    )
    add("bug_fixing", r"\b(fix|repair|resolve|patch)\b")
    add("refactoring", r"\b(refactor|optimi[sz]e|cleanup|clean\s+up|improve\s+performance)\b")
    add("analysis", r"\b(explain|explanation|analy[sz]e|understand|walk\s+me\s+through|what\s+does|how\s+does)\b")
    add("validation", r"\b(validate|validation|review|re-?validate|check\s+(?:syntax|correctness)|code\s+quality|security\s+review)\b")

    # Documentation is a distinct action only when documentation itself is the
    # verb/object of the request. "Add a docstring" modifies existing source;
    # it should remain code_modification rather than becoming mixed.
    doc_action = bool(
        re.search(
            r"\b(document|write|generate|create)\b.{0,40}\b(documentation|docs?|docstrings?|comments?|readme|changelog|guide)\b"
            r"|\b(?:document|documenting|add|write|generate|create)\b.{0,25}\b(?:the\s+)?(?:fix|change|result|resulting\s+behavior)\b"
            r"|\b(?:document|documentation|docstring|comments?|readme)\s+(?:this|the|it)\b",
            req,
            re.IGNORECASE,
        )
    )
    if doc_action and not (
        has_code
        and re.search(
            r"\b(add|change|modify|update|extend|implement|replace|insert|delete|remove)\b.{0,30}\b(docstrings?|comments?|readme|documentation|docs?)\b",
            req,
            re.IGNORECASE,
        )
        and len(re.findall(r"\bthen\b|,", req)) == 0
    ):
        add("documentation", r"\b(document|documentation|docstring|docstrings?|comments?|readme|changelog|guide)\b")

    modification_action = bool(_MODIFICATION.search(req)) and has_code
    if modification_action:
        # "Add tests for this function" is testing, not a generic modification.
        if not (_EXPLICIT_TEST.search(req) and not re.search(r"\b(add|change|modify|update|extend|implement|replace|insert|delete|remove)\b.{0,50}\b(code|function|class|logic|source|implementation)\b", req, re.IGNORECASE)):
            add("code_modification", _MODIFICATION.pattern)

    project_action = bool(
        re.search(
            r"\b(project\s+operation|project\s+structure|set\s+up|configure|restructure|reorganize|workspace|repo(?:sitory)?|deployment\s+layout|directory\s+convention|file|folder|directory|package|module)\b",
            req,
            re.IGNORECASE,
        )
        and not has_code
    ) or bool(
        re.search(
            r"\b(create|add|delete|remove|move|rename)\b.{0,50}\b(file|folder|directory|project|module|package|workspace|layout)\b",
            req,
            re.IGNORECASE,
        )
    )
    if project_action:
        add("project_operations", r"\b(?:project\s+operation|project\s+structure|set\s+up|configure|restructure|reorganize|workspace|repo(?:sitory)?|deployment\s+layout|directory\s+convention|file|folder|directory|package|module)\b")

    # Existing-source modification must win over a documentation noun, but
    # explicit multi-clause requests still produce mixed.
    if len(signals) > 1:
        if "code_modification" in signals and "documentation" in signals and re.search(
            r"\b(?:add|change|modify|update|extend|implement|replace|insert|delete|remove)\b.{0,35}\b(?:docstrings?|comments?|readme|documentation|docs?)\b",
            req,
            re.IGNORECASE,
        ) and not re.search(r"\b(?:then|and then)\b|,\s*(?:then|and)\b", req, re.IGNORECASE):
            signals.remove("documentation")
        if len(signals) > 1:
            return signals

    return signals


def intent_guard(original: Callable[..., str], request: str, code: str = "", file_path: str = "") -> str:
    """Return a deterministic, action-aware classification over the Brain guess."""
    result = original(request, code, file_path)
    has_code = bool((code or "").strip())
    signals = _intent_signals(request, has_code=has_code)

    if len(signals) > 1:
        return "mixed"
    if len(signals) == 1:
        signal = signals[0]
        # Preserve explicit code-generation requests with no supplied source.
        if signal == "code_generation" and has_code:
            return result if result not in {"unknown", "code_generation"} else "code_modification"
        return signal

    if not has_code:
        return result
    if result != "test_generation":
        return result
    # "Add/modify X ... testing" is a code change unless the user explicitly
    # asked to create/update tests. This prevents CAP-007 from hijacking CAP-002.
    if _MODIFICATION.search(" ".join((request or "").lower().split())) and not _EXPLICIT_TEST.search(request or ""):
        return "code_modification"
    return result
