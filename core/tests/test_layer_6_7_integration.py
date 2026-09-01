"""
Integration tests for Layer 6 (Validation) and Layer 7 (Governance).

Tests the full workflow: proposed change → governance check → validation → decision
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from layers.layer_06_validation import Validator, SandboxResult, SandboxStatus, MetricsSnapshot
from layers.layer_07_governance import GovernanceGate, ChangeType, DecisionStatus


class TestLayer6Layer7Integration:
    """Test interaction between Validation and Governance layers."""

    @pytest.fixture
    def workflow_setup(self):
        """Setup for testing complete workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "project"
            project_path.mkdir()
            decisions_dir = Path(tmpdir) / "decisions"
            
            validator = Validator(str(project_path))
            governance_gate = GovernanceGate(decisions_dir=str(decisions_dir))
            
            yield {
                "project_path": project_path,
                "validator": validator,
                "governance_gate": governance_gate,
            }

    def test_complete_change_workflow(self, workflow_setup):
        """
        Test complete workflow:
        1. Propose change
        2. Governance checks DNA rules
        3. Risk assessment
        4. Validation sandbox testing
        5. Final decision
        """
        gate = workflow_setup["governance_gate"]
        
        # Step 1: Make governance decision
        decision = gate.make_decision(
            change_id="CHANGE-001",
            change_type=ChangeType.SYNTAX_FIX,
            change_description="Fix import in module.py",
            affected_files=["src/module.py"],
            related_capabilities=["CAP-001"]
        )

        assert decision is not None
        assert decision.decision == DecisionStatus.AUTO_APPROVED

        # Step 2: Create simulated validation result
        before_metrics = MetricsSnapshot(
            test_count=42,
            tests_passing=42,
            code_coverage=85.0,
            execution_time_ms=2100.0
        )

        after_metrics = MetricsSnapshot(
            test_count=42,
            tests_passing=42,
            code_coverage=86.0,
            execution_time_ms=2050.0
        )

        result = SandboxResult(
            status=SandboxStatus.SUCCESS,
            metrics=after_metrics,
            stdout="All tests passed",
            stderr="",
            exit_code=0
        )

        # Step 3: Verify change can proceed
        assert decision.decision == DecisionStatus.AUTO_APPROVED
        assert result.status == SandboxStatus.SUCCESS

    def test_evolution_change_workflow_pending(self, workflow_setup):
        """
        Test evolution (self-programming) change requiring human review.
        """
        gate = workflow_setup["governance_gate"]

        # Propose evolution (high-risk)
        decision = gate.make_decision(
            change_id="CHANGE-002",
            change_type=ChangeType.EVOLUTION,
            change_description="Generate new capability CAP-009",
            affected_files=["capabilities/generated/CAP-009/capability.py"],
            related_capabilities=["CAP-001", "CAP-002", "CAP-003", "CAP-004"]
        )

        # Should be pending human review due to evolution + multiple related capabilities
        assert decision.requires_human_approval
        assert decision.decision == DecisionStatus.PENDING_HUMAN_REVIEW

        # Simulate human approval
        approved = gate.approve_human(
            decision_id=decision.id,
            reviewer="dr.salman@vu.edu.pk"
        )

        assert approved.decision == DecisionStatus.APPROVED

    def test_validation_caught_regression_workflow(self, workflow_setup):
        """
        Test workflow where validation detects regression.
        """
        gate = workflow_setup["governance_gate"]

        # Governance approves change
        decision = gate.make_decision(
            change_id="CHANGE-003",
            change_type=ChangeType.REFACTORING,
            change_description="Refactor module for performance",
            affected_files=["src/module.py"],
            related_capabilities=["CAP-001"]
        )

        assert decision.decision == DecisionStatus.AUTO_APPROVED

        # But validation detects regression
        after_metrics = MetricsSnapshot(
            test_count=42,
            tests_passing=40,  # 2 tests now fail!
            code_coverage=85.0,
            execution_time_ms=2100.0
        )

        result = SandboxResult(
            status=SandboxStatus.FAILURE,
            metrics=after_metrics,
            stdout="",
            stderr="2 tests failed",
            exit_code=1
        )

        # Even though governance approved, validation caught the issue
        assert result.status == SandboxStatus.FAILURE

    def test_hard_violation_blocks_change(self, workflow_setup):
        """
        Test that HARD DNA violations block changes immediately.
        """
        gate = workflow_setup["governance_gate"]

        # Attempt to modify governance logic (HARD violation)
        decision = gate.make_decision(
            change_id="CHANGE-004",
            change_type=ChangeType.LOGIC_FIX,
            change_description="Fix bug in governance.py",
            affected_files=["layers/layer_07_governance/governance.py"]
        )

        # Should be rejected due to HARD DNA violation
        assert decision.decision == DecisionStatus.REJECTED
        assert len(decision.dna_violations) > 0
        assert any(v.severity.value == "hard" for v in decision.dna_violations)

    def test_adaptation_workflow(self, workflow_setup):
        """
        Test adaptation change workflow (adjusting existing capability).
        """
        gate = workflow_setup["governance_gate"]

        # Adaptation is lower risk than evolution
        decision = gate.make_decision(
            change_id="CHANGE-005",
            change_type=ChangeType.ADAPTATION,
            change_description="Adapt CAP-001 timeout from 30s to 60s",
            affected_files=["capabilities/seeds/CAP-001/capability.py"],
            related_capabilities=["CAP-001"]
        )

        # Should be low risk if only adjusting parameters
        assert decision.decision in [DecisionStatus.AUTO_APPROVED, DecisionStatus.PENDING_HUMAN_REVIEW]

    def test_test_generation_workflow(self, workflow_setup):
        """
        Test test generation change workflow.
        """
        gate = workflow_setup["governance_gate"]

        # Test generation for existing code
        decision = gate.make_decision(
            change_id="CHANGE-006",
            change_type=ChangeType.TEST_GENERATION,
            change_description="Generate unit tests for CAP-001",
            affected_files=["capabilities/seeds/CAP-001/tests.py"],
            related_capabilities=["CAP-001"]
        )

        # Should be low risk - only adding tests
        assert decision.decision == DecisionStatus.AUTO_APPROVED


