"""Data models exchanged within Layer 2 (Cognitive Core).

These are intentionally plain dataclasses rather than pydantic models: the
Cognitive Core only needs structural clarity for now, and pydantic is
reserved for boundaries that need runtime validation/(de)serialization
(model provider configs, persisted registry/lineage records, etc).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Request:
    """A user request as received by ``CognitiveCore.receive_request``."""

    user_request: str
    code_context: str = ""
    target_project: str = ""
    target_language: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FunctionInfo:
    """A single function/method signature extracted from source."""

    name: str
    start_line: int
    end_line: int
    parameters: List[str] = field(default_factory=list)


@dataclass
class FileAnalysis:
    """Parse result for a single source file."""

    file_path: str
    language: str
    functions: List[FunctionInfo] = field(default_factory=list)
    parse_ok: bool = True
    error: Optional[str] = None


@dataclass
class ProjectAnalysis:
    """Aggregate analysis of a target project (or a single-file context)."""

    project_path: str
    files: List[FileAnalysis] = field(default_factory=list)
    languages_detected: List[str] = field(default_factory=list)

    @property
    def total_functions(self) -> int:
        return sum(len(f.functions) for f in self.files)


@dataclass
class Subtask:
    """One decomposed unit of work toward satisfying a request."""

    id: str
    description: str
    depends_on: List[str] = field(default_factory=list)


@dataclass
class ModificationPlan:
    """A plan for how to satisfy a request using selected capabilities."""

    subtasks: List[Subtask]
    selected_capability_ids: List[str]
    rationale: str = ""
