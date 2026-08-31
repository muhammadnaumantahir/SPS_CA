"""CAP-006: Unused Variable Removal.

Structure-only seed capability. Within each function, finds simple
``name = <expr>`` assignments whose target is never read again in that
function body, and reports them. Deliberately conservative: it does not
flag tuple/starred assignments, augmented assignments, or names also used
as function parameters, to avoid false positives.
"""

from __future__ import annotations

import ast

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}


def _find_unused_in_function(func: ast.FunctionDef):
    assigned = {}
    used = set()

    for node in ast.walk(func):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                pass
            elif isinstance(node.ctx, ast.Load):
                used.add(node.id)

    for node in ast.walk(func):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and not target.id.startswith("_"):
                assigned[target.id] = node.lineno

    findings = []
    for name, lineno in assigned.items():
        if name not in used:
            findings.append(
                {
                    "line": lineno,
                    "issue": "unused-variable",
                    "detail": f"Variable '{name}' assigned on line {lineno} is never used.",
                }
            )
    return findings


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in _SUPPORTED:
        return CapabilityResult.ok(
            summary=f"CAP-006 has no rule set yet for language '{context.language}'",
        )

    try:
        tree = ast.parse(context.code)
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Could not parse source: {exc}")

    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            findings.extend(_find_unused_in_function(node))

    summary = (
        f"Found {len(findings)} unused variable(s)."
        if findings
        else "No unused variables found by CAP-006's current rule set."
    )
    return CapabilityResult.ok(summary=summary, findings=findings)
