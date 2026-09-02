"""Layer 8: Evolution Engine -- the core self-programming mechanism.

Per the architecture contract, Evolution proposes and develops new capabilities
from repeated limitations. The supervisor-facing path also supports an
immediate capability gap: once Layers 2/9 determine that no suitable capability
exists, Layer 8 plans, generates, tests, and registers a new capability.
"""

from __future__ import annotations

import json
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
FIRST_GENERATED_NUMBER = 9

_COVERAGE_TOTAL_RE = re.compile(r"TOTAL\s+.*?(\d+)%\s*$", re.MULTILINE)


class EvolutionError(Exception):
    """Raised when an evolution step cannot complete."""


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "capability"


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

    def should_evolve(self, experience_log: ExperienceLog, min_occurrences: int = DEFAULT_MIN_OCCURRENCES) -> bool:
        patterns = experience_log.get_failure_patterns()
        return any(count >= min_occurrences for count in patterns.values())

    def get_trigger_patterns(self, experience_log: ExperienceLog, min_occurrences: int = DEFAULT_MIN_OCCURRENCES) -> List[EvolutionTrigger]:
        patterns = experience_log.get_failure_patterns()
        triggers = []
        for pattern, count in patterns.items():
            if count < min_occurrences:
                continue
            task_ids = [task.id for task in experience_log.tasks if task.is_failure and task.failure_category == pattern]
            triggers.append(EvolutionTrigger(pattern=pattern, occurrence_count=count, trigger_task_ids=task_ids))
        triggers.sort(key=lambda t: t.occurrence_count, reverse=True)
        return triggers

    def plan_new_capability(self, trigger: EvolutionTrigger, capability_id: Optional[str] = None, supported_languages: Optional[List[str]] = None) -> CapabilityPlan:
        capability_id = capability_id or self.next_capability_id()
        slug = _slugify(trigger.pattern)
        languages = supported_languages or ["python"]
        return CapabilityPlan(
            capability_id=capability_id,
            name=f"{trigger.pattern.strip().title()} Handler",
            description=(
                f"Generated from {trigger.occurrence_count} repeated '{trigger.pattern}' failures "
                f"(tasks: {', '.join(trigger.trigger_task_ids) if trigger.trigger_task_ids else 'n/a'})."
            ),
            entry_point=f"capabilities.generated.{_module_name(capability_id)}.capability.run",
            supported_languages=languages,
            trigger_pattern=trigger.pattern,
            trigger_task_ids=list(trigger.trigger_task_ids),
            test_case_names=[
                f"test_{slug}_modifies_supported_input",
                f"test_{slug}_fails_gracefully_on_empty_input",
                f"test_{slug}_no_ops_on_unsupported_language",
            ],
        )

    def plan_capability_for_gap(self, task_description: str, language: str, reason: str, task_id: Optional[str] = None) -> CapabilityPlan:
        from .gap_planner import CapabilityGapPlanner
        planner = CapabilityGapPlanner(seeds_dir=str(self.seeds_dir), generated_dir=str(self.generated_dir))
        return planner.plan(task_description=task_description, language=language, reason=reason, task_id=task_id)

    def next_capability_id(self) -> str:
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

    def generate_capability_code(self, plan: CapabilityPlan) -> GeneratedCapabilityFiles:
        """Generate an executable capability plus tests and provenance metadata."""
        module = _module_name(plan.capability_id)
        primary_language = plan.supported_languages[0]
        trigger = plan.trigger_pattern
        test_names = plan.test_case_names or [
            f"test_{_slugify(trigger)}_modifies_supported_input",
            f"test_{_slugify(trigger)}_fails_gracefully_on_empty_input",
            f"test_{_slugify(trigger)}_no_ops_on_unsupported_language",
        ]

        capability_code = f'''"""{plan.capability_id}: generated by Layer 8 (Evolution).

Trigger: {trigger}
Purpose: {plan.description}
"""

from __future__ import annotations

import ast
import re

from capabilities.base import CapabilityContext, CapabilityResult

SUPPORTED_LANGUAGES = {plan.supported_languages!r}
TRIGGER_PATTERN = {trigger!r}


def _input_validation(code: str) -> tuple[str, list[dict]]:
    lines = code.splitlines()
    findings = []
    function_pattern = re.compile(r"^(\\s*)def\\s+(\\w+)\\s*\\(([^)]*)\\)\\s*:")
    for index, line in enumerate(lines):
        match = function_pattern.match(line)
        if not match:
            continue
        params = [p.strip().split(":", 1)[0].strip() for p in match.group(3).split(",") if p.strip()]
        if not params:
            continue
        param = re.sub(r"[^A-Za-z0-9_]", "", params[0])
        if not param:
            continue
        indent = match.group(1) + "    "
        validation = f"{{indent}}if {{param}} is None:\\n{{indent}}    raise ValueError('input validation failed: {{param}} is required')"
        # Avoid adding the same guard twice.
        following = "\\n".join(lines[index + 1:index + 4])
        if f"if {{param}} is None:" in following:
            continue
        lines.insert(index + 1, validation.format(indent=indent, param=param))
        findings.append({{"issue": "input-validation-added", "function": match.group(2), "parameter": param}})
        break
    return "\\n".join(lines), findings


def _sql_parameterization(code: str) -> tuple[str, list[dict]]:
    pattern = re.compile(r"cursor\\.execute\\(f([\\\"'])(.*?)\\1\\)")
    match = pattern.search(code)
    if not match:
        return code, []
    query = match.group(2)
    variables = re.findall(r"\\{{\\s*([A-Za-z_]\\w*)\\s*\\}}", query)
    if len(variables) != 1:
        return code, []
    variable = variables[0]
    parameterized = re.sub(r"\\{{\\s*" + re.escape(variable) + r"\\s*\\}}", "%s", query)
    replacement = f"cursor.execute(\\\"{{parameterized}}\\\", ({{variable}},))"
    updated = code[:match.start()] + replacement + code[match.end():]
    return updated, [{{"issue": "sql-parameterized", "parameter": variable}}]


def _logging(code: str) -> tuple[str, list[dict]]:
    if "import logging" not in code and "from logging" not in code:
        code = "import logging\\nlogger = logging.getLogger(__name__)\\n\\n" + code
    lines = code.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^(\\s*)def\\s+(\\w+)\\s*\\(", line)
        if match:
            indent = match.group(1) + "    "
            body = f"{{indent}}logger.info('{{match.group(2)}} called')"
            following = "\\n".join(lines[index + 1:index + 4])
            if "logger.info(" not in following:
                lines.insert(index + 1, body)
            return "\\n".join(lines), [{{"issue": "request-logging-added", "function": match.group(2)}}]
    return code, []


def _modify(code: str) -> tuple[str, list[dict]]:
    if TRIGGER_PATTERN == "input_validation":
        return _input_validation(code)
    if TRIGGER_PATTERN == "sql_parameterization":
        return _sql_parameterization(code)
    if TRIGGER_PATTERN == "logging":
        return _logging(code)
    return code, []


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in SUPPORTED_LANGUAGES:
        return CapabilityResult.ok(summary=f"{{TRIGGER_PATTERN}} capability does not support '{{context.language}}'.")
    if not context.code or not context.code.strip():
        return CapabilityResult.fail(error="No code provided to modify.")
    updated, findings = _modify(context.code)
    if not findings:
        return CapabilityResult.fail(error=f"{{TRIGGER_PATTERN}} capability could not safely transform this code.")
    try:
        ast.parse(updated) if context.language == "python" else None
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Generated modification is not valid Python: {{exc}}")
    return CapabilityResult.ok(
        summary=f"Generated {{TRIGGER_PATTERN}} capability modified the submitted code.",
        modified_code=updated,
        findings=findings,
    )
'''

        examples = {
            "input_validation": "def calculate(age):\n    return age + 10\n",
            "sql_parameterization": 'cursor.execute(f"select * from users where id={user_id}")\n',
            "logging": "def process(value):\n    return value * 2\n",
        }
        supported_example = examples.get(trigger, "def process(value):\n    return value\n")
        tests_code = f'''"""Tests for {plan.capability_id}."""

from capabilities.base import CapabilityContext
from capabilities.generated.{module}.capability import run


def {test_names[0]}():
    result = run(CapabilityContext(code={supported_example!r}, language={primary_language!r}))
    assert result.success
    assert result.modified_code
    assert result.modified_code != {supported_example!r}
    assert result.findings


def {test_names[1]}():
    result = run(CapabilityContext(code="", language={primary_language!r}))
    assert not result.success


def {test_names[2]}():
    result = run(CapabilityContext(code="some code", language="__unsupported__"))
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
            f"# {plan.capability_id}: {plan.name}\n\n{plan.description}\n\n"
            "Generated by Layer 8 (Evolution) after a capability gap was detected.\n"
        )
        return GeneratedCapabilityFiles(
            capability_code=capability_code,
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
        (module_dir / "metadata.json").write_text(json.dumps(files.metadata, indent=2) + "\n", encoding="utf-8")
        (module_dir / "README.md").write_text(files.readme, encoding="utf-8")
        init_path = self.generated_dir / "__init__.py"
        if not init_path.exists():
            init_path.write_text("", encoding="utf-8")
        return module_dir

    def test_capability(self, capability_id: str, project_root: str = ".") -> TestRunResult:
        module = _module_name(capability_id)
        module_dir = self.generated_dir / module
        tests_path = module_dir / "tests.py"
        if not tests_path.exists():
            raise EvolutionError(f"No generated tests found for {capability_id}: {tests_path}")
        cov_target = f"capabilities.generated.{module}.capability"
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", str(tests_path), "-v", f"--cov={cov_target}", "--cov-report=term-missing"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = completed.stdout + completed.stderr
        return TestRunResult(
            passed=(completed.returncode == 0),
            tests_run=len(re.findall(r"\bPASSED\b|\bFAILED\b", output)),
            tests_failed=len(re.findall(r"\bFAILED\b", output)),
            coverage_percent=self._parse_coverage(output),
            output=output,
        )

    @staticmethod
    def _parse_coverage(output: str) -> Optional[float]:
        match = _COVERAGE_TOTAL_RE.search(output)
        return float(match.group(1)) if match else None

    def register_capability(self, plan: CapabilityPlan, files: GeneratedCapabilityFiles, test_result: TestRunResult, governance_decision_status: Optional[DecisionStatus] = None) -> bool:
        if not test_result.passed or not test_result.meets_coverage_gate or governance_decision_status == DecisionStatus.REJECTED:
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

    def develop_capability_for_gap(self, plan: CapabilityPlan, *, project_root: str = ".", governance_decision_status: Optional[DecisionStatus] = None) -> Dict[str, Any]:
        files = self.generate_capability_code(plan)
        module_dir = self.implement_capability(plan, files)
        test_result = self.test_capability(plan.capability_id, project_root=project_root)
        registered = self.register_capability(plan, files, test_result, governance_decision_status=governance_decision_status)
        return {
            "capability_id": plan.capability_id,
            "module_dir": str(module_dir),
            "implemented": True,
            "test_result": {
                "passed": test_result.passed,
                "tests_run": test_result.tests_run,
                "tests_failed": test_result.tests_failed,
                "coverage_percent": test_result.coverage_percent,
            },
            "registered": registered,
        }

    def build_commit_message(self, plan: CapabilityPlan, test_result: TestRunResult, governance_decision_id: Optional[str] = None) -> str:
        coverage = f"{test_result.coverage_percent:.1f}%" if test_result.coverage_percent is not None else "unmeasured"
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

    def run_evolution_cycle(self, experience_log: ExperienceLog, min_occurrences: int = DEFAULT_MIN_OCCURRENCES, project_root: str = ".") -> Optional[EvolutionRecord]:
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
                affected_files=[str(module_dir / "capability.py"), str(module_dir / "tests.py"), str(module_dir / "metadata.json")],
                related_capabilities=[plan.capability_id],
            )
            governance_decision_id = decision.id
            governance_decision_status = decision.decision
        registered = self.register_capability(plan, files, test_result, governance_decision_status)
        record = EvolutionRecord(
            capability_id=plan.capability_id,
            trigger_pattern=trigger.pattern,
            trigger_task_ids=trigger.trigger_task_ids,
            test_result=test_result,
            governance_decision_id=governance_decision_id,
            registered=registered,
            commit_message=self.build_commit_message(plan, test_result, governance_decision_id),
        )
        self._save_record(record)
        return record

    def _save_record(self, record: EvolutionRecord) -> None:
        self.evaluation_dir.mkdir(parents=True, exist_ok=True)
        path = self.evaluation_dir / f"{record.capability_id}.json"
        path.write_text(json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8")
