"""
Layer 7: Governance Layer

Implements governance gates, DNA rule enforcement, risk assessment,
and audit trail logging for all SPS-CA decisions.

This layer ensures that all proposed changes (whether to user projects or
SPS-CA itself) comply with the Software DNA constraints and are assessed
for risk before approval.

Key components:
- GovernanceGate: Main class for making governance decisions
- DNARule: Immutable constraints that govern SPS-CA behavior
- GovernanceDecision: Complete record of a governance decision with audit trail
- RiskAssessment: Evaluation of change risk level
- DNAViolation: Record of DNA rule violations
"""

from .governance import GovernanceGate, GovernanceError
from .models import (
    DNARule,
    DNARuleSeverity,
    RiskLevel,
    RiskAssessment,
    DNAViolation,
    GovernanceDecision,
    DecisionStatus,
    ChangeType,
    GovernanceStats,
)

__version__ = "0.1.0"
__all__ = [
    "GovernanceGate",
    "GovernanceError",
    "DNARule",
    "DNARuleSeverity",
    "RiskLevel",
    "RiskAssessment",
    "DNAViolation",
    "GovernanceDecision",
    "DecisionStatus",
    "ChangeType",
    "GovernanceStats",
]
