"""Route explicit modification requests away from test generation."""

from __future__ import annotations

import re

from capabilities.base import CapabilityContext, CapabilityResult
from capabilities.seeds.cap_003_unit_test_generation.capability import run as generate_tests
from capabilities.seeds.cap_010_natural_language_code_modification.capability import run as modify_code

# These phrases describe a requested source-code change, not a request to
# generate tests. Keep the matcher conservative so ordinary "add tests" still
# reaches CAP-003.
_MODIFICATION_PATTERNS = (
    r"\badd\b.*\bfunction\b",
    r"\bcreate\b.*\bfunction\b",
    r"\bimplement\b.*\bfunction\b",
    r"\badd\b.*\bvalidation\b",
    r"\binput\s+validation\b",
    r"\bimplement\b.*\bvalidation\b",
    r"\bmodify\b.*\bcode\b",
    r"\bchange\b.*\bcode\b",
    r"\badd\b.*\bfeature\b",
    r"\bimplement\b.*\bfeature\b",
)


def _is_explicit_modification(request: str) -> bool:
    lowered = request.lower()
    return any(re.search(pattern, lowered, flags=re.DOTALL) for pattern in _MODIFICATION_PATTERNS)


def run(context: CapabilityContext) -> CapabilityResult:
    request = str(context.metadata.get("request", ""))
    if _is_explicit_modification(request):
        return modify_code(context)
    return generate_tests(context)
