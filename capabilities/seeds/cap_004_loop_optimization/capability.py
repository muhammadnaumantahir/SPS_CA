"""CAP-004: Loop Optimization.

Structure-only seed capability. Detects the single most common
mechanically-rewritable loop pattern in Python -- building a list by
repeated ``.append()`` inside a ``for`` loop with no other side effects --
and reports it as a candidate for a list-comprehension rewrite. Reports
findings only; it does not rewrite the code, since correctness of the
rewrite depends on whether the loop body truly has no side effects, which
this seed capability does not attempt to prove.
"""

from __future__ import annotations

import ast

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}


def _is_simple_append_loop(node: ast.For):
    if len(node.body) != 1:
        return None
    stmt = node.body[0]
    if not isinstance(stmt, ast.Expr):
        return None
    call = stmt.value
    if not isinstance(call, ast.Call):
        return None
    if not isinstance(call.func, ast.Attribute) or call.func.attr != "append":
        return None
    if not isinstance(call.func.value, ast.Name):
        return None
    return call.func.value.id


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in _SUPPORTED:
        return CapabilityResult.ok(
            summary=f"CAP-004 has no rule set yet for language '{context.language}'",
        )

    try:
        tree = ast.parse(context.code)
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Could not parse source: {exc}")

    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            target_list = _is_simple_append_loop(node)
            if target_list:
                findings.append(
                    {
                        "line": node.lineno,
                        "issue": "append-loop-to-comprehension",
                        "detail": f"Loop appending to '{target_list}' could likely "
                        "be rewritten as a list comprehension.",
                    }
                )

    summary = (
        f"Found {len(findings)} loop(s) that could be simplified."
        if findings
        else "No simplifiable loops found by CAP-004's current rule set."
    )
    return CapabilityResult.ok(summary=summary, findings=findings)
