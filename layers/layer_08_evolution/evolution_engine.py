"""Layer 8: Evolution Engine -- the core self-programming mechanism."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

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
FIRST_GENERATED_NUMBER = 10  # CAP-001..CAP-009 are the seed capabilities.

_COVERAGE_TOTAL_RE = re.compile(r"TOTAL\s+.*?(\d+(?:\.\d+)?)%\s*$", re.MULTILINE)


class EvolutionError(Exception):
    """Raised when an evolution step cannot complete."""


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "capability"


def _module_name(capability_id: str) -> str:
    return capability_id.lower().replace("-", "_")


class EvolutionEngine:
    """Layer 8: detect limitations and grow reusable capabilities."""

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

    def should_evolve(
        self, experience_log: ExperienceLog, min_occurrences: int = DEFAULT_MIN_OCCURRENCES
    ) -> bool:
        return any(
            count >= min_occurrences
            for count in experience_log.get_failure_patterns().values()
        )

    def get_trigger_patterns(
        self, experience_log: ExperienceLog, min_occurrences: int = DEFAULT_MIN_OCCURRENCES
    ) -> List[EvolutionTrigger]:
        patterns = experience_log.get_failure_patterns()
        triggers: List[EvolutionTrigger] = []
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
                    pattern=pattern,
                    occurrence_count=count,
                    trigger_task_ids=task_ids,
                )
            )
        triggers.sort(key=lambda item: item.occurrence_count, reverse=True)
        return triggers

    def plan_new_capability(
        self,
        trigger: EvolutionTrigger,
        capability_id: Optional[str] = None,
        supported_languages: Optional[List[str]] = None,
    ) -> CapabilityPlan:
        capability_id = capability_id or self.next_capability_id()
        return CapabilityPlan(
            capability_id=capability_id,
            name=f"{trigger.pattern.strip().title()} Handler",
            description=(
                f"Generated from {trigger.occurrence_count} repeated '{trigger.pattern}' failures "
                f"(tasks: {', '.join(trigger.trigger_task_ids) if trigger.trigger_task_ids else 'n/a'})."
            ),
            entry_point=f"capabilities.generated.{_module_name(capability_id)}.capability.run",
            supported_languages=supported_languages or ["python"],
            trigger_pattern=trigger.pattern,
            trigger_task_ids=list(trigger.trigger_task_ids),
            test_case_names=[
                f"test_{_slugify(trigger.pattern)}_modifies_supported_input",
                f"test_{_slugify(trigger.pattern)}_fails_gracefully_on_empty_input",
                f"test_{_slugify(trigger.pattern)}_no_ops_on_unsupported_language",
            ],
        )

    def plan_capability_for_gap(
        self,
        task_description: str,
        language: str,
        reason: str,
        task_id: Optional[str] = None,
    ) -> CapabilityPlan:
        from .gap_planner import CapabilityGapPlanner

        return CapabilityGapPlanner(
            seeds_dir=str(self.seeds_dir),
            generated_dir=str(self.generated_dir),
        ).plan(
            task_description=task_description,
            language=language,
            reason=reason,
            task_id=task_id,
        )

    def next_capability_id(self) -> str:
        used_numbers = set()
        for directory in (self.seeds_dir, self.generated_dir):
            if not directory.exists():
                continue
            for metadata_path in directory.glob("*/metadata.json"):
                try:
                    data = json.loads(metadata_path.read_text(encoding="utf-8"))
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

    @staticmethod
    def _generated_capability_source(plan: CapabilityPlan) -> str:
        trigger = plan.trigger_pattern
        common = (
            f'"""{plan.capability_id}: generated by Layer 8 (Evolution).\n\n'
            f'Trigger: {trigger}\n'
            f'Purpose: {plan.description}\n'
            '"""\n\n'
            'from __future__ import annotations\n\n'
            'from capabilities.base import CapabilityContext, CapabilityResult\n\n'
            f"SUPPORTED_LANGUAGES = {plan.supported_languages!r}\n"
            f"TRIGGER_PATTERN = {trigger!r}\n\n"
        )

        if trigger == "input_validation":
            body = '''def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in SUPPORTED_LANGUAGES:
        return CapabilityResult.ok(
            summary=f"{TRIGGER_PATTERN} capability does not support '{context.language}'."
        )
    if not context.code or not context.code.strip():
        return CapabilityResult.fail(error="No code provided to modify.")

    lines = context.code.splitlines()
    for index, line in enumerate(lines):
        marker = line.strip()
        if marker.startswith("def ") and "(" in marker and marker.endswith(":"):
            inside = marker.split("(", 1)[1].rsplit(")", 1)[0]
            parameter = (
                inside.split(",", 1)[0]
                .strip()
                .split(":", 1)[0]
                .strip()
                .split("=", 1)[0]
                .strip()
            )
            if parameter:
                indent = line[: len(line) - len(line.lstrip())] + "    "
                guard_line1 = f"{indent}if {parameter} is None:"
                guard_line2 = f"{indent}    raise ValueError('input validation failed: {parameter} is required')"
                guard = guard_line1 + chr(10) + guard_line2
                lines.insert(index + 1, guard)
                return CapabilityResult.ok(
                    summary="Added input validation.",
                    modified_code=chr(10).join(lines),
                    findings=[{"issue": "input-validation-added", "parameter": parameter}],
                )
    return CapabilityResult.fail(error="No safe function parameter was found to validate.")
'''
            return common + body

        if trigger == "sql_parameterization":
            body = '''import re


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in SUPPORTED_LANGUAGES:
        return CapabilityResult.ok(
            summary=f"{TRIGGER_PATTERN} capability does not support '{context.language}'."
        )
    if not context.code or not context.code.strip():
        return CapabilityResult.fail(error="No code provided to modify.")

    pattern = re.compile(r'cursor\\.execute\\(f(["\\\'])(.*?)\\1\\)')
    match = pattern.search(context.code)
    if not match:
        return CapabilityResult.fail(error="No safely parameterizable cursor.execute f-string was found.")
    query = match.group(2)
    variables = re.findall(r'\\{\\s*([A-Za-z_]\\w*)\\s*\\}', query)
    if len(variables) != 1:
        return CapabilityResult.fail(error="Expected exactly one SQL interpolation variable.")

    variable = variables[0]
    parameterized = re.sub(
        r'\\{\\s*' + re.escape(variable) + r'\\s*\\}',
        '%s',
        query,
    )
    replacement = f'cursor.execute("{parameterized}", ({variable},))'
    updated = context.code[:match.start()] + replacement + context.code[match.end():]
    return CapabilityResult.ok(
        summary="Parameterized SQL interpolation.",
        modified_code=updated,
        findings=[{"issue": "sql-parameterized", "parameter": variable}],
    )
'''
            return common + body

        if trigger == "logging":
            body = '''import re


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in SUPPORTED_LANGUAGES:
        return CapabilityResult.ok(
            summary=f"{TRIGGER_PATTERN} capability does not support '{context.language}'."
        )
    if not context.code or not context.code.strip():
        return CapabilityResult.fail(error="No code provided to modify.")

    lines = context.code.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r'^(\\s*)def\\s+(\\w+)\\s*\\(', line)
        if match:
            prefix = (
                "import logging" + chr(10) + "logger = logging.getLogger(__name__)" + chr(10) + chr(10)
                if "import logging" not in context.code
                else ""
            )
            log_line = f"{match.group(1)}    logger.info('{match.group(2)} called')"
            updated = prefix + chr(10).join(
                lines[: index + 1] + [log_line] + lines[index + 1 :]
            )
            return CapabilityResult.ok(
                summary="Added function-call logging.",
                modified_code=updated,
                findings=[{"issue": "request-logging-added", "function": match.group(2)}],
            )
    return CapabilityResult.fail(error="No function was found to instrument.")
'''
            return common + body

        body = '''def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in SUPPORTED_LANGUAGES:
        return CapabilityResult.ok(
            summary=f"{TRIGGER_PATTERN} capability does not support '{context.language}'."
        )
    if not context.code or not context.code.strip():
        return CapabilityResult.fail(error="No code provided to modify.")

    nl = chr(10)
    marker = nl + nl + "# Layer 8 generated capability: " + TRIGGER_PATTERN + nl
    updated = context.code.rstrip() + marker
    return CapabilityResult.ok(
        summary=f"Generated {TRIGGER_PATTERN} marker transformation.",
        modified_code=updated,
        findings=[{"issue": "generated-transform", "trigger": TRIGGER_PATTERN}],
    )
'''
        return common + body

    def generate_capability_code(self, plan: CapabilityPlan) -> GeneratedCapabilityFiles:
        primary_language = plan.supported_languages[0]
        trigger = plan.trigger_pattern
        names = plan.test_case_names or [
            f"test_{_slugify(trigger)}_modifies_supported_input",
            f"test_{_slugify(trigger)}_fails_gracefully_on_empty_input",
            f"test_{_slugify(trigger)}_no_ops_on_unsupported_language",
        ]
        examples = {
            "input_validation": "def calculate(age):\n    return age + 10\n",
            "sql_parameterization": 'cursor.execute(f"select * from users where id={user_id}")\n',
            "logging": "def process(value):\n    return value * 2\n",
        }
        supported_example = examples.get(trigger, "def process(value):\n    return value\n")
        tests_code = f'''"""Tests for {plan.capability_id}."""

from pathlib import Path
import importlib.util
import os
import sys

REPO_ROOT = os.environ.get("SPS_CA_REPO_ROOT")
if REPO_ROOT and REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

_MODULE_PATH = Path(__file__).with_name("capability.py")
_SPEC = importlib.util.spec_from_file_location("generated_capability_under_test", _MODULE_PATH)
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
run = _MODULE.run


def {names[0]}():
    result = run(_MODULE.CapabilityContext(code={supported_example!r}, language={primary_language!r}))
    assert result.success
    assert result.modified_code
    assert result.modified_code != {supported_example!r}
    assert result.findings


def {names[1]}():
    result = run(_MODULE.CapabilityContext(code="", language={primary_language!r}))
    assert not result.success


def {names[2]}():
    result = run(_MODULE.CapabilityContext(code="some code", language="__unsupported__"))
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
            "tags": ["evolution", "generated", trigger],
            "generated": True,
            "failure_pattern": trigger,
            "trigger_tasks": plan.trigger_task_ids,
            "reuse_count": 0,
            "test_coverage": None,
            "provenance": plan.provenance,
        }
        readme = (
            f"# {plan.capability_id}: {plan.name}\n\n"
            f"{plan.description}\n\n"
            "Generated by Layer 8 (Evolution) after a capability gap was detected.\n"
        )
        return GeneratedCapabilityFiles(
            capability_code=self._generated_capability_source(plan),
            tests_code=tests_code,
            metadata=metadata,
            readme=readme,
        )

    def implement_capability(self, plan: CapabilityPlan, files: GeneratedCapabilityFiles) -> Path:
        module_dir = self.generated_dir / _module_name(plan.capability_id)
        module_dir.mkdir(parents=True, exist_ok=True)
        (module_dir / "__init__.py").write_text("", encoding="utf-8")
        (module_dir / "capability.py").write_text(files.capability_code, encoding="utf-8")
        (module_dir / "tests.py").write_text(files.tests_code, encoding="utf-8")
        (module_dir / "metadata.json").write_text(
            json.dumps(files.metadata, indent=2) + "\n", encoding="utf-8"
        )
        (module_dir / "README.md").write_text(files.readme, encoding="utf-8")
        if not (self.generated_dir / "__init__.py").exists():
            self.generated_dir.mkdir(parents=True, exist_ok=True)
            (self.generated_dir / "__init__.py").write_text("", encoding="utf-8")
        return module_dir

    def test_capability(self, capability_id: str, project_root: str = ".") -> TestRunResult:
        module_dir = self.generated_dir / _module_name(capability_id)
        tests_path = module_dir / "tests.py"
        if not tests_path.exists():
            raise EvolutionError(f"No generated tests found for {capability_id}: {tests_path}")

        env = os.environ.copy()
        env["SPS_CA_REPO_ROOT"] = str(Path(__file__).resolve().parents[2])
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(tests_path),
                "-v",
                f"--cov={module_dir}",
                "--cov-report=term-missing",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        output = completed.stdout + completed.stderr
        return TestRunResult(
            passed=completed.returncode == 0,
            tests_run=len(re.findall(r"\bPASSED\b|\bFAILED\b", output)),
            tests_failed=len(re.findall(r"\bFAILED\b", output)),
            coverage_percent=self._parse_coverage(output),
            output=output,
        )

    @staticmethod
    def _parse_coverage(output: str) -> Optional[float]:
        match = _COVERAGE_TOTAL_RE.search(output)
        return float(match.group(1)) if match else None

    def register_capability(
        self,
        plan: CapabilityPlan,
        files: GeneratedCapabilityFiles,
        test_result: TestRunResult,
        governance_decision_status: Optional[DecisionStatus] = None,
    ) -> bool:
        if (
            not test_result.passed
            or not test_result.meets_coverage_gate
            or governance_decision_status == DecisionStatus.REJECTED
        ):
            return False

        registry: dict = {}
        if self.registry_path.exists():
            try:
                registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                registry = {}

        entry = dict(files.metadata)
        entry["test_coverage"] = test_result.coverage_percent
        registry[plan.capability_id] = entry
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(
            json.dumps(registry, indent=2) + "\n", encoding="utf-8"
        )
        return True

    def develop_capability_for_gap(
        self,
        plan: CapabilityPlan,
        *,
        project_root: str = ".",
        governance_decision_status: Optional[DecisionStatus] = None,
    ) -> Dict[str, Any]:
        files = self.generate_capability_code(plan)
        module_dir = self.implement_capability(plan, files)
        result = self.test_capability(plan.capability_id, project_root=project_root)
        registered = self.register_capability(
            plan,
            files,
            result,
            governance_decision_status=governance_decision_status,
        )
        return {
            "capability_id": plan.capability_id,
            "module_dir": str(module_dir),
            "implemented": True,
            "test_result": {
                "passed": result.passed,
                "tests_run": result.tests_run,
                "tests_failed": result.tests_failed,
                "coverage_percent": result.coverage_percent,
            },
            "registered": registered,
        }

    def build_commit_message(
        self,
        plan: CapabilityPlan,
        test_result: TestRunResult,
        governance_decision_id: Optional[str] = None,
    ) -> str:
        coverage = (
            f"{test_result.coverage_percent:.1f}%"
            if test_result.coverage_percent is not None
            else "unmeasured"
        )
        lines = [
            f"EVOLUTION: {plan.capability_id} {plan.name}",
            f"Generated from {plan.trigger_pattern} capability gap.",
            f"Test coverage: {coverage}. Entry point: {plan.entry_point.rsplit('.', 1)[-1]}().",
            f"Supported languages: {', '.join(plan.supported_languages)}.",
            "",
            f"Trigger rationale: {plan.description}",
        ]
        if governance_decision_id:
            lines.append(f"Decision: {governance_decision_id}")
        return "\n".join(lines)

    def run_evolution_cycle(
        self,
        experience_log: ExperienceLog,
        min_occurrences: int = DEFAULT_MIN_OCCURRENCES,
        project_root: str = ".",
    ) -> Optional[EvolutionRecord]:
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
            plan,
            files,
            test_result,
            governance_decision_status,
        )
        record = EvolutionRecord(
            capability_id=plan.capability_id,
            trigger_pattern=trigger.pattern,
            trigger_task_ids=trigger.trigger_task_ids,
            test_result=test_result,
            governance_decision_id=governance_decision_id,
            registered=registered,
            commit_message=self.build_commit_message(
                plan,
                test_result,
                governance_decision_id,
            ),
        )
        self._save_record(record)
        return record

    def _save_record(self, record: EvolutionRecord) -> None:
        self.evaluation_dir.mkdir(parents=True, exist_ok=True)
        (self.evaluation_dir / f"{record.capability_id}.json").write_text(
            json.dumps(record.to_dict(), indent=2) + "\n",
            encoding="utf-8",
        )
