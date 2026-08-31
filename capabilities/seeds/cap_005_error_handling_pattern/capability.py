"""CAP-005: Error Handling Pattern.

Structure-only seed capability. Flags calls to a small set of commonly
risky builtins/functions (``open``, ``int``, ``json.loads``) that are not
wrapped in any ``try`` block within the enclosing function, as candidates
for added error handling.
"""

from __future__ import annotations

import ast

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}
_RISKY_CALLS = {"open", "int", "float", "loads"}


class _TryRangeCollector(ast.NodeVisitor):
    def __init__(self):
        self.ranges = []

    def visit_Try(self, node: ast.Try):
        start = node.lineno
        end = getattr(node, "end_lineno", None) or node.lineno
        self.ranges.append((start, end))
        self.generic_visit(node)


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in _SUPPORTED:
        return CapabilityResult.ok(
            summary=f"CAP-005 has no rule set yet for language '{context.language}'",
        )

    try:
        tree = ast.parse(context.code)
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Could not parse source: {exc}")

    collector = _TryRangeCollector()
    collector.visit(tree)

    def covered(lineno: int) -> bool:
        return any(start <= lineno <= end for start, end in collector.ranges)

    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn_name = None
            if isinstance(node.func, ast.Name):
                fn_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                fn_name = node.func.attr
            if fn_name in _RISKY_CALLS and not covered(node.lineno):
                findings.append(
                    {
                        "line": node.lineno,
                        "issue": "unhandled-risky-call",
                        "detail": f"Call to '{fn_name}(...)' on line {node.lineno} "
                        "is not wrapped in error handling.",
                    }
                )

    summary = (
        f"Found {len(findings)} unhandled risky call(s)."
        if findings
        else "No unhandled risky calls found by CAP-005's current rule set."
    )
    return CapabilityResult.ok(summary=summary, findings=findings)
