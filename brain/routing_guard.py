"""Deterministic routing guard for the replaceable Brain.

The LLM may reason about a plan, but a clear user instruction must win over
keyword collisions. In particular, words such as "testing" or "test" inside
a modification request must not silently route the task to CAP-007.
"""

from __future__ import annotations

import re
from typing import Callable

_MODIFICATION = re.compile(
    r"\b(add|change|modify|update|extend|implement|replace|remove|insert|delete|fix)\b"
)
_EXPLICIT_TEST = re.compile(
    r"\b(generate|write|create|add|update)\s+(?:new\s+)?(?:unit\s+|integration\s+|pytest\s+)?tests?\b"
    r"|\btests?\s+for\b|\bpytest\s+tests?\b|\bunit\s+tests?\b",
    re.IGNORECASE,
)


def intent_guard(original: Callable[..., str], request: str, code: str = "", file_path: str = "") -> str:
    """Return the original classification except for an unambiguous conflict."""
    result = original(request, code, file_path)
    req = " ".join((request or "").lower().split())
    if not code.strip():
        return result
    if result != "test_generation":
        return result
    # "Add/modify X ... testing" is a code change unless the user explicitly
    # asked to create/update tests. This prevents CAP-007 from hijacking CAP-002.
    if _MODIFICATION.search(req) and not _EXPLICIT_TEST.search(req):
        return "code_modification"
    return result
