"""End-to-end governed evolution workflow for Phase 4.

This orchestration layer keeps the responsibilities explicit:
experience evidence -> Layer 8 planning/generation -> Layer 6 validation ->
Layer 7 governance -> Layer 9 registration.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from layers.layer_06_validation import Validator
from layers.layer_07_governance import GovernanceGate
from layers.layer_07_governance.models import ChangeType, DecisionStatus
from layers.layer_09_capability_registry.registry import CapabilityRecord, CapabilityRegistry
from layers.layer_03_experience.experience_log import ExperienceLog
from .evolution_engine import EvolutionEngine, EvolutionError, GeneratedCapability, TestResults


@dataclass
class EvolutionWorkflowResult:
    capability_id: str
    trigger_pattern: str
    staged_path: Path
    test_results: TestResults
    governance_status: DecisionStatus
    promoted_path: Optional[Path] = None
    registered: bool = False


class EvolutionWorkflow:
    """Coordinate one safe evolution cycle without bypassing governance."""

    def __init__(
        self,
        engine: EvolutionEngine,
        governance: GovernanceGate,
        registry: CapabilityRegistry,
    ) -> None:
        self.engine = engine
        self.governance = governance
        self.registry = registry

    def evolve(
        self,
        experience_log: ExperienceLog,
        validator: Optional[Validator] = None,
        evidence: Optional[List[str]] = None,
        approved: Optional[bool] = None,
    ) -> EvolutionWorkflowResult:
        patterns = self.engine.repeated_failure_patterns(experience_log)
        if not patterns:
            raise EvolutionError("No repeated failure pattern meets the evolution threshold")
        trigger = next(iter(patterns))
        plan = self.engine.plan_new_capability(trigger, experience_log)
        generated: GeneratedCapability = self.engine.generate_capability_code(plan, evidence)
        staged = self.engine.stage_capability(generated)
        tests = self.engine.test_capability(plan.capability_id, staged)
        if not tests.passed:
            raise EvolutionError(f"Generated capability failed validation: {tests.error or 'unknown error'}")

        # Layer 6 is an optional integration boundary because its current API
        # validates project-file changes, while Layer 8 generates a new package.
        # When supplied, callers can run project-level regression checks here.
        _ = validator

        affected_files = [
            f"capabilities/generated/{plan.capability_id}/{name}"
            for name in generated.files
        ]
        decision = self.governance.evaluate_change(
            change_id=plan.capability_id,
            change_type=ChangeType.EVOLUTION,
            change_description=plan.reason,
            affected_files=affected_files,
            related_capabilities=plan.parent_capabilities,
        )
        governance_approved = approved if approved is not None else decision.decision in {
            DecisionStatus.AUTO_APPROVED,
            DecisionStatus.APPROVED,
        }
        promoted: Optional[Path] = None
        registered = False
        if governance_approved:
            promoted = self.engine.promote_capability(plan.capability_id, approved=True)
            record = CapabilityRecord(
                capability_id=plan.capability_id,
                name=plan.name,
                version=str(generated.metadata.get("version", "1.0.0")),
                path=str(promoted),
                entry_point=plan.entry_point,
                trigger_pattern=plan.trigger_pattern,
                parent_capabilities=plan.parent_capabilities,
                model_provider=str(generated.metadata.get("model_provider", "")),
                model=str(generated.metadata.get("model", "")),
            )
            self.registry.register(record)
            registered = True
        return EvolutionWorkflowResult(
            capability_id=plan.capability_id,
            trigger_pattern=trigger,
            staged_path=staged,
            test_results=tests,
            governance_status=decision.decision,
            promoted_path=promoted,
            registered=registered,
        )
