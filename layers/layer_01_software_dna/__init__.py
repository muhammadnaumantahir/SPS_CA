"""Layer 01: Software DNA.

Immutable constraints and versioned capability metadata. This is the
foundation layer: every other layer's self-modifying actions are ultimately
checked against the rules loaded here.
"""

from .capability_template import CapabilityTemplate
from .dna_rule import DNARule
from .software_dna import DNACheckResult, DNAViolation, SoftwareDNA

__all__ = [
    "CapabilityTemplate",
    "DNARule",
    "SoftwareDNA",
    "DNACheckResult",
    "DNAViolation",
]
