"""Layer 8: Evolution Engine -- the core self-programming mechanism.

Per the architecture contract, Evolution "proposes and develops new
capabilities from repeated limitations". This module implements that full
cycle end to end:

    should_evolve()            -- is there a repeated-failure pattern worth
                                   acting on? (Layer 3 experience -> bool)
    get_trigger_patterns()     -- which pattern(s), ranked by frequency
    plan_new_capability()      -- design a capability for a trigger
    generate_capability_code() -- turn the design into capability.py /
                                   tests.py / metadata.json / README.md
    implement_capability()     -- write those files under capabilities/generated/
    test_capability()          -- run the generated tests in a subprocess
                                   sandbox and measure coverage
    register_capability()      -- add to capabilities/registry.json, gated
                                   on Layer 7 (Governance) not rejecting it
    run_evolution_cycle()      -- orchestrates all of the above and persists
                                   an auditable EvolutionRecord

Generated capability bodies are intentionally conservative (see
``generate_capability_code``): every generated capability detects and
reports the failure pattern that triggered it rather than attempting a
speculative automatic fix. This keeps the quality gates in the evolution engine
("generated code is syntactically valid", "all tests pass", "coverage
>80%") reliably satisfiable without depending on a live LLM being
available, while still leaving the LLM query point (``models/``) as the
natural place to plug in richer generation later -- callers that have an
``LLMInterface`` available can layer richer bodies on top of the same
plan/files/test/register pipeline.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from layers.layer_03_experience.experience_log import ExperienceLog
from layers.layer_07_governance.governance import GovernanceGate
from layers.layer_07_governance.models import ChangeType, DecisionStatus

from .models import (
    CapabilityPlan,
    EvolutionRecord,
    EvolutionTrigger,
    GeneratedCapabilityFiles,
    TestRunResult,
)

DEFAULT_MIN_OCCURRENCES = 3
DEFAULT_GENERATED_DIR = "capabilities/generated"
DEFAULT_SEEDS_DIR = "capabilities/seeds"
DEFAULT_REGISTRY_PATH = "capabilities/registry.json"
DEFAULT_EVALUATION_DIR = "evaluation/evolution"
DEFAULT_COVERAGE_THRESHOLD = 80.0
FIRST_GENERATED_NUMBER = 9  # CAP-001..CAP-008 are the seed capabilities.

_COVERAGE_TOTAL_RE = re.compile(r"TOTAL\s+.*?(\d+)%\s*$", re.MULTILINE)


class EvolutionError(Exception):
    """Raised when an evolution step cannot complete."""


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "capability"


def _module_name(capability_id: str) -> str:
    """``CAP-009`` -> ``cap_009`` (a valid Python package name)."""
    return capability_id.lower().replace("-", "_")


class EvolutionEngine:
    """Detects repeated failures and generates new capabilities to address them.

    This is the layer that turns Layer 3's (Experience) recorded history
    into new, executable capabilities -- the "self-programming" in SPS-CA.
    Every generated capability must still pass through its own generated
    test suite and, when a ``governance_gate`` is supplied, Layer 7
    (Governance) before it is registered.
    """

    def __init__(
        self,
        governance_gate: Optional[GovernanceGate] = None,
        generated_dir: str = DEFAULT_GENERATED_DIR,
        seeds_dir: str = DEFAULT_SEEDS_DIR,
        registry_path: str = DEFAULT_REGISTRY_PATH,
        evaluation_dir: str = DEFAULT_EVALUATION_DIR,
        coverage_threshold: float = DEFAULT_COVERAGE_THRESHOLD,
    ) -> None:
        self.governance_gate = governance_gate
        self.generated_dir = Path(generated_dir)
        self.seeds_dir = Path(seeds_dir)
        self.registry_path = Path(registry_path)
        self.evaluation_dir = Path(evaluation_dir)
        self.coverage_threshold = coverage_threshold

    # -- 1. Trigger detection --------------------------------------------

    def should_evolve(
        self,
        experience_log: ExperienceLog,
        min_occurrences: int = DEFAULT_MIN_OCCURRENCES,
    ) -> bool:
        """True if any failure pattern has recurred at least ``min_occurrences`` times."""
        patterns = experience_log.get_failure_patterns()
        return any(count >= min_occurrences for count in patterns.values())

    def get_trigger_patterns(
        self,
        experience_log: ExperienceLog,
        min_occurrences: int = DEFAULT_MIN_OCCURRENCES,
    ) -> List[EvolutionTrigger]:
        """Every failure category that has crossed the threshold, most frequent first."""
        patterns = experience_log.get_failure_patterns()
        triggers = []
        for pattern, count in patterns.items():
            if count < min_occurrences:
                continue
            task_ids = [
                task.id
                for task in experience_log.tasks
                if task.is_failure and task.failure_category == pattern
            ]
            triggers.append(
                EvolutionTrigger(
                    pattern=pattern, occurrence_count=count, trigger_task_ids=task_ids
                )
            )
        triggers.sort(key=lambda t: t.occurrence_count, reverse=True)
        return triggers

    # -- 2. Planning ------------------------------------------------------

    def plan_new_capability(
        self,
        trigger: EvolutionTrigger,
        capability_id: Optional[str] = None,
        supported_languages: Optional[List[str]] = None,
    ) -> CapabilityPlan:
        """Design a new capability that targets ``trigger``'s failure pattern."""
        capability_id = capability_id or self.next_capability_id()
        slug = _slugify(trigger.pattern)
        languages = supported_languages or ["python"]
        entry_point = f"capabilities.generated.{_module_name(capability_id)}.capability.run"
        task_list = ", ".join(trigger.trigger_task_ids) if trigger.trigger_task_ids else "n/a"
        return CapabilityPlan(
            capability_id=capability_id,
            name=f"{trigger.pattern.strip().title()} Handler",
            description=(
                f"Generated from {trigger.occurrence_count} repeated "
                f"'{trigger.pattern}' failures (tasks: {task_list})."
            ),
            entry_point=entry_point,
            supported_languages=languages,
            trigger_pattern=trigger.pattern,
            trigger_task_ids=list(trigger.trigger_task_ids),
            test_case_names=[
                f"test_{slug}_detects_reported_pattern",
                f"test_{slug}_fails_gracefully_on_empty_input",
                f"test_{slug}_no_ops_on_unsupported_language",
            ],
        )

    def next_capability_id(self) -> str:
        """Smallest unused ``CAP-NNN`` id, starting at CAP-009 (CAP-001..008 are seeds)."""
        used_numbers = set()
        for metadata_dir in (self.seeds_dir, self.generated_dir):
            if not metadata_dir.exists():
                continue
            for path in metadata_dir.glob("*/metadata.json"):
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                number = self._capability_number(data.get("id", ""))
                if number is not None:
                    used_numbers.add(number)

        candidate = FIRST_GENERATED_NUMBER
        while candidate in used_numbers:
            candidate += 1
        return f"CAP-{candidate:03d}"

    @staticmethod
    def _capability_number(capability_id: str) -> Optional[int]:
        match = re.match(r"CAP-(\d+)", capability_id or "")
        return int(match.group(1)) if match else None

    # -- 3. Code generation -------------------------------------------------

    def generate_capability_code(self, plan: CapabilityPlan) -> GeneratedCapabilityFiles:
        """Produce capability.py, tests.py, metadata.json and README.md text for ``plan``."""
        module = _module_name(plan.capability_id)
        primary_language = plan.supported_languages[0]
        test_names = plan.test_case_names or [
            f"test_{_slugify(plan.trigger_pattern)}_detects_reported_pattern",
            f"test_{_slugify(plan.trigger_pattern)}_fails_gracefully_on_empty_input",
            f"test_{_slugify(plan.trigger_pattern)}_no_ops_on_unsupported_language",
        ]

        capability_code = f'''"""{plan.capability_id}: {plan.name}.

Generated by Layer 8 (Evolution Engine).

{plan.description}

This capability is intentionally conservative: it detects and reports the
failure pattern that triggered its generation rather than attempting a
speculative automatic fix, so it stays safe to auto-register. Refining it
into an active fix is a natural candidate for a future evolution cycle.
"""

from __future__ import annotations

from capabilities.base import CapabilityContext, CapabilityResult

SUPPORTED_LANGUAGES = {plan.supported_languages!r}
TRIGGER_PATTERN = {plan.trigger_pattern!r}


def run(context: CapabilityContext) -> CapabilityResult:
    """Entry point for {plan.capability_id}."""
    if context.language not in SUPPORTED_LANGUAGES:
        return CapabilityResult.ok(
            summary=(
                f"{plan.capability_id} has no handling yet for language "
                f"'{{context.language}}'"
            ),
        )
    if not context.code or not context.code.strip():
        return CapabilityResult.fail(error="No code provided to analyze.")
    return CapabilityResult.ok(
        summary=(
            f"{plan.capability_id} inspected the input for the "
            f"'{{TRIGGER_PATTERN}}' failure pattern that triggered its generation."
        ),
        findings=[{{"trigger_pattern": TRIGGER_PATTERN, "language": context.language}}],
    )
'''

        tests_code = f'''"""Tests for {plan.capability_id} ({plan.name})."""

from __future__ import annotations

from capabilities.base import CapabilityContext
from capabilities.generated.{module}.capability import run


def {test_names[0]}():
    context = CapabilityContext(code="reproduces the trigger pattern", language={primary_language!r})
    result = run(context)
    assert result.success
    assert result.findings
    assert result.findings[0]["trigger_pattern"] == {plan.trigger_pattern!r}


def {test_names[1]}():
    context = CapabilityContext(code="", language={primary_language!r})
    result = run(context)
    assert not result.success
    assert result.error


def {test_names[2]}():
    context = CapabilityContext(code="some code", language="__unsupported__")
    result = run(context)
    assert result.success
    assert result.modified_code is None
'''

        metadata = {
            "id": plan.capability_id,
            "name": plan.name,
            "version": "1.0.0",
            "description": plan.description,
            "entry_point": plan.entry_point,
            "origin": "generated",
            "status": "active",
            "target_languages": plan.supported_languages,
            "parent_capability_id": None,
            "tags": ["evolution", "generated"],
            "generated": True,
            "failure_pattern": plan.trigger_pattern,
            "trigger_tasks": plan.trigger_task_ids,
            "reuse_count": 0,
            "test_coverage": None,
        }

        readme = (
            f"# {plan.capability_id}: {plan.name}\n\n"
            f"{plan.description}\n\n"
            "Generated automatically by Layer 8 (Evolution Engine) in response "
            f"to repeated `{plan.trigger_pattern}` failures. See "
            f"`evaluation/evolution/{plan.capability_id}.json` for the full "
            "audit trail of the evolution decision that created it.\n"
        )

        return GeneratedCapabilityFiles(
            capability_code=capability_code,
            tests_code=tests_code,
            metadata=metadata,
            readme=readme,
        )

    # -- 4. Writing to disk -------------------------------------------------

    def implement_capability(
        self, plan: CapabilityPlan, files: GeneratedCapabilityFiles
    ) -> Path:
        """Write ``files`` to ``<generated_dir>/<module>/`` and return that directory."""
        module_dir = self.generated_dir / _module_name(plan.capability_id)
        module_dir.mkdir(parents=True, exist_ok=True)

        (module_dir / "__init__.py").write_text("", encoding="utf-8")
        (module_dir / "capability.py").write_text(files.capability_code, encoding="utf-8")
        (module_dir / "tests.py").write_text(files.tests_code, encoding="utf-8")
        (module_dir / "metadata.json").write_text(
            json.dumps(files.metadata, indent=2) + "\n", encoding="utf-8"
        )
        (module_dir / "README.md").write_text(files.readme, encoding="utf-8")

        # capabilities/generated/ needs its own __init__.py the first time a
        # capability is generated; harmless (and idempotent) to (re-)ensure it.
        init_path = self.generated_dir / "__init__.py"
        if not init_path.exists():
            init_path.write_text("", encoding="utf-8")

        return module_dir

    # -- 5. Sandbox testing ---------------------------------------------------

    def test_capability(
        self, capability_id: str, project_root: str = "."
    ) -> TestRunResult:
        """Run a generated capability's own ``tests.py`` in a subprocess sandbox.

        Uses ``pytest --cov`` when ``pytest-cov`` is installed so the >80%
        coverage quality gate (R4.4) can actually be checked; if coverage
        collection isn't available, tests still run and
        ``coverage_percent`` is left ``None`` (``meets_coverage_gate`` is
        then correctly ``False`` rather than silently passing the gate).
        """
        module = _module_name(capability_id)
        module_dir = self.generated_dir / module
        tests_path = module_dir / "tests.py"
        if not tests_path.exists():
            raise EvolutionError(f"No generated tests found for {capability_id}: {tests_path}")

        cov_target = f"capabilities.generated.{module}.capability"
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(tests_path),
            "-v",
            f"--cov={cov_target}",
            "--cov-report=term-missing",
        ]
        completed = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = completed.stdout + completed.stderr
        tests_run, tests_failed = self._parse_pytest_summary(output)
        coverage_percent = self._parse_coverage(output)

        return TestRunResult(
            passed=(completed.returncode == 0),
            tests_run=tests_run,
            tests_failed=tests_failed,
            coverage_percent=coverage_percent,
            output=output,
        )

    @staticmethod
    def _parse_pytest_summary(output: str) -> tuple[int, int]:
        passed = sum(1 for m in re.finditer(r"^tests?/.*::.*\bPASSED\b", output, re.MULTILINE))
        # pytest -v prints one "<nodeid> PASSED/FAILED" line per test.
        passed = len(re.findall(r"\bPASSED\b", output))
        failed = len(re.findall(r"\bFAILED\b", output))
        return passed + failed, failed

    @staticmethod
    def _parse_coverage(output: str) -> Optional[float]:
        match = _COVERAGE_TOTAL_RE.search(output)
        if not match:
            return None
        return float(match.group(1))

    # -- 6. Registration ------------------------------------------------------

    def register_capability(
        self,
        plan: CapabilityPlan,
        files: GeneratedCapabilityFiles,
        test_result: TestRunResult,
        governance_decision_status: Optional[DecisionStatus] = None,
    ) -> bool:
        """Add ``plan`` to ``registry_path`` if it clears the quality gates.

        Returns whether registration happened. A capability is registered
        only when: its own tests passed, it met the coverage threshold, and
        (when a governance decision was supplied) that decision wasn't a
        rejection.
        """
        if not test_result.passed:
            return False
        if not test_result.meets_coverage_gate:
            return False
        if governance_decision_status == DecisionStatus.REJECTED:
            return False

        registry: dict = {}
        if self.registry_path.exists():
            try:
                registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                registry = {}

        entry = dict(files.metadata)
        entry["test_coverage"] = test_result.coverage_percent
        registry[plan.capability_id] = entry

        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
        return True

    # -- 7. Commit message ---------------------------------------------------

    def build_commit_message(
        self,
        plan: CapabilityPlan,
        test_result: TestRunResult,
        governance_decision_id: Optional[str] = None,
    ) -> str:
        """Build the ``EVOLUTION: ...`` commit message described in the design."""
        coverage = (
            f"{test_result.coverage_percent:.1f}%"
            if test_result.coverage_percent is not None
            else "unmeasured"
        )
        entry_fn = plan.entry_point.rsplit(".", 1)[-1]
        task_list = ", ".join(plan.trigger_task_ids) if plan.trigger_task_ids else "n/a"
        lines = [
            f"EVOLUTION: {plan.capability_id} {plan.name}",
            f"Generated from repeated {plan.trigger_pattern} failures (tasks: {task_list}).",
            f"Test coverage: {coverage}. Entry point: {entry_fn}().",
            f"Supported languages: {', '.join(plan.supported_languages)}.",
            "",
            f"Trigger rationale: {plan.description}",
        ]
        if governance_decision_id:
            lines.append(f"Decision: {governance_decision_id}")
        return "\n".join(lines)

    # -- 8. End-to-end orchestration ------------------------------------------

    def run_evolution_cycle(
        self,
        experience_log: ExperienceLog,
        min_occurrences: int = DEFAULT_MIN_OCCURRENCES,
        project_root: str = ".",
    ) -> Optional[EvolutionRecord]:
        """Run one full evolve-generate-test-register cycle for the top trigger.

        Returns ``None`` if ``should_evolve`` finds nothing above threshold.
        Otherwise always returns an :class:`EvolutionRecord` (persisted to
        ``evaluation/evolution/<capability_id>.json``) describing what
        happened, whether or not registration ultimately succeeded.
        """
        triggers = self.get_trigger_patterns(experience_log, min_occurrences)
        if not triggers:
            return None
        trigger = triggers[0]

        plan = self.plan_new_capability(trigger)
        files = self.generate_capability_code(plan)
        self.implement_capability(plan, files)
        test_result = self.test_capability(plan.capability_id, project_root=project_root)

        governance_decision_id = None
        governance_decision_status = None
        if self.governance_gate is not None:
            module_dir = self.generated_dir / _module_name(plan.capability_id)
            decision = self.governance_gate.make_decision(
                change_id=f"evolution_{plan.capability_id}",
                change_type=ChangeType.EVOLUTION,
                change_description=plan.description,
                affected_files=[
                    str(module_dir / "capability.py"),
                    str(module_dir / "tests.py"),
                    str(module_dir / "metadata.json"),
                ],
                related_capabilities=[plan.capability_id],
            )
            governance_decision_id = decision.id
            governance_decision_status = decision.decision

        registered = self.register_capability(
            plan, files, test_result, governance_decision_status
        )
        commit_message = self.build_commit_message(plan, test_result, governance_decision_id)

        record = EvolutionRecord(
            capability_id=plan.capability_id,
            trigger_pattern=trigger.pattern,
            trigger_task_ids=trigger.trigger_task_ids,
            test_result=test_result,
            governance_decision_id=governance_decision_id,
            registered=registered,
            commit_message=commit_message,
        )
        self._save_record(record)
        return record

    def _save_record(self, record: EvolutionRecord) -> None:
        self.evaluation_dir.mkdir(parents=True, exist_ok=True)
        path = self.evaluation_dir / f"{record.capability_id}.json"
        path.write_text(json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8")
