"""Phase 1: controlled self-programming and self-repair.

This module keeps the canonical ten SPS layers intact while adding the missing
closed-loop mechanism inside Layer 8 (Evolution): diagnose a system failure,
construct a bounded repair candidate, run the candidate through Software DNA
and Governance, execute it in the controlled Layer 10 environment, and record
regression evidence. A failed candidate is rolled back by the Execution layer.

The engine is deliberately conservative: it can never target Software DNA,
Governance, audit history, or runtime state for autonomous repair. Human review
is required whenever Governance does not auto-approve a mutation.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from layers.layer_01_software_dna import DNAViolation as Layer1DNAViolation, SoftwareDNA
from layers.layer_02_governance import ChangeType, DecisionStatus, GovernanceGate
from layers.layer_03_cognitive.llm_interface import LLMInterface, LLMQueryError
from layers.layer_10_execution import Change, ExecutionEngine, FileEdit, ExecutionStatus


@dataclass(frozen=True)
class FailureDiagnosis:
    """Structured diagnosis produced before a self-repair candidate is built."""

    failure_id: str
    category: str
    component: str
    symptom: str
    root_cause_hypothesis: str
    severity: str
    affected_files: List[str] = field(default_factory=list)


@dataclass
class SelfRepairResult:
    """Auditable outcome of one controlled self-repair attempt."""

    success: bool
    diagnosis: Optional[FailureDiagnosis] = None
    decision: Optional[str] = None
    change_id: Optional[str] = None
    execution_status: Optional[str] = None
    rollback_triggered: bool = False
    regression_case_id: Optional[str] = None
    message: str = ""
    repair_attempts: int = 0
    candidate: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "diagnosis": self.diagnosis.__dict__ if self.diagnosis else None,
            "decision": self.decision,
            "change_id": self.change_id,
            "execution_status": self.execution_status,
            "rollback_triggered": self.rollback_triggered,
            "regression_case_id": self.regression_case_id,
            "message": self.message,
            "repair_attempts": self.repair_attempts,
            "candidate": self.candidate,
        }


class SelfProgrammingError(Exception):
    """Raised when a self-programming request is invalid or unsafe."""


class SelfProgrammingEngine:
    """Layer-8 controlled self-modification engine.

    The engine is designed for failures in SPS-CA itself, not arbitrary user
    projects. It does not bypass the other layers: Software DNA is evaluated
    first, Governance decides whether a mutation may proceed, Layer 10 owns
    snapshot/execute/rollback, and regression evidence is retained for future
    evaluation.
    """

    MAX_REPAIR_ATTEMPTS = 3
    MAX_FILES_PER_REPAIR = 5
    PROTECTED_PREFIXES = (
        "governance/",
        "layers/layer_01_software_dna/",
        "layers/layer_02_governance/",
        "experience/logs/",
        "experience/traces/",
        "runtime/",
    )
    ALLOWED_TEXT_SUFFIXES = (
        ".py", ".md", ".json", ".txt", ".yml", ".yaml", ".toml", ".ini", ".css", ".js", ".ts"
    )

    def __init__(
        self,
        *,
        repo_root: str | Path = ".",
        dna: Optional[SoftwareDNA] = None,
        governance: Optional[GovernanceGate] = None,
        llm: Optional[LLMInterface] = None,
        execution: Optional[ExecutionEngine] = None,
        regression_path: str | Path = "experience/regressions/self_programming_regressions.json",
        max_repair_attempts: int = MAX_REPAIR_ATTEMPTS,
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.dna = dna or SoftwareDNA()
        self.governance = governance or GovernanceGate()
        self.llm = llm or LLMInterface(timeout_seconds=120.0)
        self.execution = execution or ExecutionEngine(
            snapshot_dir=str(self.repo_root / "data" / "self_programming_snapshots"),
            log_path=str(self.repo_root / "evaluation" / "execution" / "self_programming_execution.json"),
        )
        self.regression_path = self.repo_root / regression_path
        self.max_repair_attempts = max(1, min(int(max_repair_attempts), self.MAX_REPAIR_ATTEMPTS))

    def diagnose_failure(
        self,
        *,
        symptom: str,
        component: str = "unknown",
        affected_files: Optional[List[str]] = None,
        failure_id: Optional[str] = None,
    ) -> FailureDiagnosis:
        """Classify a failure before any mutation candidate is generated."""
        text = f"{component} {symptom}".lower()
        if any(token in text for token in ("routing", "intent", "test_generation", "capability selection")):
            category, severity = "ROUTING_FAILURE", "high"
        elif any(token in text for token in ("trace", "logging", "audit")):
            category, severity = "TRACE_FAILURE", "medium"
        elif any(token in text for token in ("provider", "ollama", "llm", "model")):
            category, severity = "MODEL_FAILURE", "medium"
        elif any(token in text for token in ("governance", "approval", "dna")):
            category, severity = "GOVERNANCE_FAILURE", "critical"
        elif any(token in text for token in ("validation", "validator", "test")):
            category, severity = "VALIDATION_FAILURE", "high"
        elif any(token in text for token in ("execution", "rollback", "sandbox")):
            category, severity = "EXECUTION_FAILURE", "high"
        elif any(token in text for token in ("session", "state", "conversation")):
            category, severity = "STATE_FAILURE", "medium"
        else:
            category, severity = "CORE_DEFECT", "high"

        hypothesis = (
            f"Observed symptom is associated with {category.lower()} in {component}; "
            "repair should change the smallest responsible component and preserve layer boundaries."
        )
        return FailureDiagnosis(
            failure_id=failure_id or f"FAIL-{uuid.uuid4().hex[:10]}",
            category=category,
            component=component,
            symptom=symptom.strip(),
            root_cause_hypothesis=hypothesis,
            severity=severity,
            affected_files=list(affected_files or []),
        )

    def repair_from_failure(
        self,
        *,
        symptom: str,
        component: str = "unknown",
        affected_files: Optional[List[str]] = None,
        tests: Optional[List[str]] = None,
        failure_id: Optional[str] = None,
    ) -> SelfRepairResult:
        """Run diagnose -> candidate -> DNA -> governance -> execute -> verify.

        The method performs at most ``max_repair_attempts`` candidates. Every
        candidate is fully rejected if it targets a protected surface, violates
        a hard DNA rule, exceeds scope, or fails Layer-10 verification.
        """
        diagnosis = self.diagnose_failure(
            symptom=symptom,
            component=component,
            affected_files=affected_files,
            failure_id=failure_id,
        )
        regression_case_id = self.record_regression_case(diagnosis, tests or [])
        last_message = "No repair candidate was accepted."

        for attempt in range(1, self.max_repair_attempts + 1):
            try:
                candidate = self._generate_candidate(diagnosis, attempt, tests or [])
                edits = self._validate_candidate(diagnosis, candidate)
            except (SelfProgrammingError, LLMQueryError, ValueError, SyntaxError) as exc:
                last_message = f"Candidate {attempt} rejected before execution: {exc}"
                continue

            change = Change.new(
                capability_id="SELF-REPAIR",
                description=(
                    f"Controlled self-repair for {diagnosis.failure_id}: "
                    f"{diagnosis.symptom}"
                ),
                edits=[FileEdit(file_path=path, new_content=content) for path, content in edits],
                target_language="python",
                test_command=self._test_command(tests),
            )

            dna_decision = self._check_dna(change)
            if not dna_decision[1]:
                last_message = f"Candidate {attempt} rejected by Software DNA: {dna_decision[0]}"
                continue

            governance_decision = self.governance.make_decision(
                change_id=change.change_id,
                change_type=ChangeType.ADAPTATION,
                change_description=change.description,
                affected_files=[edit.file_path for edit in change.edits],
                related_capabilities=["SELF-REPAIR"],
            )
            if governance_decision.decision not in {DecisionStatus.AUTO_APPROVED, DecisionStatus.APPROVED}:
                last_message = (
                    f"Candidate {attempt} requires human governance review: "
                    f"{governance_decision.rationale}"
                )
                return SelfRepairResult(
                    success=False,
                    diagnosis=diagnosis,
                    decision=governance_decision.decision.value,
                    regression_case_id=regression_case_id,
                    message=last_message,
                    repair_attempts=attempt,
                    candidate=candidate,
                )

            execution = self.execution.execute_change(change, str(self.repo_root))
            self._append_regression_result(regression_case_id, execution, attempt)
            if execution.status == ExecutionStatus.SUCCESS:
                return SelfRepairResult(
                    success=True,
                    diagnosis=diagnosis,
                    decision=governance_decision.decision.value,
                    change_id=change.change_id,
                    execution_status=execution.status.value,
                    rollback_triggered=False,
                    regression_case_id=regression_case_id,
                    message="Self-repair candidate passed controlled execution and regression verification.",
                    repair_attempts=attempt,
                    candidate=candidate,
                )

            last_message = execution.error_message or f"Execution returned {execution.status.value}."
            if execution.status == ExecutionStatus.ROLLBACK_FAILED:
                break

        return SelfRepairResult(
            success=False,
            diagnosis=diagnosis,
            decision="rejected",
            execution_status=ExecutionStatus.ROLLED_BACK.value if "rollback" in last_message.lower() else None,
            rollback_triggered="rollback" in last_message.lower(),
            regression_case_id=regression_case_id,
            message=last_message,
            repair_attempts=self.max_repair_attempts,
        )

    def record_regression_case(self, diagnosis: FailureDiagnosis, tests: List[str]) -> str:
        """Persist a reproducible regression record without storing source text."""
        case_id = f"REG-{uuid.uuid4().hex[:10]}"
        data = self._load_regressions()
        data.append({
            "case_id": case_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "failure_id": diagnosis.failure_id,
            "category": diagnosis.category,
            "component": diagnosis.component,
            "symptom": diagnosis.symptom,
            "root_cause_hypothesis": diagnosis.root_cause_hypothesis,
            "affected_files": list(diagnosis.affected_files),
            "tests": list(tests),
            "status": "open",
            "attempts": [],
        })
        self._save_regressions(data)
        return case_id

    def _generate_candidate(self, diagnosis: FailureDiagnosis, attempt: int, tests: List[str]) -> Dict[str, Any]:
        context_files = self._read_context(diagnosis.affected_files)
        prompt = f"""Produce one minimal SPS-CA self-repair candidate.

