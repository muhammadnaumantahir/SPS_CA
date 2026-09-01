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
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from layers.layer_03_experience.experience_log import ExperienceLog
from models.base import LLMProvider, LLMRequest


@dataclass(frozen=True)
class CapabilityPlan:
    """Deterministic plan for a capability produced from a failure pattern."""

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
    """Files generated for a capability before governance promotion."""

    capability_id: str
    files: Dict[str, str]
    metadata: Dict[str, Any]


@dataclass
class TestResults:
    """Sandbox-style validation result for a generated capability."""

    passed: bool
    return_code: int = 0
    output: str = ""
    coverage_percent: Optional[float] = None
    error: Optional[str] = None


class EvolutionError(RuntimeError):
    """Raised when an evolution operation cannot safely continue."""


class EvolutionEngine:
    """Detect, plan, generate, validate and stage new capabilities.

    ``ExperienceLog`` is the source of failure evidence. A model provider is
    optional for planning/tests, but required when generated source is
    requested. This keeps detection deterministic and makes the component
    straightforward to unit-test without Ollama.
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

    def should_evolve(
        self, experience_log: ExperienceLog, min_occurrences: Optional[int] = None
    ) -> bool:
        """Return True when any failure category reaches the threshold."""
        threshold = min_occurrences or self.min_occurrences
        if threshold < 1:
            raise ValueError("min_occurrences must be >= 1")
        return any(count >= threshold for count in experience_log.get_failure_patterns().values())

    def repeated_failure_patterns(
        self, experience_log: ExperienceLog, min_occurrences: Optional[int] = None
    ) -> Dict[str, int]:
        """Return recurring failure categories ordered by frequency."""
        threshold = min_occurrences or self.min_occurrences
        patterns = {
            name: count
            for name, count in experience_log.get_failure_patterns().items()
            if count >= threshold
        }
        return dict(sorted(patterns.items(), key=lambda item: (-item[1], item[0])))

    def plan_new_capability(
        self,
        trigger_pattern: str,
        experience_log: Optional[ExperienceLog] = None,
        capability_id: Optional[str] = None,
    ) -> CapabilityPlan:
        """Create a stable plan without invoking the model."""
        trigger = trigger_pattern.strip()
        if not trigger:
            raise ValueError("trigger_pattern must be non-empty")

        parent_ids: List[str] = []
        languages: List[str] = ["python"]
        if experience_log:
            for task in experience_log.tasks:
                if task.failure_category == trigger and task.selected_capability:
                    if task.selected_capability not in parent_ids:
                        parent_ids.append(task.selected_capability)
                if task.failure_category == trigger and task.target_language:
                    if task.target_language not in languages:
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

    def generate_capability_code(
        self, plan: CapabilityPlan, evidence: Optional[Sequence[str]] = None
    ) -> GeneratedCapability:
        """Ask the provider for a capability package and parse its JSON envelope."""
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
- Do not execute subprocesses, network calls, filesystem writes, eval, exec, or dynamic imports in the generated capability.
"""
        response = self.provider.generate(
            LLMRequest(
                prompt=prompt,
                system="You generate small, testable, deterministic SPS-CA capability modules.",
                model=self.model,
                temperature=0.1,
                timeout_seconds=self.timeout_seconds,
                metadata={"layer": "8", "capability_id": plan.capability_id},
            )
        )
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
        return GeneratedCapability(
            capability_id=plan.capability_id,
            files={
                "capability.py": capability_py,
                "tests.py": tests_py,
                "metadata.json": json.dumps(metadata, indent=2) + "\n",
                "README.md": str(payload["readme_md"]),
            },
            metadata=metadata,
        )

    def stage_capability(self, generated: GeneratedCapability) -> Path:
        """Write generated files to a non-active pending directory."""
        target = self.pending_root / generated.capability_id
        if target.exists():
            raise EvolutionError(f"Pending capability already exists: {target}")
        for relative, content in generated.files.items():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
        return target

    def test_capability(self, capability_id: str, staged_path: Optional[Path] = None) -> TestResults:
        """Run generated tests with Python's isolated test process."""
        path = staged_path or (self.pending_root / capability_id)
        tests = path / "tests.py"
        if not tests.exists():
            return TestResults(False, error=f"tests.py not found: {tests}")
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", str(tests)],
                cwd=str(path),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return TestResults(False, error=str(exc))
        output = (proc.stdout + "\n" + proc.stderr).strip()
        coverage = self._extract_coverage(output)
        passed = proc.returncode == 0 and (coverage is None or coverage >= 80.0)
        error = None if passed else ("Generated tests failed" if proc.returncode else "Coverage below 80%")
        return TestResults(passed, proc.returncode, output, coverage, error)

    def promote_capability(self, capability_id: str, approved: bool) -> Path:
        """Promote a validated staged capability only after governance approval."""
        source = self.pending_root / capability_id
        if not source.exists():
            raise EvolutionError(f"Staged capability does not exist: {source}")
        if not approved:
            raise EvolutionError("Governance approval is required before promotion")
        destination = self.generated_root / capability_id
        if destination.exists():
            raise EvolutionError(f"Generated capability already exists: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        for source_file in source.rglob("*"):
            if source_file.is_file():
                relative = source_file.relative_to(source)
                target = destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")
        return destination

    def _next_capability_id(self) -> str:
        ids: Iterable[str] = []
        if self.generated_root.exists():
            ids = [p.name for p in self.generated_root.iterdir() if p.is_dir()]
        numbers = [int(match.group(1)) for name in ids if (match := re.fullmatch(r"CAP-(\d+)", name))]
        pending_ids = []
        if self.pending_root.exists():
            pending_ids = [p.name for p in self.pending_root.iterdir() if p.is_dir()]
        numbers.extend(int(match.group(1)) for name in pending_ids if (match := re.fullmatch(r"CAP-(\d+)", name)))
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
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in banned:
                raise EvolutionError(f"Generated {filename} uses banned operation: {node.func.id}")
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                modules = [alias.name.split(".")[0] for alias in node.names]
                if any(module in {"subprocess", "socket", "requests", "urllib", "os", "shutil"} for module in modules):
                    raise EvolutionError(f"Generated {filename} imports a restricted module")

    @staticmethod
    def _extract_coverage(output: str) -> Optional[float]:
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
        return float(match.group(1)) if match else None

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
