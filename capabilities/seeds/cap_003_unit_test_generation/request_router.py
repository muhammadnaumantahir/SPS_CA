"""Route explicit modification requests away from test generation."""

from __future__ import annotations

from capabilities.base import CapabilityContext, CapabilityResult
from capabilities.seeds.cap_003_unit_test_generation.capability import (
    _is_explicit_modification,
    run as generate_tests,
)
from capabilities.seeds.cap_009_natural_language_code_modification.capability import (
    run as modify_code,
)


def run(context: CapabilityContext) -> CapabilityResult:
    """Preserve the legacy router while delegating intent detection to CAP-003."""
    request = str(context.metadata.get("request", ""))
    if _is_explicit_modification(request):
        return modify_code(context)
    return generate_tests(context)
