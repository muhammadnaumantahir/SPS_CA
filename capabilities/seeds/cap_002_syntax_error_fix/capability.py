"""CAP-002: Syntax Error Fix.

Structure-only seed capability. Handles a very small set of common,
mechanically-fixable Python syntax mistakes (missing colon on a block
header) as a proof of the capability interface; anything beyond that rule
set is reported as unfixed rather than guessed at, since silently
"fixing" code the capability doesn't understand would violate the
project's safety-first design intent.
"""

from __future__ import annotations

import ast
import re

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}
_BLOCK_HEADER_RE = re.compile(
    r"^(\s*)(if|elif|else|for|while|def|class|try|except|finally|with)\b(.*[^:\s])\s*$"
)


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in _SUPPORTED:
        return CapabilityResult.ok(
            summary=f"CAP-002 has no rule set yet for language '{context.language}'",
        )

    try:
        ast.parse(context.code)
        return CapabilityResult.ok(summary="No syntax errors detected.")
    except SyntaxError as exc:
        error = exc

    lines = context.code.splitlines()
    fixed_lines = list(lines)
    findings = []

    if error.lineno and 1 <= error.lineno <= len(lines):
        line = lines[error.lineno - 1]
        match = _BLOCK_HEADER_RE.match(line)
        if match:
            fixed_lines[error.lineno - 1] = line.rstrip() + ":"
            findings.append(
                {
                    "line": error.lineno,
                    "issue": "missing-colon",
                    "detail": f"Added missing ':' at end of block header on line {error.lineno}.",
                }
            )

    if not findings:
        return CapabilityResult.fail(
            error=f"SyntaxError not recognized by CAP-002's rule set: {error}",
            summary="Could not automatically fix this syntax error.",
        )

    candidate = "\n".join(fixed_lines)
    try:
        ast.parse(candidate)
    except SyntaxError as still_broken:
        return CapabilityResult.fail(
            error=f"Proposed fix did not resolve the syntax error: {still_broken}",
        )

    return CapabilityResult.ok(
        summary=f"Fixed {len(findings)} syntax issue(s).",
        modified_code=candidate,
        findings=findings,
    )
