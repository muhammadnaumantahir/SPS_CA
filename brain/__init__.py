"""Provider-neutral SPS-CA brain subsystem."""

from .brain import Brain, BrainPlan, BrainError
from .routing_guard import intent_guard

# Preserve the existing Brain API while adding a deterministic final guard.
# The Brain remains replaceable and the guard only resolves an explicit
# modification-vs-test ambiguity; it does not create or execute capabilities.
_original_infer_intent_class = Brain.infer_intent_class


def _guarded_infer_intent_class(request: str, code: str = "", file_path: str = "") -> str:
    return intent_guard(_original_infer_intent_class, request, code, file_path)


Brain.infer_intent_class = staticmethod(_guarded_infer_intent_class)

__all__ = ["Brain", "BrainPlan", "BrainError"]
