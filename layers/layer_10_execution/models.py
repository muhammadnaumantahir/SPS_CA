"""Layer 10 execution data models."""
from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    ROLLBACK_FAILED = "rollback_failed"
    PENDING = "pending"


@dataclass
class FileEdit:
    file_path: str
    new_content: str
    original_content: Optional[str] = None
    existed_before: bool = True


@dataclass
class Change:
    change_id: str
    capability_id: str
    description: str
    edits: List[FileEdit] = field(default_factory=list)
    target_language: str = "python"
    test_command: Optional[str] = None
    created_at: float = field(default_factory=time.time)

    @staticmethod
    def new(capability_id: str, description: str, edits: List[FileEdit],
            target_language: str = "python", test_command: Optional[str] = None) -> "Change":
        return Change(
            change_id=f"change_{uuid.uuid4().hex[:10]}",
            capability_id=capability_id,
            description=description,
            edits=edits,
            target_language=target_language,
            test_command=test_command,
        )


@dataclass
class FileSnapshot:
    file_path: str
    existed: bool
    content_hash: Optional[str]
    backup_path: Optional[str]

    @staticmethod
    def hash_content(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


@dataclass
class TestOutcome:
    tests_passing: int = 0
    tests_failing: int = 0
    return_code: int = 0
    duration_ms: int = 0
    raw_output: str = ""

    @property
    def all_passed(self) -> bool:
        return self.return_code == 0 and self.tests_failing == 0


@dataclass
class ExecutionResult:
    change_id: str
    status: ExecutionStatus
    target_project: str
    target_language: str
    tests_passing: int = 0
    tests_failing: int = 0
    execution_time_ms: int = 0
    rollback_triggered: bool = False
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass
class RollbackResult:
    change_id: str
    success: bool
    files_restored: List[str] = field(default_factory=list)
    files_failed: List[str] = field(default_factory=list)
    verified: bool = False
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ExecutionRecord:
    id: str
    change_id: str
    capability_id: str
    target_project: str
    target_language: str
    timestamp: str
    status: str
    tests_passing: int
    tests_failing: int
    execution_time_ms: int
    rollback_triggered: bool
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)
