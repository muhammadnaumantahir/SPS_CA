"""
SPS-CA Core: 10-Layer Implementation

This package contains the complete architecture for Self-Programming Software (SPS).

Layers:
  1. Layer 1: Software DNA - Immutable constraints and seed capabilities
  2. Layer 2: Governance - Decision gates and risk assessment
  3. Layer 3: Cognitive Core - Planning, analysis, and Brain interface
  4. Layer 4: Knowledge Core - Structured domain knowledge
  5. Layer 5: Experience Core - Task history and feedback
  6. Layer 6: Meta-Learning Core - Strategy improvement
  7. Layer 7: Adaptation Core - Context-aware behavior adjustment
  8. Layer 8: Evolution Core - Capability generation and controlled self-programming
  9. Layer 9: Verification & Validation - Sandboxed testing
  10. Layer 10: Execution - Safe application and rollback

The application-facing SelfProgrammingService is a facade only; self-modification
remains owned by Layer 8 and must pass the Layer 1, Layer 2, Layer 9, and Layer 10
boundaries.
"""

from .self_programming_service import SelfProgrammingService
from .assistant_service import SpsAssistantService


# Enrich the catalog presented to Brain so generated capabilities can declare
# their own intent eligibility. Canonical capabilities retain the same IDs and
# remain the default fallback when Layer 6 has insufficient evidence.
_original_capability_catalog = SpsAssistantService.capability_catalog


def _rich_capability_catalog(self: SpsAssistantService) -> list[dict]:
    catalog = _original_capability_catalog(self)
    enriched = []
    for item, capability in zip(catalog, self.registry.list_all_capabilities()):
        if capability.status != "active":
            continue
        record = dict(item)
        for field in (
            "intent_class",
            "allowed_intents",
            "forbidden_intents",
            "risk_level",
            "supported_languages",
        ):
            value = getattr(capability, field, None)
            if value is not None:
                record[field] = list(value) if isinstance(value, (list, tuple, set)) else value
        enriched.append(record)
    return enriched


SpsAssistantService.capability_catalog = _rich_capability_catalog

__all__ = ["SelfProgrammingService", "SpsAssistantService"]
