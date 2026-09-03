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
_MODIFICATION_TARGET = re.compile(
    r"\b(add|change|modify|update|extend|implement|replace|insert|delete|remove)\b.{0,55}"
    r"\b(code|function|class|method|logic|source|implementation|behavior|validation|logging|annotation|docstrings?|comments?|guard|error handling|cache|parameter|argument|input|output)\b",
    re.IGNORECASE,
)
_EXPLICIT_TEST = re.compile(
    r"\b(generate|write|create|add|update)\s+(?:new\s+)?(?:unit\s+|integration\s+|pytest\s+)?tests?\b"
    r"|\btests?\s+for\b|\bpytest\s+tests?\b|\bunit\s+tests?\b",
    re.IGNORECASE,
)

# Validation is a separate intent only when the user explicitly asks for a
# validation action. A noun such as "validation" or a relative clause such as
# "supports validation" is part of the requested implementation target.
_SEPARATE_VALIDATION_ACTION = re.compile(
    r"(?:^|\b(?:then|and then)\b|,\s*(?:then|and)?\s*)"
    r"(?:please\s+)?(?:validate|review|re-validate|check)\b",
    re.IGNORECASE,
)


def _intent_signals(request: str, *, has_code: bool) -> list[str]:
    """Return distinct task-level intent signals in a stable capability order.

    Signals are scoped to action clauses so target nouns such as "validation"
    or "function" do not become accidental secondary intents.
    """
    req = " ".join((request or "").lower().split())
    signals: list[str] = []

    def add(intent: str, pattern: str) -> None:
        if intent not in signals and re.search(pattern, req, re.IGNORECASE):
            signals.append(intent)

    # A code-generation target must appear before any test noun in the same
    # clause. Otherwise "Create tests for this function" is misread as code
    # generation because the trailing word "function" happens to match.
    generation_clause = (
        r"(?:^|\b(?:then|and then)\b|,\s*)"
        r"(generate|write|create|build|develop|make)\b"
        r"(?![^,]{0,80}\b(?:unit\s+|integration\s+|pytest\s+)?tests?\b)"
        r"[^,]{0,80}\b(code|program|script|application|app|function|class|solution|utility|validator)\b"
    )
    add("code_generation", generation_clause)

    add("test_generation", _EXPLICIT_TEST.pattern)
    add(
        "bug_diagnosis",
        r"\b(find|detect|diagnos(?:e|is)|debug|identify|investigate)\w*\b(?:.{0,80}\b(root\s+cause|bug|error|issue|exception|failure|defect|problem|risk|race\s+condition|deadlock|memory\s+leak|vulnerability|corruption)\b)?",
    )
    add("bug_fixing", r"\b(fix|repair|resolve|patch)\b")
    add("refactoring", r"\b(refactor|optimi[sz]e|cleanup|clean\s+up|improve\s+performance)\b")
    add("analysis", r"\b(explain|explanation|analy[sz]e|understand|walk\s+me\s+through|what\s+does|how\s+does)\b")

    validation_signal = r"\b(validate|validation|review|re-?validate|check\s+(?:syntax|correctness)|code\s+quality|security\s+review)\b"
    add("validation", validation_signal)

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

    if has_code and _MODIFICATION_TARGET.search(req):
        if not (_EXPLICIT_TEST.search(req) and not re.search(
            r"\b(add|change|modify|update|extend|implement|replace|insert|delete|remove)\b.{0,50}\b(code|function|class|logic|source|implementation)\b",
            req,
            re.IGNORECASE,
        )):
            add("code_modification", _MODIFICATION_TARGET.pattern)

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

    # Validation words embedded in a generation/modification target are not a
    # second task. Only an explicit validation action (e.g. "then validate")
    # keeps validation as a distinct signal and therefore produces "mixed".
    if "validation" in signals and (
        "code_generation" in signals or "code_modification" in signals
    ) and not _SEPARATE_VALIDATION_ACTION.search(req):
        signals.remove("validation")

    # A target noun such as "input validation" belongs to the modification
    # capability when it is the single requested action. It becomes mixed only
    # when a separate validation action is explicitly requested.
    if "code_modification" in signals and "validation" in signals and _MODIFICATION_TARGET.search(req):
        if not re.search(r"\b(?:then|and then)\b|,\s*(?:then|and)\b|\band\s+(?:review|validate|re-validate|check)\b", req, re.IGNORECASE):
            signals.remove("validation")

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
        if signal == "code_generation" and has_code:
            return result if result not in {"unknown", "code_generation"} else "code_modification"
        return signal

    if not has_code:
        return result
    if result != "test_generation":
        return result
    if _MODIFICATION.search(" ".join((request or "").lower().split())) and not _EXPLICIT_TEST.search(request or ""):
        return "code_modification"
    return result
