"""CAP-001: Simple Bug Detection.

Structure-only seed capability (per Phase 1 scope). Implements real,
minimal detection logic for Python using the standard library ``ast``
module so that Layer 2/6 integration tests have something genuine to
exercise. Non-Python languages return a not-yet-implemented result rather
than raising, so capability selection/execution flow can still be tested
end-to-end before Phase 1's tree-sitter-based analysis is extended to
per-language rule sets in a later phase.
"""

from __future__ import annotations

import ast

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in _SUPPORTED:
        return CapabilityResult.ok(
            summary=f"CAP-001 has no rule set yet for language '{context.language}'",
        )

    try:
        tree = ast.parse(context.code)
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Could not parse source: {exc}")

    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append(
                {
                    "line": node.lineno,
                    "issue": "bare-except",
                    "detail": "Bare 'except:' catches all exceptions including "
                    "KeyboardInterrupt/SystemExit; prefer 'except Exception:'.",
                }
            )
        if isinstance(node, ast.FunctionDef):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    findings.append(
                        {
                            "line": node.lineno,
                            "issue": "mutable-default-argument",
                            "detail": f"Function '{node.name}' uses a mutable "
                            "default argument, which is shared across calls.",
                        }
                    )
        if isinstance(node, ast.Compare):
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and (
                    isinstance(comparator, ast.Constant) and comparator.value is None
                ):
                    findings.append(
                        {
                            "line": node.lineno,
                            "issue": "equality-with-none",
                            "detail": "Use 'is None' / 'is not None' instead of "
                            "'==' / '!=' when comparing to None.",
                        }
                    )

    summary = (
        f"Found {len(findings)} potential issue(s)."
        if findings
        else "No issues found by CAP-001's current rule set."
    )
    return CapabilityResult.ok(summary=summary, findings=findings)
