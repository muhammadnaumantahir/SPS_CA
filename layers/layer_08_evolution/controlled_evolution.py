"""Controlled Layer-8 self-programming.

This module extends the existing EvolutionEngine without changing the public
10-layer architecture or the canonical CAP-001..CAP-010 baseline.

A generated capability is treated as an untrusted candidate: it is generated,
syntax-checked, tested, coverage-gated, governed, and only then registered.
Failed candidates are rolled back from the generated workspace.
"""

from __future__ import annotations

import ast
import re
import shutil
from pathlib import Path
from typing import Optional

from layers.layer_03_cognitive.llm_interface import LLMInterface, LLMQueryError
from layers.layer_02_governance.models import DecisionStatus

from .evolution_engine import EvolutionEngine as BaseEvolutionEngine
from .models import CapabilityPlan, GeneratedCapabilityFiles, TestRunResult

FIRST_GENERATED_NUMBER = 11


class ControlledEvolutionEngine(BaseEvolutionEngine):
    """Layer-8 engine with candidate generation, validation and rollback."""

    def __init__(self, *args, llm: Optional[LLMInterface] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.llm = llm or LLMInterface(timeout_seconds=120.0)

    def next_capability_id(self) -> str:
        """Allocate only CAP-011+; CAP-001..CAP-010 are permanently canonical."""
        used_numbers = set()
        for directory in (self.seeds_dir, self.generated_dir):
            if not directory.exists():
                continue
            for metadata_path in directory.glob("*/metadata.json"):
                try:
                    import json
                    data = json.loads(metadata_path.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                match = re.fullmatch(r"CAP-(\d+)", str(data.get("id", "")))
                if match:
                    used_numbers.add(int(match.group(1)))
        candidate = FIRST_GENERATED_NUMBER
        while candidate in used_numbers:
            candidate += 1
        return f"CAP-{candidate:03d}"

    def generate_capability_code(self, plan: CapabilityPlan) -> GeneratedCapabilityFiles:
        """Generate a real candidate with the Brain/LLM when available.

        The existing deterministic generator remains the compatibility fallback
        when the model is unavailable or returns unsafe/incomplete source.
        """
        if not plan.supported_languages or plan.supported_languages[0].lower() != "python":
            return super().generate_capability_code(plan)

        prompt = f"""Create one reusable Python SPS-CA capability for this approved Layer-8 plan.

CAPABILITY ID: {plan.capability_id}
NAME: {plan.name}
DESCRIPTION: {plan.description}
TRIGGER: {plan.trigger_pattern}
TASKS: {plan.trigger_task_ids}

Contract:
- Return ONLY Python source, no Markdown fences or prose.
- Define SUPPORTED_LANGUAGES = ['python'] and TRIGGER_PATTERN.
- Define run(context) accepting capabilities.base.CapabilityContext.
- Return capabilities.base.CapabilityResult.
- Implement the described behavior rather than a marker/no-op.
- Never execute subprocesses, shell commands, network requests, or filesystem writes.
- Never import eval/exec or dynamically import untrusted modules.
- On unsupported language, return CapabilityResult.ok without modifying code.
- On invalid/empty input, return CapabilityResult.fail with a useful error.
"""
        try:
            raw = self.llm.query(code="", instruction=prompt, model="", temperature=0.0)
            source = self._clean_candidate_source(raw)
            self._validate_candidate_source(source)
            base = super().generate_capability_code(plan)
            metadata = dict(base.metadata)
            metadata["generation_method"] = "brain_candidate"
            metadata["candidate_validation"] = "ast_static_contract"
            return GeneratedCapabilityFiles(
                capability_code=source,
                tests_code=base.tests_code,
                metadata=metadata,
                readme=base.readme,
            )
        except (LLMQueryError, ValueError, SyntaxError):
            return super().generate_capability_code(plan)

    @staticmethod
    def _clean_candidate_source(raw: str) -> str:
        text = str(raw or "").strip()
        fences = re.findall(r"```(?:python)?\s*\n?(.*?)\n?```", text, re.DOTALL | re.IGNORECASE)
        if fences:
            text = max(fences, key=len).strip()
        if not text:
            raise ValueError("empty candidate source")
        return text

    @staticmethod
    def _validate_candidate_source(source: str) -> None:
        tree = ast.parse(source)
        names = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        if "run" not in names:
            raise ValueError("candidate must define run(context)")
        assignments = {
            node.targets[0].id
            for node in tree.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        }
        if "SUPPORTED_LANGUAGES" not in assignments or "TRIGGER_PATTERN" not in assignments:
            raise ValueError("candidate missing required capability constants")
        blocked = {"subprocess", "socket", "requests", "urllib", "eval", "exec", "os.system"}
        source_lower = source.lower()
        if any(token in source_lower for token in blocked):
            raise ValueError("candidate contains a blocked execution/network primitive")

    def develop_capability_for_gap(
        self,
        plan: CapabilityPlan,
        *,
        project_root: str = ".",
        governance_decision_status: Optional[DecisionStatus] = None,
    ) -> dict:
        """Run candidate -> validate -> test -> govern -> promote, with rollback."""
        files = self.generate_capability_code(plan)
        module_dir = self.implement_capability(plan, files)
        try:
            result = self.test_capability(plan.capability_id, project_root=project_root)
            approved = governance_decision_status in {
                None,
                DecisionStatus.AUTO_APPROVED,
                DecisionStatus.APPROVED,
            }
            registered = self.register_capability(
                plan,
                files,
                result,
                governance_decision_status=governance_decision_status,
            ) if approved else False
            promoted = bool(registered)
            if not promoted:
                shutil.rmtree(module_dir, ignore_errors=True)
            return {
                "capability_id": plan.capability_id,
                "module_dir": str(module_dir),
                "implemented": promoted,
                "candidate_created": True,
                "promoted": promoted,
                "rolled_back": not promoted,
                "test_result": {
                    "passed": result.passed,
                    "tests_run": result.tests_run,
                    "tests_failed": result.tests_failed,
                    "coverage_percent": result.coverage_percent,
                },
                "generation_method": files.metadata.get("generation_method", "deterministic_fallback"),
            }
        except Exception:
            shutil.rmtree(module_dir, ignore_errors=True)
            raise
