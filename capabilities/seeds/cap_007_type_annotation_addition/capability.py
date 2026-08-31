"""CAP-007: Type Annotation Addition.

Structure-only seed capability. Finds function parameters with no type
annotation and, where a default value's literal type is obvious (str,
int, float, bool), proposes that annotation. Parameters without a
sufficiently obvious inferred type are reported as needing annotation but
are not guessed at.
"""

from __future__ import annotations

import ast

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}

_LITERAL_TYPE_MAP = {
    str: "str",
    bool: "bool",  # checked before int, since bool is an int subclass
    int: "int",
    float: "float",
}


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
        return CapabilityResult.ok(
            summary=f"CAP-007 has no rule set yet for language '{context.language}'",
        )

    try:
        tree = ast.parse(context.code)
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Could not parse source: {exc}")

    findings = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        args = node.args
        positional = args.args
        defaults = args.defaults
        offset = len(positional) - len(defaults)

        for i, arg in enumerate(positional):
            if arg.arg == "self" or arg.arg == "cls":
                continue
            if arg.annotation is not None:
                continue
            default_index = i - offset
            inferred = None
            if default_index >= 0:
                inferred = _infer_type_from_default(defaults[default_index])
            findings.append(
                {
                    "line": node.lineno,
                    "issue": "missing-parameter-annotation",
                    "detail": f"Parameter '{arg.arg}' of '{node.name}' has no type "
                    "annotation."
                    + (f" Inferred type: {inferred}." if inferred else ""),
                    "inferred_type": inferred,
                }
            )

        if node.returns is None:
            findings.append(
                {
                    "line": node.lineno,
                    "issue": "missing-return-annotation",
                    "detail": f"Function '{node.name}' has no return type annotation.",
                }
            )

    summary = (
        f"Found {len(findings)} missing annotation(s)."
        if findings
        else "No missing annotations found by CAP-007's current rule set."
    )
    return CapabilityResult.ok(summary=summary, findings=findings)
