"""Layer 8: Evolution Engine.

Turns repeated failure patterns from Layer 3/4 into candidate, versioned
capabilities. The engine deliberately separates generation from promotion:
generated artifacts are staged first, validated, then promoted only after
the caller's governance gate approves the change.
"""
from __future__ import annotations

import ast
import json
import re
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from layers.layer_03_experience.experience_log import ExperienceLog
from models.base import LLMProvider, LLMRequest


@dataclass(frozen=True)
class CapabilityPlan:
    capability_id: str
    name: str
    trigger_pattern: str
    entry_point: str = "run"
    supported_languages: List[str] = field(default_factory=lambda: ["python"])
    test_cases: List[str] = field(default_factory=list)
    parent_capabilities: List[str] = field(default_factory=list)
    reason: str = ""


@dataclass
class GeneratedCapability:
    capability_id: str
    files: Dict[str, str]
    metadata: Dict[str, Any]


@dataclass
class TestResults:
    passed: bool
    return_code: int = 0
    output: str = ""
    coverage_percent: Optional[float] = None
    error: Optional[str] = None


class EvolutionError(RuntimeError):
    """Raised when an evolution operation cannot safely continue."""


class EvolutionEngine:
    """Detect, plan, generate and stage new capabilities.

    Promotion is intentionally not a governance decision. Callers must pass
    explicit approval after validation and the Layer 7 governance gate.
    """

    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        generated_root: str = "capabilities/generated",
        pending_root: str = "evaluation/evolution/pending",
        min_occurrences: int = 3,
        model: str = "",
        timeout_seconds: float = 120.0,
    ) -> None:
        if min_occurrences < 1:
            raise ValueError("min_occurrences must be >= 1")
        self.provider = provider
        self.generated_root = Path(generated_root)
        self.pending_root = Path(pending_root)
        self.min_occurrences = min_occurrences
        self.model = model
        self.timeout_seconds = timeout_seconds

    def should_evolve(self, experience_log: ExperienceLog, min_occurrences: Optional[int] = None) -> bool:
        threshold = self.min_occurrences if min_occurrences is None else min_occurrences
        if threshold < 1:
            raise ValueError("min_occurrences must be >= 1")
        return any(count >= threshold for count in experience_log.get_failure_patterns().values())

    def repeated_failure_patterns(self, experience_log: ExperienceLog, min_occurrences: Optional[int] = None) -> Dict[str, int]:
        threshold = self.min_occurrences if min_occurrences is None else min_occurrences
        patterns = {name: count for name, count in experience_log.get_failure_patterns().items() if count >= threshold}
        return dict(sorted(patterns.items(), key=lambda item: (-item[1], item[0])))

    def plan_new_capability(self, trigger_pattern: str, experience_log: Optional[ExperienceLog] = None, capability_id: Optional[str] = None) -> CapabilityPlan:
        trigger = trigger_pattern.strip()
        if not trigger:
            raise ValueError("trigger_pattern must be non-empty")
        parent_ids: List[str] = []
        languages: List[str] = ["python"]
        if experience_log:
            for task in experience_log.tasks:
                if task.failure_category == trigger and task.selected_capability and task.selected_capability not in parent_ids:
                    parent_ids.append(task.selected_capability)
                if task.failure_category == trigger and task.target_language and task.target_language not in languages:
                    languages.append(task.target_language)
        slug = self._slug(trigger)
        cap_id = capability_id or self._next_capability_id()
        name = "".join(part.capitalize() for part in slug.split("_")) or "GeneratedCapability"
        return CapabilityPlan(
            capability_id=cap_id,
            name=name,
            trigger_pattern=trigger,
            supported_languages=languages,
            test_cases=[
                f"reproduces the failure category: {trigger}",
                "handles a normal valid input",
                "returns a structured CapabilityResult",
            ],
            parent_capabilities=parent_ids,
            reason=f"Repeated failure pattern '{trigger}' met the evolution threshold.",
        )

    def generate_capability_code(self, plan: CapabilityPlan, evidence: Optional[Sequence[str]] = None) -> GeneratedCapability:
        if self.provider is None:
            raise EvolutionError("An LLMProvider is required to generate capability code")
        evidence_text = "\n".join(f"- {item}" for item in (evidence or []))
        prompt = f"""Generate a new SPS-CA capability from this evolution plan.
Return ONLY valid JSON with keys capability_py, tests_py, readme_md.
Do not include markdown fences around the JSON.

Plan:
{json.dumps(asdict(plan), indent=2)}

Evidence:
{evidence_text or '- No additional evidence supplied'}

Rules:
- Python only for the generated module.
- capability.py must expose run(context) and use capabilities.base.CapabilityContext/CapabilityResult.
- Do not modify SPS-CA governance, DNA, execution or existing seed capabilities.
- tests.py must be self-contained and test the public run() entry point.
- Do not execute subprocesses, network calls, filesystem writes, eval, exec, or dynamic imports.
"""
        response = self.provider.generate(LLMRequest(prompt=prompt, system="You generate small, testable, deterministic SPS-CA capability modules.", model=self.model, temperature=0.1, timeout_seconds=self.timeout_seconds, metadata={"layer": "8", "capability_id": plan.capability_id}))
        payload = self._parse_json_response(response.text)
        required = {"capability_py", "tests_py", "readme_md"}
        missing = required.difference(payload)
        if missing:
            raise EvolutionError(f"Generated response missing keys: {sorted(missing)}")
        capability_py = str(payload["capability_py"])
        tests_py = str(payload["tests_py"])
        self._validate_generated_source(capability_py, "capability.py")
        self._validate_generated_source(tests_py, "tests.py")
        metadata = self._metadata(plan, response.provider, response.model)
        return GeneratedCapability(plan.capability_id, {"capability.py": capability_py, "tests.py": tests_py, "metadata.json": json.dumps(metadata, indent=2) + "\n", "README.md": str(payload["readme_md"])}, metadata)

    def stage_capability(self, generated: GeneratedCapability) -> Path:
        target = self.pending_root / generated.capability_id
        if target.exists():
            raise EvolutionError(f"Pending capability already exists: {target}")
        for relative, content in generated.files.items():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
        return target

    def test_capability(self, capability_id: str, staged_path: Optional[Path] = None) -> TestResults:
        """Compatibility helper for direct engine callers.

        Full package validation, including the mandatory coverage gate, is
        owned by Layer 6's CapabilityPackageValidator.
        """
        path = staged_path or (self.pending_root / capability_id)
        tests = path / "tests.py"
        if not tests.exists():
            return TestResults(False, error=f"tests.py not found: {tests}")
        return TestResults(False, error="Use Layer 6 CapabilityPackageValidator for authoritative validation")

    def promote_capability(self, capability_id: str, approved: bool) -> Path:
        source = self.pending_root / capability_id
        if not source.exists():
            raise EvolutionError(f"Staged capability does not exist: {source}")
        if not approved:
            raise EvolutionError("Governance approval is required before promotion")
        destination = self.generated_root / capability_id
        if destination.exists():
            raise EvolutionError(f"Generated capability already exists: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination)
        return destination

    def _next_capability_id(self) -> str:
        ids: Iterable[str] = []
        if self.generated_root.exists():
            ids = [p.name for p in self.generated_root.iterdir() if p.is_dir()]
        numbers = [int(match.group(1)) for name in ids if (match := re.fullmatch(r"CAP-(\d+)", name))]
        if self.pending_root.exists():
            numbers.extend(int(match.group(1)) for p in self.pending_root.iterdir() if p.is_dir() if (match := re.fullmatch(r"CAP-(\d+)", p.name)))
        return f"CAP-{max(numbers, default=0) + 1:03d}"

    @staticmethod
    def _slug(value: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
        return slug[:60] or "generated_capability"

    @staticmethod
    def _parse_json_response(text: str) -> Dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE | re.DOTALL).strip()
        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise EvolutionError(f"Model response is not valid JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise EvolutionError("Model response must be a JSON object")
        return payload

    @staticmethod
    def _validate_generated_source(source: str, filename: str) -> None:
        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError as exc:
            raise EvolutionError(f"Generated {filename} has invalid Python: {exc}") from exc
        banned = {"eval", "exec", "compile", "__import__"}
        restricted = {"subprocess", "socket", "requests", "urllib", "os", "shutil"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in banned:
                raise EvolutionError(f"Generated {filename} uses banned operation: {node.func.id}")
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                modules = [alias.name.split(".")[0] for alias in node.names]
                if any(module in restricted for module in modules):
                    raise EvolutionError(f"Generated {filename} imports a restricted module")

    @staticmethod
    def _metadata(plan: CapabilityPlan, provider: str, model: str) -> Dict[str, Any]:
        return {
            "id": plan.capability_id,
            "name": plan.name,
            "version": "1.0.0",
            "created_date": datetime.now(timezone.utc).isoformat(),
            "entry_point": plan.entry_point,
            "supported_languages": plan.supported_languages,
            "dependencies": [],
            "test_coverage": None,
            "reuse_count": 0,
            "parent_capabilities": plan.parent_capabilities,
            "trigger_pattern": plan.trigger_pattern,
            "generation_reason": plan.reason,
            "model_provider": provider,
            "model": model,
        }
