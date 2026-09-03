"""AI-driven Layer-8 capability evolution.

Brain designs the implementation; EvolutionEngine owns persistence, tests, governance
integration, and registry admission.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from layers.layer_08_evolution import EvolutionEngine
from layers.layer_08_evolution.models import CapabilityPlan, GeneratedCapabilityFiles

from .evolution_designer import AICapabilityDesigner


class AIEvolutionEngine:
    """Turn an AI-identified capability gap into a tested registered capability."""

    def __init__(self, evolution: EvolutionEngine, *, provider: Optional[Any] = None, model: str = "") -> None:
        self.evolution = evolution
        self.designer = AICapabilityDesigner(provider=provider, model=model)

    def create_from_gap(
        self,
        *,
        gap: str,
        language: str,
        scenario_id: str,
        existing_capabilities: list[dict[str, Any]],
        observations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        capability_id = self.evolution.next_capability_id()
        design = self.designer.design(
            gap=gap,
            language=language,
            capability_id=capability_id,
            existing_capabilities=existing_capabilities,
            observations=observations,
        )
        plan = CapabilityPlan(
            capability_id=capability_id,
            name=design.name,
            description=design.description,
            entry_point=design.entry_point,
            supported_languages=design.supported_languages,
            trigger_pattern="ai_capability_gap",
            trigger_task_ids=[scenario_id],
            test_case_names=[],
            provenance={
                "origin": "brain_ai_evolution",
                "gap": gap,
                "rationale": design.rationale,
                "success_criteria": design.success_criteria,
                "brain_provider": self.designer.provider_name,
            },
        )
        files = GeneratedCapabilityFiles(
            capability_code=design.source_code,
            tests_code=design.tests_code,
            metadata={
                "id": capability_id,
                "name": design.name,
                "version": "1.0.0",
                "description": design.description,
                "entry_point": design.entry_point,
                "origin": "generated",
                "status": "active",
                "supported_languages": design.supported_languages,
                "target_languages": design.supported_languages,
                "generated": True,
                "failure_pattern": "ai_capability_gap",
                "trigger_tasks": [scenario_id],
                "reuse_count": 0,
                "test_coverage": None,
                "provenance": plan.provenance,
                "brain_design": {
                    "rationale": design.rationale,
                    "success_criteria": design.success_criteria,
                },
            },
            readme=(
                f"# {capability_id}: {design.name}\n\n{design.description}\n\n"
                "Designed by the SPS Brain and admitted through Layer 8 quality gates.\n"
            ),
        )
        module_dir = self.evolution.implement_capability(plan, files)
        test_result = self.evolution.test_capability(capability_id, project_root=".")
        registered = self.evolution.register_capability(plan, files, test_result)
        return {
            "capability_id": capability_id,
            "name": design.name,
            "module_dir": str(module_dir),
            "implemented": True,
            "registered": registered,
            "test_result": {
                "passed": test_result.passed,
                "tests_run": test_result.tests_run,
                "tests_failed": test_result.tests_failed,
                "coverage_percent": test_result.coverage_percent,
            },
            "brain_design": {
                "provider": self.designer.provider_name,
                "rationale": design.rationale,
                "success_criteria": design.success_criteria,
            },
        }


__all__ = ["AIEvolutionEngine"]
