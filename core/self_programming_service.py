"""Application-facing facade for SPS-CA self-programming.

The facade intentionally lives outside the ten SPS layers. The actual
self-programming lifecycle remains owned by Layer 08 (Evolution), with Layer
01 Software DNA, Layer 02 Governance, Layer 09 Verification & Validation and
Layer 10 Execution acting as mandatory boundaries.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from layers.layer_08_evolution import SelfProgrammingEngine, SelfRepairResult


class SelfProgrammingService:
    """Expose controlled SPS-CA self-repair to application/CLI callers."""

    def __init__(self, repo_root: str | Path = ".", **engine_kwargs: Any) -> None:
        self.engine = SelfProgrammingEngine(repo_root=repo_root, **engine_kwargs)

    def repair(
        self,
        *,
        symptom: str,
        component: str,
        affected_files: List[str],
        tests: Optional[List[str]] = None,
        failure_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Diagnose and attempt a governed self-repair; return an audit-ready dict."""
        if not symptom.strip():
            raise ValueError("symptom is required")
        if not affected_files:
            raise ValueError("affected_files is required so the repair scope cannot be guessed")
        result: SelfRepairResult = self.engine.repair_from_failure(
            symptom=symptom,
            component=component,
            affected_files=affected_files,
            tests=tests,
            failure_id=failure_id,
        )
        return result.to_dict()
