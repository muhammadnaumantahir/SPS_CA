"""CAP-007: Type Annotation Addition.

Adds parameter annotations only when the type can be inferred safely from a
literal default value. It never guesses types for parameters without reliable
static evidence.
"""

from __future__ import annotations

import ast

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}


def _infer_type_from_default(default: ast.expr):
    if isinstance(default, ast.Constant):
        value = default.value
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, str):
            return "str"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
    return None


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in _SUPPORTED:
        return CapabilityResult.ok(summary=f"CAP-007 has no rule set yet for language '{context.language}'")
    try:
        tree = ast.parse(context.code)
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Could not parse source: {exc}")

    findings = []
    edits = []
    lines = context.code.splitlines()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        positional = node.args.args
        defaults = [None] * (len(positional) - len(node.args.defaults)) + list(node.args.defaults)
        for arg, default in zip(positional, defaults):
            if arg.arg in {"self", "cls"} or arg.annotation is not None:
                continue
            inferred = _infer_type_from_default(default) if default is not None else None
            findings.append({
                "line": node.lineno,
                "issue": "missing-parameter-annotation",
                "detail": f"Parameter '{arg.arg}' of '{node.name}' has no type annotation."
                + (f" Inferred type: {inferred}." if inferred else ""),
                "inferred_type": inferred,
            })
            if inferred and context.parameters.get("apply", False):
                line_index = node.lineno - 1
                original_line = lines[line_index]
                marker = f"{arg.arg}"
                replacement = f"{arg.arg}: {inferred}"
                if marker in original_line and replacement not in original_line:
                    lines[line_index] = original_line.replace(marker, replacement, 1)
                    edits.append(arg.arg)

        if node.returns is None:
            findings.append({
                "line": node.lineno,
                "issue": "missing-return-annotation",
                "detail": f"Function '{node.name}' has no return type annotation.",
                "inferred_type": None,
            })

    if not findings:
        return CapabilityResult.ok(summary="No missing annotations found by CAP-007's current rule set.")
    if not context.parameters.get("apply", False):
        return CapabilityResult.ok(summary=f"Found {len(findings)} missing annotation(s).", findings=findings)
    if not edits:
        return CapabilityResult.ok(summary="Missing annotations found, but none could be inferred safely.", findings=findings)

    modified = "\n".join(lines) + ("\n" if context.code.endswith("\n") else "")
    return CapabilityResult.ok(
        summary=f"Added {len(edits)} safely inferred parameter annotation(s).",
        modified_code=modified,
        findings=findings,
    )
