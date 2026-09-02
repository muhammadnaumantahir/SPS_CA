"""CAP-006: Unused Variable Removal.

Finds unused assignments inside functions and can remove assignments whose
right-hand side is a literal-only expression. Calls with potential side
 effects are reported but never removed automatically.
"""

from __future__ import annotations

import ast

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}


def _literal_only(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return all(_literal_only(item) for item in node.elts)
    if isinstance(node, ast.Dict):
        return all((key is None or _literal_only(key)) and _literal_only(value) for key, value in zip(node.keys, node.values))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub, ast.Not)):
        return _literal_only(node.operand)
    return False


def _find_unused_in_function(func: ast.FunctionDef | ast.AsyncFunctionDef):
    used = {
        node.id
        for node in ast.walk(func)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    findings = []
    for node in ast.walk(func):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id.startswith("_") or target.id in used:
            continue
        findings.append({
            "line": node.lineno,
            "issue": "unused-variable",
            "detail": f"Variable '{target.id}' assigned on line {node.lineno} is never used.",
            "safe_to_remove": _literal_only(node.value),
        })
    return findings


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in _SUPPORTED:
        return CapabilityResult.ok(summary=f"CAP-006 has no rule set yet for language '{context.language}'")
    try:
        tree = ast.parse(context.code)
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Could not parse source: {exc}")

    findings = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            findings.extend(_find_unused_in_function(node))

    if not findings:
        return CapabilityResult.ok(summary="No unused variables found by CAP-006's current rule set.")
    if not context.parameters.get("apply", False):
        return CapabilityResult.ok(summary=f"Found {len(findings)} unused variable(s).", findings=findings)

    safe_lines = {item["line"] for item in findings if item["safe_to_remove"]}
    if not safe_lines:
        return CapabilityResult.ok(summary="Unused variables found, but none are safe to remove automatically.", findings=findings)

    lines = context.code.splitlines()
    updated = [line for index, line in enumerate(lines, start=1) if index not in safe_lines]
    modified = "\n".join(updated) + ("\n" if context.code.endswith("\n") else "")
    return CapabilityResult.ok(
        summary=f"Removed {len(safe_lines)} literal-only unused assignment(s).",
        modified_code=modified,
        findings=findings,
    )
