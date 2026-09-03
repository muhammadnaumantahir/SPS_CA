"""
Unit tests for Layer 7: Governance Layer.

Tests DNA rule enforcement, risk assessment, governance decisions,
and audit trail logging.
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from ..governance import GovernanceGate, GovernanceError
from ..models import (
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


class TestDNARule:
    """Test DNA rule models."""

    def test_dna_rule_creation_hard(self):
        """Test creating a HARD severity DNA rule."""
        rule = DNARule(
            id="rule_001",
            constraint="Never modify governance logic",
            severity=DNARuleSeverity.HARD,
            affected_files=["layers/layer_02_governance/*"],
            description="Governance must be immutable"
        )

        assert rule.id == "rule_001"
        assert rule.severity == DNARuleSeverity.HARD
        assert "governance" in rule.constraint.lower()

    def test_dna_rule_creation_soft(self):
        """Test creating a SOFT severity DNA rule."""
        rule = DNARule(
            id="rule_003",
            constraint="All generated capabilities must have >80% test coverage",
            severity=DNARuleSeverity.SOFT
        )

        assert rule.id == "rule_003"
        assert rule.severity == DNARuleSeverity.SOFT
        assert rule.affected_files is None

    def test_dna_rule_affected_files(self):
        """Test DNA rule with multiple affected file patterns."""
        rule = DNARule(
            id="rule_005",
            constraint="All changes must be reversible",
            severity=DNARuleSeverity.HARD,
            affected_files=[".git", "capabilities/*", "layers/*"]
        )

        assert len(rule.affected_files) == 3
        assert ".git" in rule.affected_files


class TestRiskAssessment:
    """Test risk assessment functionality."""

    def test_risk_assessment_low(self):
        """Test low-risk assessment."""
        assessment = RiskAssessment(
            risk_level=RiskLevel.LOW,
            factors=[],
            confidence=0.95,
            recommended_action="AUTO-APPROVE"
        )

        assert assessment.risk_level == RiskLevel.LOW
        assert assessment.confidence == 0.95

    def test_risk_assessment_medium(self):
        """Test medium-risk assessment."""
        assessment = RiskAssessment(
            risk_level=RiskLevel.MEDIUM,
            factors=["Modifies core logic", "Affects 3 capabilities"],
            confidence=0.85,
            recommended_action="REVIEW"
        )

        assert assessment.risk_level == RiskLevel.MEDIUM
        assert len(assessment.factors) == 2

    def test_risk_assessment_high(self):
        """Test high-risk assessment."""
        assessment = RiskAssessment(
            risk_level=RiskLevel.HIGH,
            factors=["DNA violations detected", "Self-modification"],
            confidence=1.0,
            recommended_action="REJECT"
        )

        assert assessment.risk_level == RiskLevel.HIGH
        assert assessment.confidence == 1.0


class TestDNAViolation:
    """Test DNA violation records."""

    def test_dna_violation_hard(self):
        """Test recording a HARD severity violation."""
        violation = DNAViolation(
            rule_id="rule_001",
            rule_description="Never modify governance logic",
            severity=DNARuleSeverity.HARD,
            evidence="File layers/layer_02_governance/governance.py would be modified"
        )

        assert violation.rule_id == "rule_001"
        assert violation.severity == DNARuleSeverity.HARD
        assert "governance.py" in violation.evidence

    def test_dna_violation_soft(self):
        """Test recording a SOFT severity violation."""
        violation = DNAViolation(
            rule_id="rule_003",
            rule_description="All generated capabilities must have >80% test coverage",
            severity=DNARuleSeverity.SOFT,
            evidence="Generated capability has 75% test coverage"
        )

        assert violation.severity == DNARuleSeverity.SOFT
        assert "75%" in violation.evidence


class TestGovernanceGate:
    """Test GovernanceGate class."""

    @pytest.fixture
    def governance_gate(self):
        """Create a temporary governance gate for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gate = GovernanceGate(decisions_dir=tmpdir)
            yield gate

    def test_governance_gate_initialization(self):
        """Test GovernanceGate initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gate = GovernanceGate(decisions_dir=tmpdir)

            assert len(gate.dna_rules) > 0
            assert gate.stats.total_decisions == 0
            assert Path(tmpdir).exists()

    def test_default_rules_loaded(self, governance_gate):
        """Test that both mechanical and canonical DNA rules are loaded."""
        # Mechanical, file-pattern-checkable rules (namespaced gov_mech_*
        # specifically so they never collide with the canonical rule_* IDs
        # below).
        assert "gov_mech_001" in governance_gate.dna_rules
        assert "gov_mech_002" in governance_gate.dna_rules
        assert "gov_mech_003" in governance_gate.dna_rules
        assert "gov_mech_004" in governance_gate.dna_rules
        # Canonical, declarative Software DNA rules from
        # governance/dna_rules.json, merged in by default.
        assert "rule_001" in governance_gate.dna_rules
        assert "rule_002" in governance_gate.dna_rules

    def test_load_custom_dna_rules(self):
        """Test loading custom DNA rules from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create custom DNA rules file
            rules_file = tmpdir / "dna_rules.json"
            rules_data = {
                "dna_rules": [
                    {
                        "id": "custom_001",
                        "constraint": "Custom test rule",
                        "severity": "hard",
                        "affected_files": ["test/*"]
                    }
                ]
            }
            
            with open(rules_file, "w") as f:
                json.dump(rules_data, f)

            gate = GovernanceGate(
                dna_rules_path=str(rules_file),
                decisions_dir=str(tmpdir)
            )

            assert "custom_001" in gate.dna_rules

    def test_dna_violation_detection_hard_violation(self, governance_gate):
        """Test detection of HARD DNA violations."""
        affected_files = ["layers/layer_02_governance/governance.py"]
        violations, has_hard = governance_gate.check_dna_violations(
            change_id="change_001",
            affected_files=affected_files,
            change_type=ChangeType.LOGIC_FIX
        )

        assert has_hard is True
        assert len(violations) > 0

    def test_dna_violation_detection_no_violation(self, governance_gate):
        """Test that no violations are detected for safe changes."""
        affected_files = ["capabilities/generated/CAP-009/capability.py"]
        violations, has_hard = governance_gate.check_dna_violations(
            change_id="change_002",
            affected_files=affected_files,
            change_type=ChangeType.FEATURE_ADDITION
        )

        # Capability generation should not violate existing rules
        has_hard_on_capability = any(
            v.severity == DNARuleSeverity.HARD for v in violations
        )
        assert has_hard_on_capability is False

    def test_risk_assessment_low_risk(self, governance_gate):
        """Test low-risk assessment."""
        assessment = governance_gate.assess_risk(
            change_type=ChangeType.SYNTAX_FIX,
            affected_files=["projects/project_a/main.py"],
            violations=[],
            related_capabilities=["CAP-001"]
        )

        assert assessment.risk_level == RiskLevel.LOW
        assert "AUTO-APPROVE" in assessment.recommended_action

    def test_risk_assessment_medium_risk(self, governance_gate):
        """Test medium-risk assessment."""
        violations = [
            DNAViolation(
                rule_id="rule_003",
                rule_description="Test coverage rule",
                severity=DNARuleSeverity.SOFT,
                evidence="Coverage below 80%"
            )
        ]

        assessment = governance_gate.assess_risk(
            change_type=ChangeType.ADAPTATION,
            affected_files=["capabilities/generated/CAP-009/capability.py"],
            violations=violations,
            related_capabilities=["CAP-001", "CAP-002", "CAP-003"]
        )

        assert assessment.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]

    def test_risk_assessment_high_risk_hard_violation(self, governance_gate):
        """Test high-risk assessment with HARD violations."""
        violations = [
            DNAViolation(
                rule_id="rule_001",
                rule_description="Governance immutability",
                severity=DNARuleSeverity.HARD,
                evidence="Modifies governance logic"
            )
        ]

        assessment = governance_gate.assess_risk(
            change_type=ChangeType.EVOLUTION,
            affected_files=["layers/layer_02_governance/governance.py"],
            violations=violations
        )

        assert assessment.risk_level == RiskLevel.HIGH
        assert assessment.confidence == 1.0

    def test_governance_decision_auto_approved(self, governance_gate):
        """Test automatic approval for low-risk changes."""
        decision = governance_gate.make_decision(
            change_id="change_001",
            change_type=ChangeType.SYNTAX_FIX,
            change_description="Fix typo in module.py",
            affected_files=["projects/project_a/module.py"],
            related_capabilities=["CAP-001"]
        )

        assert decision.decision == DecisionStatus.AUTO_APPROVED
        assert not decision.requires_human_approval

    def test_governance_decision_pending_review(self, governance_gate):
        """Test escalation to human review for medium-risk changes."""
        decision = governance_gate.make_decision(
            change_id="change_002",
            change_type=ChangeType.EVOLUTION,
            change_description="Generate new capability from failures",
            affected_files=["capabilities/generated/CAP-009/capability.py"],
            related_capabilities=["CAP-001", "CAP-002", "CAP-003", "CAP-004"]
        )

        assert decision.decision == DecisionStatus.PENDING_HUMAN_REVIEW
        assert decision.requires_human_approval

    def test_governance_decision_rejected_hard_violation(self, governance_gate):
        """Test rejection due to HARD DNA violations."""
        decision = governance_gate.make_decision(
            change_id="change_003",
            change_type=ChangeType.LOGIC_FIX,
            change_description="Modify governance logic",
            affected_files=["layers/layer_02_governance/governance.py"]
        )

        assert decision.decision == DecisionStatus.REJECTED

    def test_decision_logging(self, governance_gate):
        """Test that decisions are logged to audit trail."""
        decision = governance_gate.make_decision(
            change_id="change_004",
            change_type=ChangeType.SYNTAX_FIX,
            change_description="Fix import statements",
            affected_files=["src/module.py"]
        )

        # Check that decision file exists
        decision_file = governance_gate.decisions_dir / f"{decision.id}.json"
        assert decision_file.exists()

        # Verify content
        with open(decision_file) as f:
            logged_data = json.load(f)

        assert logged_data["id"] == decision.id
        assert logged_data["change_id"] == "change_004"

    def test_human_approval_workflow(self, governance_gate):
        """Test human approval of pending decisions."""
        # Create a pending decision
        decision = governance_gate.make_decision(
            change_id="change_005",
            change_type=ChangeType.EVOLUTION,
            change_description="Generate new capability",
            affected_files=["capabilities/generated/CAP-010/capability.py"],
            related_capabilities=["CAP-001", "CAP-002", "CAP-003", "CAP-004", "CAP-005"]
        )

        assert decision.decision == DecisionStatus.PENDING_HUMAN_REVIEW

        # Approve
        approved = governance_gate.approve_human(
            decision_id=decision.id,
            reviewer="dr.salman@vu.edu.pk"
        )

        assert approved.decision == DecisionStatus.APPROVED
        assert approved.human_reviewer == "dr.salman@vu.edu.pk"

    def test_human_rejection_workflow(self, governance_gate):
        """Test human rejection of pending decisions."""
        # Create a pending decision
        decision = governance_gate.make_decision(
            change_id="change_006",
            change_type=ChangeType.EVOLUTION,
            change_description="Generate new capability",
            affected_files=["capabilities/generated/CAP-011/capability.py"],
            related_capabilities=["CAP-001", "CAP-002", "CAP-003"]
        )

        # Reject
        rejected = governance_gate.reject_human(
            decision_id=decision.id,
            reviewer="dr.salman@vu.edu.pk",
            reason="Coverage requirements not met"
        )

        assert rejected.decision == DecisionStatus.REJECTED
        assert "Coverage" in rejected.notes

    def test_governance_statistics_tracking(self, governance_gate):
        """Test that governance statistics are tracked correctly."""
        # Make several decisions
        governance_gate.make_decision(
            change_id="change_007",
            change_type=ChangeType.SYNTAX_FIX,
            change_description="Fix typo",
            affected_files=["src/module.py"]
        )

        governance_gate.make_decision(
            change_id="change_008",
            change_type=ChangeType.EVOLUTION,
            change_description="New capability",
            affected_files=["capabilities/generated/CAP-012/capability.py"],
            related_capabilities=["CAP-001", "CAP-002", "CAP-003", "CAP-004"]
        )

        stats = governance_gate.get_stats()

        assert stats.total_decisions == 2
        assert stats.auto_approved > 0
        assert stats.pending_human_review > 0
        assert stats.approval_rate >= 0.0
        assert stats.approval_rate <= 1.0

    def test_pending_decisions_retrieval(self, governance_gate):
        """Test retrieving pending decisions."""
        governance_gate.make_decision(
            change_id="change_009",
            change_type=ChangeType.EVOLUTION,
            change_description="Generate new capability",
            affected_files=["capabilities/generated/CAP-013/capability.py"],
            related_capabilities=["CAP-001", "CAP-002", "CAP-003"]
        )

        pending = governance_gate.get_pending_decisions()

        assert len(pending) > 0
        assert all(d.decision == DecisionStatus.PENDING_HUMAN_REVIEW for d in pending)


