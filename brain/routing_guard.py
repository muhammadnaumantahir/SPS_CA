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

# Only an explicit sequencing phrase establishes a second task boundary. A
# plain "and explain" commonly gives supporting detail for the first action.
_EXPLICIT_CHAIN_BOUNDARY = re.compile(
    r"\b(?:then|after\s+that|afterwards)\b|,\s*(?:then|and\s+then)\b",
    re.IGNORECASE,
)

_SEPARATE_VALIDATION_ACTION = re.compile(
    r"(?:^|\b(?:then|and then)\b|,\s*(?:then|and)?\s*)"
    r"(?:please\s+)?(?:validate|review|re-validate|check)\b",
    re.IGNORECASE,
)


# A project operation must act directly on a project artifact. Requiring the
# artifact to follow the operation verb prevents phrases such as
# "create a Python function for file processing" from becoming project ops.
_PROJECT_ARTIFACT_ACTION = re.compile(
    r"\b(?:create|add|delete|remove|move|rename)\s+"
    r"(?:a|an|the|new)?\s*(?:file|folder|directory|project|module|package|workspace|layout)\b"
    r"|\b(?:set\s+up|restructure|reorganize)\s+(?:the\s+)?(?:project|workspace|repo(?:sitory)?|directory|layout)\b"
    r"|\b(?:configure)\s+(?:the\s+)?(?:project|workspace|repo(?:sitory)?|environment)\b"
    r"|\b(?:project\s+operation|project\s+structure|deployment\s+layout|directory\s+convention)\b",
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

    if _PROJECT_ARTIFACT_ACTION.search(req):
        add("project_operations", _PROJECT_ARTIFACT_ACTION.pattern)

    if "validation" in signals and (
        "code_generation" in signals or "code_modification" in signals
    ) and not _SEPARATE_VALIDATION_ACTION.search(req):
        signals.remove("validation")

    if "code_modification" in signals and "validation" in signals and _MODIFICATION_TARGET.search(req):
        if not _SEPARATE_VALIDATION_ACTION.search(req):
            signals.remove("validation")

    if "code_modification" in signals and "documentation" in signals and not _EXPLICIT_CHAIN_BOUNDARY.search(req):
        signals.remove("documentation")

    # Diagnosis + explanation is one task by default: the explanation supplies
    # the root-cause detail for the diagnosis. It becomes mixed only when the
    # request explicitly sequences the explanation as a follow-up task.
    if "bug_diagnosis" in signals and "analysis" in signals and not _EXPLICIT_CHAIN_BOUNDARY.search(req):
        signals.remove("analysis")

    # Generation/modification takes precedence over project context unless the
    # project artifact action is explicitly requested as another task.
    if "project_operations" in signals and (
        "code_generation" in signals or "code_modification" in signals
    ) and not re.search(
        r"\b(?:then|after\s+that|afterwards)\b|,\s*(?:then|and\s+then)\b|\band\s+(?:also\s+)?(?:create|add|delete|remove|move|rename)\s+(?:a|an|the|new)?\s*(?:file|folder|directory|project|module|package|workspace|layout)\b",
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
