"""
Models for Layer 7: Governance Layer.

Defines data structures for DNA rules, governance decisions, risk assessments,
and audit trail logging.
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DNARuleSeverity(str, Enum):
    """Severity levels for DNA rules."""
    HARD = "hard"      # Violation causes immediate rejection
    SOFT = "soft"      # Violation causes warning but may proceed


class RiskLevel(str, Enum):
    """Risk levels for proposed changes."""
    LOW = "low"           # Auto-approve, log decision
    MEDIUM = "medium"     # Log decision with rationale, may need review
    HIGH = "high"         # Escalate to human reviewer


class DecisionStatus(str, Enum):
    """Status of a governance decision."""
    AUTO_APPROVED = "auto_approved"           # Automatically approved (low risk)
    PENDING_HUMAN_REVIEW = "pending_human_review"  # Waiting for human approval
    APPROVED = "approved"                     # Approved by human
    REJECTED = "rejected"                     # Rejected by human or governance


class ChangeType(int, Enum):
    """Types of changes in the SPS-CA system."""
    SYNTAX_FIX = 1
    LOGIC_FIX = 2
    FEATURE_ADDITION = 3
    REFACTORING = 4
    TEST_GENERATION = 5
    ADAPTATION = 6
    EVOLUTION = 7


class DNARule(BaseModel):
    """
    Immutable rule that constrains SPS-CA behavior.
    
    DNA rules define what SPS-CA can and cannot do. They are part of the
    Software DNA (Layer 1) and are enforced by the Governance Layer (Layer 7).
    """
    model_config = ConfigDict(use_enum_values=False)
    
    id: str = Field(..., description="Unique rule identifier (e.g., rule_001)")
    constraint: str = Field(..., description="Natural language constraint")
    severity: DNARuleSeverity = Field(..., description="HARD or SOFT")
    affected_files: Optional[List[str]] = Field(
        default=None,
        description="List of files affected by this rule"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed explanation of the constraint"
    )
    created_date: datetime = Field(default_factory=datetime.now)


class RiskAssessment(BaseModel):
    """
    Risk assessment for a proposed change.
    
    Factors:
    - Scope: Does it modify core logic or capabilities?
    - Blast radius: How many downstream components could be affected?
    - Test coverage: Is the change well-tested?
    - Governance: Does it violate any DNA rules?
    """
    model_config = ConfigDict(use_enum_values=True)
    
    risk_level: RiskLevel = Field(..., description="LOW, MEDIUM, or HIGH")
    factors: List[str] = Field(
        default_factory=list,
        description="Reasons contributing to risk level"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in risk assessment (0.0-1.0)"
    )
    recommended_action: str = Field(
        ...,
        description="Recommended action (auto-approve, review, or reject)"
    )


class DNAViolation(BaseModel):
    """
    Record of a DNA rule violation detected in a proposed change.
    """
    model_config = ConfigDict(use_enum_values=False)
    
    rule_id: str = Field(..., description="ID of violated rule")
    rule_description: str = Field(..., description="Description of violated rule")
    severity: DNARuleSeverity = Field(..., description="HARD or SOFT")
    evidence: str = Field(..., description="How the violation was detected")
    timestamp: datetime = Field(default_factory=datetime.now)


class GovernanceDecision(BaseModel):
    """
    A governance decision record - the outcome of applying governance gates.
    
    Includes:
    - Change details
    - DNA violations (if any)
    - Risk assessment
    - Final decision
    - Audit trail
    """
    model_config = ConfigDict(use_enum_values=False)
    
    id: str = Field(..., description="Unique decision ID (e.g., decision_001)")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Change details
    change_id: str = Field(..., description="ID of the proposed change")
    change_type: ChangeType = Field(..., description="Type of change (1-7)")
    change_description: str = Field(..., description="Brief description of change")
    
    # Analysis results
    dna_violations: List[DNAViolation] = Field(
        default_factory=list,
        description="List of detected DNA violations"
    )
    risk_assessment: RiskAssessment = Field(..., description="Risk evaluation")
    
    # Decision outcome
    decision: DecisionStatus = Field(..., description="Final decision status")
    rationale: str = Field(..., description="Explanation for the decision")
    
    # Human review (if applicable)
    requires_human_approval: bool = Field(
        default=False,
        description="Whether human approval is required"
    )
    human_reviewer: Optional[str] = Field(
        default=None,
        description="Email or username of human reviewer"
    )
    human_approval_timestamp: Optional[datetime] = Field(
        default=None,
        description="When human approved/rejected"
    )
    
    # Additional context
    related_capabilities: Optional[List[str]] = Field(
        default=None,
        description="Capabilities affected by this change (e.g., CAP-001, CAP-002)"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes or context"
    )


class GovernanceStats(BaseModel):
    """
    Aggregated statistics about governance decisions.
    
    Used for reporting and analysis of governance effectiveness.
    """
    total_decisions: int = 0
    auto_approved: int = 0
    pending_human_review: int = 0
    approved_by_human: int = 0
    rejected: int = 0
    
    dna_violations_detected: int = 0
    high_risk_changes: int = 0
    average_decision_time_ms: float = 0.0
    
    decision_change_history: Dict[ChangeType, int] = Field(
        default_factory=dict,
        description="Count of decisions by change type"
    )

    @property
    def approval_rate(self) -> float:
        """Calculate approval rate."""
        if self.total_decisions == 0:
            return 0.0
        approved = self.auto_approved + self.approved_by_human
        return approved / self.total_decisions

    @property
    def rejection_rate(self) -> float:
        """Calculate rejection rate."""
        if self.total_decisions == 0:
            return 0.0
        return self.rejected / self.total_decisions