class TestChangeTypes:
    """Test change type classifications."""

    def test_all_change_types_defined(self):
        """Test that all change types are defined."""
        assert ChangeType.SYNTAX_FIX.value == 1
        assert ChangeType.LOGIC_FIX.value == 2
        assert ChangeType.FEATURE_ADDITION.value == 3
        assert ChangeType.REFACTORING.value == 4
        assert ChangeType.TEST_GENERATION.value == 5
        assert ChangeType.ADAPTATION.value == 6
        assert ChangeType.EVOLUTION.value == 7


class TestGovernanceStats:
    """Test governance statistics model."""

    def test_stats_initialization(self):
        """Test GovernanceStats initialization."""
        stats = GovernanceStats()

        assert stats.total_decisions == 0
        assert stats.auto_approved == 0
        assert stats.approval_rate == 0.0

    def test_approval_rate_calculation(self):
        """Test approval rate calculation."""
        stats = GovernanceStats(
            total_decisions=100,
            auto_approved=60,
            approved_by_human=20,
            rejected=20
        )

        assert stats.approval_rate == 0.8

    def test_rejection_rate_calculation(self):
        """Test rejection rate calculation."""
        stats = GovernanceStats(
            total_decisions=100,
            rejected=10
        )

        assert stats.rejection_rate == 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