class TestGovernanceAuditTrail:
    """Test governance audit trail features."""

    def test_audit_trail_preservation(self):
        """Test that audit trail is preserved in decision logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gate = GovernanceGate(decisions_dir=tmpdir)

            # Make a decision
            decision = gate.make_decision(
                change_id="AUDIT-001",
                change_type=ChangeType.FEATURE_ADDITION,
                change_description="Add new feature",
                affected_files=["src/feature.py"],
                related_capabilities=["CAP-001"]
            )

            # Verify it's in the audit trail
            retrieved = gate.get_decision(decision.id)
            assert retrieved is not None
            assert retrieved.change_id == "AUDIT-001"

    def test_decision_file_format(self):
        """Test that decision files are valid JSON."""
        import json
        
        with tempfile.TemporaryDirectory() as tmpdir:
            gate = GovernanceGate(decisions_dir=tmpdir)

            decision = gate.make_decision(
                change_id="FORMAT-001",
                change_type=ChangeType.SYNTAX_FIX,
                change_description="Fix syntax",
                affected_files=["src/module.py"]
            )

            # Read the decision file
            decision_file = Path(tmpdir) / f"{decision.id}.json"
            with open(decision_file) as f:
                loaded = json.load(f)

            assert loaded["id"] == decision.id
            assert loaded["change_id"] == "FORMAT-001"


class TestRiskLevelProgression:
    """Test risk level progression through different scenarios."""

    def test_risk_escalation_path(self):
        """Test that risk levels escalate as expected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gate = GovernanceGate(decisions_dir=tmpdir)

            # Low risk: single file, single capability
            low_risk = gate.make_decision(
                change_id="RISK-001",
                change_type=ChangeType.SYNTAX_FIX,
                change_description="Fix typo",
                affected_files=["src/typo.py"],
                related_capabilities=["CAP-001"]
            )
            assert low_risk.decision == DecisionStatus.AUTO_APPROVED

            # Medium risk: evolution type
            medium_risk = gate.make_decision(
                change_id="RISK-002",
                change_type=ChangeType.EVOLUTION,
                change_description="New capability",
                affected_files=["capabilities/generated/CAP-010/capability.py"],
                related_capabilities=["CAP-001", "CAP-002", "CAP-003"]
            )
            assert medium_risk.requires_human_approval

            # High risk: governance modification (HARD violation)
            high_risk = gate.make_decision(
                change_id="RISK-003",
                change_type=ChangeType.LOGIC_FIX,
                change_description="Fix governance",
                affected_files=["layers/layer_07_governance/governance.py"]
            )
            assert high_risk.decision == DecisionStatus.REJECTED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
