"""Layer 10 execution engine: apply, monitor, log, and rollback validated changes."""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .models import (
    Change,
    ExecutionRecord,
    ExecutionResult,
    ExecutionStatus,
    FileSnapshot,
    RollbackResult,
    TestOutcome,
)


class ExecutionEngineError(Exception):
    """Raised for invalid or unrecoverable execution-layer operations."""


class ExecutionEngine:
    """Apply validated changes safely to target projects."""

    def __init__(
        self,
        snapshot_dir: str = "data/execution_snapshots",
        log_path: str = "evaluation/execution/execution_log.json",
        test_timeout_s: int = 300,
        registry: Optional[Any] = None,
    ):
        self.snapshot_dir = Path(snapshot_dir)
        self.log_path = Path(log_path)
        self.test_timeout_s = test_timeout_s
        self.registry = registry
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._executions: Dict[str, ExecutionResult] = {}
        self._changes: Dict[str, Change] = {}
        self._snapshots: Dict[str, List[FileSnapshot]] = {}

    def execute_change(self, change: Change, target_project_path: str) -> ExecutionResult:
        """Apply a validated change, test it, and roll it back on failure."""
        start = time.monotonic()
        target_root = Path(target_project_path).resolve()
        if not target_root.exists() or not target_root.is_dir():
            raise ExecutionEngineError(f"Target project path does not exist: {target_project_path}")
        self._validate_edits(change, target_root)
        self._changes[change.change_id] = change
        snapshots = self._snapshot_files(change, target_root)
        self._snapshots[change.change_id] = snapshots

        try:
            self._apply_edits(change, target_root)
            test_outcome = self._run_tests(change, target_root)
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if test_outcome.all_passed:
                self._git_commit_if_repo(target_root, change)
                result = ExecutionResult(
                    change_id=change.change_id,
                    status=ExecutionStatus.SUCCESS,
                    target_project=str(target_root),
                    target_language=change.target_language,
                    tests_passing=test_outcome.tests_passing,
                    tests_failing=test_outcome.tests_failing,
                    execution_time_ms=elapsed_ms,
                )
            else:
                rollback = self.execute_rollback(change.change_id, target_root)
                status = ExecutionStatus.ROLLED_BACK if rollback.success else ExecutionStatus.ROLLBACK_FAILED
                result = ExecutionResult(
                    change_id=change.change_id,
                    status=status,
                    target_project=str(target_root),
                    target_language=change.target_language,
                    tests_passing=test_outcome.tests_passing,
                    tests_failing=test_outcome.tests_failing,
                    execution_time_ms=elapsed_ms,
                    rollback_triggered=True,
                    error_message=(
                        "Tests failed after applying change; rollback executed."
                        if rollback.success
                        else f"Tests failed AND rollback failed: {rollback.error_message}"
                    ),
                )
        except Exception as exc:  # noqa: BLE001
            elapsed_ms = int((time.monotonic() - start) * 1000)
            rollback = self.execute_rollback(change.change_id, target_root)
            result = ExecutionResult(
                change_id=change.change_id,
                status=ExecutionStatus.ROLLED_BACK if rollback.success else ExecutionStatus.ROLLBACK_FAILED,
                target_project=str(target_root),
                target_language=change.target_language,
                execution_time_ms=elapsed_ms,
                rollback_triggered=True,
                error_message=f"Execution error: {exc}",
            )

        self._executions[change.change_id] = result
        self.update_metrics(change, result)
        self._record_registry_usage(change, result)
        return result

    def monitor_execution(self, change_id: str) -> Optional[ExecutionResult]:
        """Re-run the stored test command and roll back if a successful change regressed."""
        result = self._executions.get(change_id) or self._load_result_from_log(change_id)
        if result is None:
            return None
        change = self._changes.get(change_id)
        if change is None or not change.test_command:
            return result
        if result.status not in {ExecutionStatus.SUCCESS, ExecutionStatus.PENDING}:
            return result
        target_root = Path(result.target_project).resolve()
        if not target_root.exists():
            return result

        outcome = self._run_tests(change, target_root)
        if outcome.all_passed:
            return result

        rollback = self.execute_rollback(change_id, target_root)
        monitored = ExecutionResult(
            change_id=change_id,
            status=ExecutionStatus.ROLLED_BACK if rollback.success else ExecutionStatus.ROLLBACK_FAILED,
            target_project=str(target_root),
            target_language=result.target_language,
            tests_passing=outcome.tests_passing,
            tests_failing=outcome.tests_failing,
            execution_time_ms=result.execution_time_ms + outcome.duration_ms,
            rollback_triggered=True,
            error_message=(
                "Regression detected during monitoring; rollback executed."
                if rollback.success
                else f"Regression detected and rollback failed: {rollback.error_message}"
            ),
        )
        self._executions[change_id] = monitored
        self.update_metrics(change, monitored)
        return monitored

    def execute_rollback(
        self, change_id: str, target_project_path: Optional[Path] = None
    ) -> RollbackResult:
        """Restore the pre-change file state and verify content hashes."""
        snapshots = self._snapshots.get(change_id)
        if snapshots is None:
            return RollbackResult(
                change_id=change_id,
                success=False,
                error_message="No snapshot found for this change_id; cannot roll back.",
            )
        target_root = Path(target_project_path or self._target_from_execution(change_id) or ".").resolve()
        restored: List[str] = []
        failed: List[str] = []
        for snap in snapshots:
            file_path = target_root / snap.file_path
            try:
                if snap.existed:
                    backup = Path(snap.backup_path or "")
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")
                elif file_path.exists():
                    file_path.unlink()
                restored.append(snap.file_path)
            except OSError:
                failed.append(snap.file_path)
        verified = self._verify_rollback(snapshots, target_root)
        return RollbackResult(
            change_id=change_id,
            success=not failed and verified,
            files_restored=restored,
            files_failed=failed,
            verified=verified,
            error_message=None if not failed and verified else f"Failed to restore: {failed or 'verification failed'}",
        )

    def update_metrics(self, change: Change, result: ExecutionResult) -> None:
        """Append an execution outcome to the evaluation execution log."""
        record = ExecutionRecord(
            id=f"exec_{uuid.uuid4().hex[:10]}",
            change_id=result.change_id,
            capability_id=change.capability_id,
            target_project=result.target_project,
            target_language=result.target_language,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=result.status.value,
            tests_passing=result.tests_passing,
            tests_failing=result.tests_failing,
            execution_time_ms=result.execution_time_ms,
            rollback_triggered=result.rollback_triggered,
            error_message=result.error_message,
        )
        log = self._load_log()
        log.setdefault("executions", []).append(record.to_dict())
        self._save_log(log)

    def get_success_ratio(self, capability_id: Optional[str] = None) -> float:
        executions = self._load_log().get("executions", [])
        if capability_id:
            executions = [e for e in executions if e.get("capability_id") == capability_id]
        if not executions:
            return 0.0
        successes = sum(1 for e in executions if e.get("status") == ExecutionStatus.SUCCESS.value)
        return successes / len(executions)

    def _record_registry_usage(self, change: Change, result: ExecutionResult) -> None:
        if self.registry is None:
            return
        try:
            self.registry.record_usage(
                change.capability_id,
                success=result.status == ExecutionStatus.SUCCESS,
                execution_time_ms=result.execution_time_ms,
                notes=result.error_message or "Execution completed successfully.",
            )
        except Exception:
            # Registry persistence must not alter the already-determined execution result.
            pass

    @staticmethod
    def _validate_edits(change: Change, target_root: Path) -> None:
        for edit in change.edits:
            path = Path(edit.file_path)
            if path.is_absolute() or ".." in path.parts:
                raise ExecutionEngineError(f"Unsafe edit path: {edit.file_path}")
            resolved = (target_root / path).resolve()
            if not resolved.is_relative_to(target_root):
                raise ExecutionEngineError(f"Edit escapes target project: {edit.file_path}")

    def _snapshot_files(self, change: Change, target_root: Path) -> List[FileSnapshot]:
        snapshots: List[FileSnapshot] = []
        backup_dir = self.snapshot_dir / change.change_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        for i, edit in enumerate(change.edits):
            file_path = target_root / edit.file_path
            if file_path.exists():
                original = file_path.read_text(encoding="utf-8")
                backup_path = backup_dir / f"{i}_{file_path.name}.bak"
                backup_path.write_text(original, encoding="utf-8")
                edit.original_content = original
                edit.existed_before = True
                snapshots.append(
                    FileSnapshot(edit.file_path, True, FileSnapshot.hash_content(original), str(backup_path))
                )
            else:
                edit.existed_before = False
                edit.original_content = None
                snapshots.append(FileSnapshot(edit.file_path, False, None, None))
        return snapshots

    @staticmethod
    def _apply_edits(change: Change, target_root: Path) -> None:
        for edit in change.edits:
            file_path = target_root / edit.file_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(edit.new_content, encoding="utf-8")

    def _run_tests(self, change: Change, target_root: Path) -> TestOutcome:
        if not change.test_command:
            return TestOutcome()
        start = time.monotonic()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        try:
            proc = subprocess.run(
                change.test_command,
                cwd=str(target_root),
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.test_timeout_s,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return TestOutcome(
                tests_failing=1,
                return_code=-1,
                duration_ms=int((time.monotonic() - start) * 1000),
                raw_output="Test command timed out.",
            )
        output = proc.stdout + proc.stderr
        passing, failing = self._parse_pytest_summary(output)
        return TestOutcome(
            tests_passing=passing,
            tests_failing=failing if failing or proc.returncode == 0 else 1,
            return_code=proc.returncode,
            duration_ms=int((time.monotonic() - start) * 1000),
            raw_output=output[-4000:],
        )

    @staticmethod
    def _parse_pytest_summary(output: str) -> Tuple[int, int]:
        passed = re.search(r"(\d+)\s+passed", output)
        failed = re.search(r"(\d+)\s+failed", output)
        errors = re.search(r"(\d+)\s+error", output)
        return (
            int(passed.group(1)) if passed else 0,
            (int(failed.group(1)) if failed else 0) + (int(errors.group(1)) if errors else 0),
        )

    def _verify_rollback(self, snapshots: List[FileSnapshot], target_root: Path) -> bool:
        for snap in snapshots:
            file_path = target_root / snap.file_path
            if snap.existed:
                if not file_path.exists():
                    return False
                if FileSnapshot.hash_content(file_path.read_text(encoding="utf-8")) != snap.content_hash:
                    return False
            elif file_path.exists():
                return False
        return True

    def _git_commit_if_repo(self, target_root: Path, change: Change) -> None:
        if not (target_root / ".git").exists():
            return
        try:
            paths = [edit.file_path for edit in change.edits]
            subprocess.run(
                ["git", "add", "--", *paths],
                cwd=str(target_root),
                capture_output=True,
                timeout=30,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", f"SPS-CA: apply {change.change_id} ({change.capability_id})"],
                cwd=str(target_root),
                capture_output=True,
                timeout=30,
                check=False,
            )
        except (subprocess.SubprocessError, OSError):
            pass

    def _target_from_execution(self, change_id: str) -> Optional[str]:
        result = self._executions.get(change_id) or self._load_result_from_log(change_id)
        return result.target_project if result else None

    def _load_log(self) -> Dict[str, Any]:
        if self.log_path.exists():
            try:
                data = json.loads(self.log_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass
        return {"executions": []}

    def _save_log(self, log: Dict[str, Any]) -> None:
        tmp = self.log_path.with_suffix(self.log_path.suffix + ".tmp")
        tmp.write_text(json.dumps(log, indent=2), encoding="utf-8")
        tmp.replace(self.log_path)

    def _load_result_from_log(self, change_id: str) -> Optional[ExecutionResult]:
        for entry in reversed(self._load_log().get("executions", [])):
            if entry.get("change_id") == change_id:
                try:
                    status = ExecutionStatus(entry["status"])
                except (KeyError, ValueError):
                    return None
                return ExecutionResult(
                    change_id=change_id,
                    status=status,
                    target_project=entry["target_project"],
                    target_language=entry["target_language"],
                    tests_passing=entry.get("tests_passing", 0),
                    tests_failing=entry.get("tests_failing", 0),
                    execution_time_ms=entry.get("execution_time_ms", 0),
                    rollback_triggered=entry.get("rollback_triggered", False),
                    error_message=entry.get("error_message"),
                )
        return None
