"""CAP-004: Loop Optimization.

Detects simple list-building loops and rewrites only the narrow
semantics-preserving identity-append form. Other append expressions remain
findings-only so the capability can still surface optimization candidates
without making unsafe transformations.
"""

from __future__ import annotations

import ast

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}


def _append_loop(node: ast.For):
    if len(node.body) != 1 or not isinstance(node.body[0], ast.Expr):
        return None
    call = node.body[0].value
    if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
        return None
    if call.func.attr != "append" or len(call.args) != 1 or call.keywords:
        return None
    if not isinstance(call.func.value, ast.Name) or not isinstance(node.target, ast.Name):
        return None
    return call.func.value.id, ast.unparse(node.target), ast.unparse(call.args[0]), ast.unparse(node.iter)


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in _SUPPORTED:
        return CapabilityResult.ok(summary=f"CAP-004 has no rule set yet for language '{context.language}'")
    try:
        tree = ast.parse(context.code)
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Could not parse source: {exc}")

    findings = []
    replacements = []
    lines = context.code.splitlines()
    for node in ast.walk(tree):
        if not isinstance(node, ast.For):
            continue
        pattern = _append_loop(node)
        if not pattern:
            continue
        target_list, target, appended_expr, iterator = pattern
        identity = appended_expr == target
        findings.append({
            "line": node.lineno,
            "issue": "append-loop-to-comprehension",
            "detail": f"Loop appending to '{target_list}' can be reviewed for list-comprehension optimization.",
            "safe_to_apply": identity,
        })
        if identity and context.parameters.get("apply", False):
            indent = lines[node.lineno - 1][: len(lines[node.lineno - 1]) - len(lines[node.lineno - 1].lstrip())]
            replacements.append((node.lineno - 1, getattr(node, "end_lineno", node.lineno), f"{indent}{target_list} = [{target} for {target} in {iterator}]"))

    if not findings:
        return CapabilityResult.ok(summary="No append-loop optimization candidates found.")
    if not context.parameters.get("apply", False):
        return CapabilityResult.ok(summary=f"Found {len(findings)} append-loop optimization candidate(s).", findings=findings)
    if not replacements:
        return CapabilityResult.ok(summary="Candidates found, but none satisfy the safe identity-append rule.", findings=findings)

    updated = list(lines)
    for start, end, replacement in reversed(replacements):
        updated[start:end] = [replacement]
    modified = "\n".join(updated) + ("\n" if context.code.endswith("\n") else "")
    return CapabilityResult.ok(
        summary=f"Applied {len(replacements)} safe loop optimization(s).",
        modified_code=modified,
        findings=findings,
    )
