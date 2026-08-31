"""Shared capability execution interface.

Every capability (seed or generated) exposes a module-level ``run(context)``
function with this signature:

    def run(context: CapabilityContext) -> CapabilityResult: ...

Keeping the interface this small and uniform is what lets Layer 2
(Cognitive Core) select a capability generically, Layer 6 (Validation) run
any capability in a sandbox the same way, and Layer 9 (Capability Registry)
treat seed and generated capabilities identically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class CapabilityContext:
    """Input passed to a capability's ``run()`` function.

    Attributes:
        code: The source text the capability should operate on.
        file_path: Path (relative to the target project) that ``code`` was
            read from, when applicable.
        language: Target language identifier, e.g. ``"python"``, ``"java"``,
            ``"javascript"``, ``"go"``, ``"csharp"``.
        project_path: Root path of the target project.
        parameters: Capability-specific parameters (e.g. timeout,
            aggressiveness) as adjusted by Layer 5 (Adaptation).
        metadata: Free-form extra context (task id, request text, etc).
    """

    code: str
    language: str
    file_path: str = ""
    project_path: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CapabilityResult:
    """Output of a capability's ``run()`` function.

    Attributes:
        success: Whether the capability completed without error.
        modified_code: The resulting code, if the capability changes code.
            ``None`` when the capability only inspects/reports.
        summary: Short human-readable description of what happened.
        findings: Structured findings (e.g. list of detected issues).
        error: Error message, set only when ``success`` is False.
    """

    success: bool
    modified_code: Optional[str] = None
    summary: str = ""
    findings: list = field(default_factory=list)
    error: Optional[str] = None

    @classmethod
    def ok(
        cls,
        summary: str,
        modified_code: Optional[str] = None,
        findings: Optional[list] = None,
    ) -> "CapabilityResult":
        return cls(
            success=True,
            modified_code=modified_code,
            summary=summary,
            findings=findings or [],
        )

    @classmethod
    def fail(cls, error: str, summary: str = "") -> "CapabilityResult":
        return cls(success=False, summary=summary, error=error)
