"""Deterministic routing guard for the replaceable Brain.

The LLM may reason about a plan, but a clear user instruction must win over
keyword collisions. The guard distinguishes task-level actions from supporting
nouns/context so the Brain does not classify ordinary implementation details as
additional intents.
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

_SEPARATE_ACTION_BOUNDARY = re.compile(
    r"\b(?:then|after\s+that|afterwards)\b|,\s*(?:then|and\s+then)\b|\band\s+(?:also\s+)?(?:then\s+)?"
    r"(?:analyze|analyse|explain|diagnose|debug|identify|find|fix|repair|resolve|patch|refactor|optimi[sz]e|validate|review|check|generate|create|write|modify|update|add|remove|delete|rename|move|document)\b",
    re.IGNORECASE,
)

# Validation is a separate intent only when the user explicitly asks for a
# validation action. A noun such as "validation" or a target such as
# "input validation" belongs to the implementation request.
_SEPARATE_VALIDATION_ACTION = re.compile(
    r"(?:^|\b(?:then|and then)\b|,\s*(?:then|and)?\s*)"
    r"(?:please\s+)?(?:validate|review|re-validate|check)\b",
    re.IGNORECASE,
)


def _intent_signals(request: str, *, has_code: bool) -> list[str]:
    """Return task-level intent signals while ignoring supporting context words."""
    req = " ".join((request or "").lower().split())
    signals: list[str] = []

    def add(intent: str, pattern: str) -> None:
        if intent not in signals and re.search(pattern, req, re.IGNORECASE):
            signals.append(intent)

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
        r"\b(find|detect|diagnos(?:e|is)|debug|identify|investigate)\w*\b"
        r"(?:.{0,80}\b(root\s+cause|bug|error|issue|exception|failure|defect|problem|risk|race\s+condition|deadlock|memory\s+leak|vulnerability|corruption)\b)?",
    )
    add("bug_fixing", r"\b(fix|repair|resolve|patch)\b")

    # Refactoring must represent an explicit code action. Phrases such as
    # "resource cleanup" are implementation details of another requested task,
    # not a separate refactoring intent.
    add(
        "refactoring",
        r"\brefactor\b|\boptimi[sz]e\b|\bimprove\s+performance\b|"
        r"\b(?:clean\s+up|cleanup)\s+(?:the\s+)?(?:code|implementation|logic|source|function|class|method)\b",
    )
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

    # Project operations require an operation whose object is a project/file
    # artifact. Merely mentioning "file", "folder", "repo", or "module" as
    # context must never turn a code-generation/modification request into mixed.
    project_action = bool(
        re.search(
            r"\b(?:create|add|delete|remove|move|rename)\b.{0,50}"
            r"\b(?:file|folder|directory|project|module|package|workspace|layout)\b",
            req,
            re.IGNORECASE,
        )
        or re.search(
            r"\b(?:project\s+operation|project\s+structure|set\s+up|configure|restructure|reorganize|workspace|repo(?:sitory)?|deployment\s+layout|directory\s+convention)\b",
            req,
            re.IGNORECASE,
        )
    )
    if project_action:
        add(
            "project_operations",
            r"\b(?:project\s+operation|project\s+structure|set\s+up|configure|restructure|reorganize|workspace|repo(?:sitory)?|deployment\s+layout|directory\s+convention|(?:create|add|delete|remove|move|rename)\b.{0,50}\b(?:file|folder|directory|project|module|package|workspace|layout))\b",
        )

    # Supporting validation language in a generation/modification request is
    # part of the requested implementation unless validation is a separate
    # action clause. The same principle applies to documentation embedded in a
    # modification request.
    if "validation" in signals and (
        "code_generation" in signals or "code_modification" in signals
    ) and not _SEPARATE_VALIDATION_ACTION.search(req):
        signals.remove("validation")

    if "code_modification" in signals and "validation" in signals and _MODIFICATION_TARGET.search(req):
        if not _SEPARATE_VALIDATION_ACTION.search(req):
            signals.remove("validation")

    if "code_modification" in signals and "documentation" in signals and not _SEPARATE_ACTION_BOUNDARY.search(req):
        signals.remove("documentation")

    # Diagnosis + explanation is normally one task: explain the root cause of
    # the diagnosed defect. It becomes mixed only when the user explicitly asks
    # for a second action clause (for example, "diagnose it, then explain it").
    if "bug_diagnosis" in signals and "analysis" in signals and not _SEPARATE_ACTION_BOUNDARY.search(req):
        signals.remove("analysis")

    # Generation/modification takes precedence over project context unless the
    # user explicitly requests a project/file operation as another action.
    if "project_operations" in signals and (
        "code_generation" in signals or "code_modification" in signals
    ) and not re.search(
        r"\b(?:then|after\s+that|afterwards)\b|,\s*(?:then|and\s+then)\b|\band\s+(?:also\s+)?(?:create|add|delete|remove|move|rename)\s+(?:a\s+)?(?:file|folder|directory|project|module|package|workspace)\b",
        req,
        re.IGNORECASE,
    ):
        signals.remove("project_operations")

    return signals


def intent_guard(original: Callable[..., str], request: str, code: str = "", file_path: str = "") -> str:
    """Return an action-aware classification over the Brain's native guess."""
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