Failure ID: {diagnosis.failure_id}
Category: {diagnosis.category}
Component: {diagnosis.component}
Symptom: {diagnosis.symptom}
Hypothesis: {diagnosis.root_cause_hypothesis}
Attempt: {attempt}
Regression tests: {tests}

Rules:
- Return ONLY JSON.
- JSON shape: {{"summary": str, "test_command": str, "edits": [{{"file_path": str, "new_content": str}}]}}
- The edit must be the smallest change that fixes the diagnosed defect.
- Do not modify Software DNA, Governance, audit/traces, runtime state, secrets, or credentials.
- Maximum {self.MAX_FILES_PER_REPAIR} edited files.
- Keep the existing ten SPS layer names and boundaries unchanged.
- Preserve existing public APIs unless the failure requires a compatible fix.
- Include complete new file contents, not patches or Markdown fences.

Context:
{context_files}
"""
        raw = self.llm.query(code="", instruction=prompt, model="", temperature=0.0)
        text = str(raw or "").strip()
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("LLM did not return a JSON repair candidate")
        candidate = json.loads(match.group(0))
        if not isinstance(candidate, dict) or not isinstance(candidate.get("edits"), list):
            raise ValueError("invalid repair candidate shape")
        return candidate

    def _validate_candidate(self, diagnosis: FailureDiagnosis, candidate: Dict[str, Any]) -> List[tuple[str, str]]:
        raw_edits = candidate.get("edits") or []
        if not raw_edits or len(raw_edits) > self.MAX_FILES_PER_REPAIR:
            raise SelfProgrammingError(f"repair must contain 1..{self.MAX_FILES_PER_REPAIR} edits")

        allowed = set(diagnosis.affected_files)
        edits: List[tuple[str, str]] = []
        for item in raw_edits:
            if not isinstance(item, dict):
                raise SelfProgrammingError("repair edit must be an object")
            path = str(item.get("file_path", "")).replace("\\", "/").lstrip("./")
            content = str(item.get("new_content", ""))
            if not path or not content:
                raise SelfProgrammingError("repair edit requires file_path and new_content")
            if ".." in Path(path).parts or Path(path).is_absolute():
                raise SelfProgrammingError(f"unsafe repair path: {path}")
            if path in self.PROTECTED_PREFIXES or any(path.startswith(prefix) for prefix in self.PROTECTED_PREFIXES):
                raise SelfProgrammingError(f"protected self-programming surface: {path}")
            if not path.endswith(self.ALLOWED_TEXT_SUFFIXES):
                raise SelfProgrammingError(f"unsupported repair file type: {path}")
            if allowed and path not in allowed:
                raise SelfProgrammingError(f"candidate changed an unapproved file: {path}")
            resolved = (self.repo_root / path).resolve()
            if not resolved.is_relative_to(self.repo_root):
                raise SelfProgrammingError(f"repair escapes repository: {path}")
            if path.endswith(".py"):
                compile(content, path, "exec")
            if path == "README.md" and "Software DNA" not in content:
                raise SelfProgrammingError("README repair must preserve the documented ten-layer model")
            edits.append((path, content))
        return edits

    def _check_dna(self, change: Change) -> tuple[str, bool]:
        hard = False
        warnings: List[str] = []
        for edit in change.edits:
            path = edit.file_path
            if self.dna.is_self_modification_of_governance(path):
                return (f"protected governance/DNA target: {path}", False)
        try:
            result = self.dna.check_action(
                action_description=change.description,
                matched_rule_ids=["rule_007"],
            )
        except Layer1DNAViolation as exc:
            return (str(exc), False)
        hard = result.allowed
        warnings.extend(result.warnings)
        return ("; ".join(warnings) if warnings else "DNA check passed", hard)

    @staticmethod
    def _test_command(tests: Optional[List[str]]) -> str:
        commands = [str(item).strip() for item in (tests or []) if str(item).strip()]
        return commands[0] if commands else "python -m pytest -q"

    def _read_context(self, paths: List[str]) -> str:
        if not paths:
            return "No explicit file list supplied; candidate generation must stop rather than guess a target."
        parts = []
        for relative in paths[:self.MAX_FILES_PER_REPAIR]:
            normalized = relative.replace("\\", "/").lstrip("./")
            if normalized.startswith(self.PROTECTED_PREFIXES):
                continue
            path = self.repo_root / normalized
            if path.is_file() and path.suffix in self.ALLOWED_TEXT_SUFFIXES:
                text = path.read_text(encoding="utf-8")
                parts.append(f"FILE: {normalized}\n{text[-12000:]}")
        return "\n\n".join(parts)

    def _load_regressions(self) -> List[Dict[str, Any]]:
        if not self.regression_path.exists():
            return []
        try:
            value = json.loads(self.regression_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return value if isinstance(value, list) else []

    def _save_regressions(self, records: List[Dict[str, Any]]) -> None:
        self.regression_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.regression_path.with_suffix(self.regression_path.suffix + ".tmp")
        tmp.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(self.regression_path)

    def _append_regression_result(self, case_id: str, execution: Any, attempt: int) -> None:
        records = self._load_regressions()
        for record in records:
            if record.get("case_id") == case_id:
                record.setdefault("attempts", []).append({
                    "attempt": attempt,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "change_id": execution.change_id,
                    "status": execution.status.value,
                    "tests_passing": execution.tests_passing,
                    "tests_failing": execution.tests_failing,
                    "rollback_triggered": execution.rollback_triggered,
                    "error_message": execution.error_message,
                })
                if execution.status == ExecutionStatus.SUCCESS:
                    record["status"] = "resolved"
                elif execution.status == ExecutionStatus.ROLLBACK_FAILED:
                    record["status"] = "blocked"
                break
        self._save_regressions(records)
