"""CAP-008: Documentation Generation.

Structure-only seed capability. Finds functions and classes with no
docstring and generates a minimal docstring stub from the signature
(parameter names for functions, nothing invented about behaviour).
"""

from __future__ import annotations

import ast

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}


def _stub_docstring_for_function(node: ast.FunctionDef) -> str:
    params = [a.arg for a in node.args.args if a.arg not in ("self", "cls")]
    lines = [f"TODO: describe what {node.name} does."]
    if params:
        lines.append("")
        lines.append("Args:")
        for p in params:
            lines.append(f"    {p}: TODO")
    return "\n".join(lines)


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in _SUPPORTED:
        return CapabilityResult.ok(
            summary=f"CAP-008 has no generator yet for language '{context.language}'",
        )

    try:
        tree = ast.parse(context.code)
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Could not parse source: {exc}")

    findings = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if ast.get_docstring(node) is None:
                kind = "function" if isinstance(node, ast.FunctionDef) else "class"
                stub = (
                    _stub_docstring_for_function(node)
                    if isinstance(node, ast.FunctionDef)
                    else f"TODO: describe what {node.name} represents."
                )
                findings.append(
                    {
                        "line": node.lineno,
                        "issue": f"missing-{kind}-docstring",
                        "detail": f"{kind.capitalize()} '{node.name}' has no docstring.",
                        "proposed_docstring": stub,
                    }
                )

    summary = (
        f"Found {len(findings)} undocumented function(s)/class(es)."
        if findings
        else "No undocumented functions/classes found by CAP-008's current rule set."
    )
    return CapabilityResult.ok(summary=summary, findings=findings)
