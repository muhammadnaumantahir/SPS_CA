"""
Layer 7: Governance Layer

Implements governance gates, DNA rule enforcement, risk assessment,
and audit trail logging for all SPS-CA decisions.

This layer ensures that all proposed changes (whether to user projects or
SPS-CA itself) comply with the Software DNA constraints and are assessed
for risk before approval.
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging

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


logger = logging.getLogger(__name__)


class GovernanceError(Exception):
    """Raised when governance decision cannot be made."""
    pass


class GovernanceGate:
    """
    Enforces governance policies and DNA constraints.
    
    Responsibilities:
    - Load and validate DNA rules
    - Check proposed changes for DNA violations
    - Assess risk levels of changes
    - Make approval/rejection decisions
    - Log all decisions to audit trail
    - Escalate high-risk changes to human review
    
    All SPS-CA changes must pass through this gate.
    """

    def __init__(self, dna_rules_path: str = None, decisions_dir: str = None):
        """
        Initialize governance gate.

        Args:
            dna_rules_path: Path to DNA rules JSON file
            decisions_dir: Directory to store decision logs
        """
        self.dna_rules: Dict[str, DNARule] = {}
        self.decisions: List[GovernanceDecision] = []
        self.stats = GovernanceStats()

        # Load DNA rules
        if dna_rules_path:
            self.load_dna_rules(dna_rules_path)
        else:
            self._initialize_default_rules()

        # Setup decisions directory
        self.decisions_dir = Path(decisions_dir or "governance/decisions")
        self.decisions_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"GovernanceGate initialized with {len(self.dna_rules)} DNA rules")

    def _initialize_default_rules(self):
        """Initialize default DNA rules."""
        default_rules = [
            DNARule(
                id="rule_001",
                constraint="Never modify core governance logic (Layer 7)",
                severity=DNARuleSeverity.HARD,
                affected_files=["layers/layer_07_governance/governance.py"],
                description="Governance logic must remain immutable to prevent self-modification of controls"
            ),
            DNARule(
                id="rule_002",
                constraint="Never modify existing seed capabilities (only version-bump)",
                severity=DNARuleSeverity.HARD,
                affected_files=["capabilities/seeds/*/capability.py"],
                description="Seed capability lineage must be preserved for reproducibility"
            ),
            DNARule(
                id="rule_003",
                constraint="All generated capabilities must have >80% test coverage",
                severity=DNARuleSeverity.SOFT,
                affected_files=["capabilities/generated/*/tests.py"],
                description="Generated code quality must meet minimum standards"
            ),
            DNARule(
                id="rule_004",
                constraint="Never modify DNA rules without explicit approval",
                severity=DNARuleSeverity.HARD,
                affected_files=["layers/layer_01_software_dna/", "governance/dna_rules.json"],
                description="DNA rules define system boundaries and cannot be self-modified"
            ),
        ]

        for rule in default_rules:
            self.dna_rules[rule.id] = rule

        logger.info(f"Initialized {len(default_rules)} default DNA rules")

    def load_dna_rules(self, dna_rules_path: str):
        """
        Load DNA rules from JSON file.

        Args:
            dna_rules_path: Path to DNA rules JSON
        """
        path = Path(dna_rules_path)
        if not path.exists():
            logger.warning(f"DNA rules file not found: {dna_rules_path}")
            self._initialize_default_rules()
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for rule_data in data.get("dna_rules", []):
                rule = DNARule(**rule_data)
                self.dna_rules[rule.id] = rule

            logger.info(f"Loaded {len(self.dna_rules)} DNA rules from {dna_rules_path}")
        except Exception as e:
            logger.error(f"Failed to load DNA rules: {e}")
            self._initialize_default_rules()

    def check_dna_violations(
        self,
        change_id: str,
        affected_files: List[str],
        change_type: ChangeType
    ) -> Tuple[List[DNAViolation], bool]:
        """
        Check if a proposed change violates any DNA rules.

        Args:
            change_id: ID of the change
            affected_files: Files that would be modified
            change_type: Type of change (1-7)

        Returns:
            Tuple of (violations list, has_hard_violations boolean)
        """
        violations: List[DNAViolation] = []
        has_hard_violations = False

        for rule in self.dna_rules.values():
            # Check if this rule applies to affected files
            if not rule.affected_files:
                continue

            for pattern in rule.affected_files:
                # Simple pattern matching (in production, use glob)
                for affected_file in affected_files:
                    if self._pattern_matches(pattern, affected_file):
                        violation = DNAViolation(
                            rule_id=rule.id,
                            rule_description=rule.constraint,
                            severity=rule.severity,
                            evidence=f"Change affects {affected_file}, matched pattern {pattern}"
                        )
                        violations.append(violation)

                        if rule.severity == DNARuleSeverity.HARD:
                            has_hard_violations = True

                        logger.warning(
                            f"DNA violation detected: {rule.id} - {rule.constraint}"
                        )
                        break

        return violations, has_hard_violations

    def _pattern_matches(self, pattern: str, filename: str) -> bool:
        """
        Simple pattern matching for file paths.

        Args:
            pattern: Pattern with * wildcards (e.g., "layers/layer_07_governance/*")
            filename: Filename to check

        Returns:
            True if pattern matches filename
        """
        # Convert glob pattern to simple matching
        if "*" not in pattern:
            return pattern == filename

        # Simple wildcard matching
        parts = pattern.split("*")
        if len(parts) == 2:
            start, end = parts
            return filename.startswith(start) and filename.endswith(end)

        return False

    def assess_risk(
        self,
        change_type: ChangeType,
        affected_files: List[str],
        violations: List[DNAViolation],
        related_capabilities: List[str] = None
    ) -> RiskAssessment:
        """
        Assess risk level of a proposed change.

        Args:
            change_type: Type of change
            affected_files: Files affected
            violations: DNA violations detected
            related_capabilities: Related capability IDs

        Returns:
            RiskAssessment with risk level and factors
        """
        factors: List[str] = []
        confidence = 0.85

        # Factor 1: Hard violations = automatic HIGH risk
        has_hard_violations = any(
            v.severity == DNARuleSeverity.HARD for v in violations
        )
        if has_hard_violations:
            factors.append("DNA rule violations (HARD severity)")
            return RiskAssessment(
                risk_level=RiskLevel.HIGH,
                factors=factors,
                confidence=1.0,
                recommended_action="REJECT - DNA violations"
            )

        # Factor 2: Soft violations = MEDIUM risk
        has_soft_violations = any(
            v.severity == DNARuleSeverity.SOFT for v in violations
        )
        if has_soft_violations:
            factors.append("DNA rule violations (SOFT severity)")

        # Factor 3: Change type assessment
        if change_type == ChangeType.EVOLUTION:
            factors.append("Change creates new capability (evolution)")

        if change_type in [ChangeType.EVOLUTION, ChangeType.ADAPTATION]:
            factors.append("Self-modification to SPS-CA")

        # Factor 4: Scope assessment
        core_files = [f for f in affected_files if "core/" in f or "layers/layer_0[789]" in f]
        if core_files:
            factors.append(f"Modifies core logic ({len(core_files)} files)")

        # Factor 5: Capability lineage
        if related_capabilities and len(related_capabilities) > 3:
            factors.append(f"Affects {len(related_capabilities)} capabilities (high blast radius)")

        # Determine risk level
        if has_soft_violations or len(factors) > 3:
            risk_level = RiskLevel.MEDIUM
            recommended_action = "REVIEW - Medium risk detected"
        elif len(factors) > 1:
            risk_level = RiskLevel.MEDIUM
            recommended_action = "REVIEW - Multiple risk factors"
        else:
            risk_level = RiskLevel.LOW
            recommended_action = "AUTO-APPROVE - Low risk"

        return RiskAssessment(
            risk_level=risk_level,
            factors=factors,
            confidence=confidence,
            recommended_action=recommended_action
        )

    def make_decision(
        self,
        change_id: str,
        change_type: ChangeType,
        change_description: str,
        affected_files: List[str],
        related_capabilities: List[str] = None
    ) -> GovernanceDecision:
        """
        Make a governance decision for a proposed change.

        Full workflow:
        1. Check DNA violations
        2. Assess risk level
        3. Make decision based on risk
        4. Log decision to audit trail

        Args:
            change_id: Unique change identifier
            change_type: Type of change (1-7)
            change_description: Human-readable description
            affected_files: List of files to be modified
            related_capabilities: IDs of related capabilities

        Returns:
            GovernanceDecision with full audit trail
        """
        start_time = datetime.now()

        # Step 1: Check DNA violations
        violations, has_hard_violations = self.check_dna_violations(
            change_id, affected_files, change_type
        )

        # Step 2: Assess risk
        risk_assessment = self.assess_risk(
            change_type,
            affected_files,
            violations,
            related_capabilities
        )

        # Step 3: Make decision
        if has_hard_violations:
            decision = DecisionStatus.REJECTED
            rationale = "Hard DNA rule violations detected - change rejected"
        elif risk_assessment.risk_level == RiskLevel.HIGH:
            decision = DecisionStatus.PENDING_HUMAN_REVIEW
            rationale = f"High risk: {'; '.join(risk_assessment.factors[:2])}"
        elif risk_assessment.risk_level == RiskLevel.MEDIUM:
            decision = DecisionStatus.PENDING_HUMAN_REVIEW
            rationale = f"Medium risk: {'; '.join(risk_assessment.factors[:1])}"
        else:
            decision = DecisionStatus.AUTO_APPROVED
            rationale = "Low risk - automatically approved"

        # Step 4: Create decision record
        governance_decision = GovernanceDecision(
            id=self._generate_decision_id(),
            change_id=change_id,
            change_type=change_type,
            change_description=change_description,
            dna_violations=violations,
            risk_assessment=risk_assessment,
            decision=decision,
            rationale=rationale,
            requires_human_approval=(
                decision == DecisionStatus.PENDING_HUMAN_REVIEW
            ),
            related_capabilities=related_capabilities
        )

        # Step 5: Log decision
        self._log_decision(governance_decision)
        self.decisions.append(governance_decision)

        # Step 6: Update stats
        self._update_stats(governance_decision, start_time)

        logger.info(
            f"Governance decision: {governance_decision.id} - "
            f"{change_id} - {decision} ({risk_assessment.risk_level})"
        )

        return governance_decision

    def _generate_decision_id(self) -> str:
        """Generate unique decision ID."""
        decision_count = len(self.decisions) + 1
        return f"decision_{decision_count:06d}"

    def _log_decision(self, decision: GovernanceDecision):
        """
        Log decision to audit trail (JSON file).

        Args:
            decision: GovernanceDecision to log
        """
        try:
            decision_file = self.decisions_dir / f"{decision.id}.json"
            decision_data = decision.model_dump(exclude_none=True)
            # Convert enums to strings for JSON (already done by model_dump with by_alias)
            # But we need to ensure datetime serialization
            with open(decision_file, "w") as f:
                json.dump(decision_data, f, indent=2, default=str)

            logger.info(f"Decision logged to {decision_file}")
        except Exception as e:
            logger.error(f"Failed to log decision: {e}")

    def _update_stats(self, decision: GovernanceDecision, start_time: datetime):
        """
        Update governance statistics.

        Args:
            decision: Decision that was made
            start_time: When decision process started
        """
        self.stats.total_decisions += 1

        if decision.decision == DecisionStatus.AUTO_APPROVED:
            self.stats.auto_approved += 1
        elif decision.decision == DecisionStatus.PENDING_HUMAN_REVIEW:
            self.stats.pending_human_review += 1
        elif decision.decision == DecisionStatus.APPROVED:
            self.stats.approved_by_human += 1
        elif decision.decision == DecisionStatus.REJECTED:
            self.stats.rejected += 1

        self.stats.dna_violations_detected += len(decision.dna_violations)

        if decision.risk_assessment.risk_level == RiskLevel.HIGH:
            self.stats.high_risk_changes += 1

        # Update decision time
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        if self.stats.average_decision_time_ms == 0:
            self.stats.average_decision_time_ms = elapsed_ms
        else:
            # Running average
            total = self.stats.average_decision_time_ms * (self.stats.total_decisions - 1)
            self.stats.average_decision_time_ms = (total + elapsed_ms) / self.stats.total_decisions

        # Track by change type
        change_type_count = self.stats.decision_change_history.get(decision.change_type, 0)
        self.stats.decision_change_history[decision.change_type] = change_type_count + 1

    def approve_human(self, decision_id: str, reviewer: str) -> GovernanceDecision:
        """
        Approve a pending decision by human reviewer.

        Args:
            decision_id: ID of decision to approve
            reviewer: Username/email of reviewer

        Returns:
            Updated GovernanceDecision

        Raises:
            GovernanceError: If decision not found or not pending
        """
        decision = next(
            (d for d in self.decisions if d.id == decision_id),
            None
        )

        if not decision:
            raise GovernanceError(f"Decision not found: {decision_id}")

        if decision.decision != DecisionStatus.PENDING_HUMAN_REVIEW:
            raise GovernanceError(f"Decision not pending review: {decision_id}")

        decision.decision = DecisionStatus.APPROVED
        decision.human_reviewer = reviewer
        decision.human_approval_timestamp = datetime.now()

        self._log_decision(decision)
        self.stats.approved_by_human += 1

        logger.info(f"Decision approved by {reviewer}: {decision_id}")
        return decision

    def reject_human(self, decision_id: str, reviewer: str, reason: str) -> GovernanceDecision:
        """
        Reject a pending decision by human reviewer.

        Args:
            decision_id: ID of decision to reject
            reviewer: Username/email of reviewer
            reason: Reason for rejection

        Returns:
            Updated GovernanceDecision

        Raises:
            GovernanceError: If decision not found or not pending
        """
        decision = next(
            (d for d in self.decisions if d.id == decision_id),
            None
        )

        if not decision:
            raise GovernanceError(f"Decision not found: {decision_id}")

        if decision.decision != DecisionStatus.PENDING_HUMAN_REVIEW:
            raise GovernanceError(f"Decision not pending review: {decision_id}")

        decision.decision = DecisionStatus.REJECTED
        decision.human_reviewer = reviewer
        decision.human_approval_timestamp = datetime.now()
        decision.notes = f"Rejected by {reviewer}: {reason}"

        self._log_decision(decision)
        self.stats.rejected += 1

        logger.info(f"Decision rejected by {reviewer}: {decision_id}")
        return decision

    def get_decision(self, decision_id: str) -> Optional[GovernanceDecision]:
        """
        Retrieve a decision from audit trail.

        Args:
            decision_id: ID of decision to retrieve

        Returns:
            GovernanceDecision or None if not found
        """
        return next((d for d in self.decisions if d.id == decision_id), None)

    def get_stats(self) -> GovernanceStats:
        """
        Get governance statistics.

        Returns:
            GovernanceStats object with aggregated metrics
        """
        return self.stats

    def get_pending_decisions(self) -> List[GovernanceDecision]:
        """
        Get all decisions pending human review.

        Returns:
            List of pending GovernanceDecisions
        """
        return [
            d for d in self.decisions
            if d.decision == DecisionStatus.PENDING_HUMAN_REVIEW
        ]
