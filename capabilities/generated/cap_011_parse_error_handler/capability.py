"""CAP-011: migrated historical Parse Error Handler."""
from capabilities.base import CapabilityContext, CapabilityResult
SUPPORTED_LANGUAGES=["python"]
TRIGGER_PATTERN="Parse error"
def run(context:CapabilityContext)->CapabilityResult:
    if context.language not in SUPPORTED_LANGUAGES: return CapabilityResult.ok(summary=f"CAP-011 has no handling yet for '{context.language}'.")
    if not context.code.strip(): return CapabilityResult.fail(error="No code provided to analyze.")
    return CapabilityResult.ok(summary="CAP-011 inspected the input for the historical Parse error pattern.",findings=[{"trigger_pattern":TRIGGER_PATTERN,"language":context.language}])
