"""CAP-008: Documentation Generation.

Detects undocumented functions/classes and can insert conservative docstring
stubs derived only from the symbol name and function parameter names. It never
claims behavioural details that are not present in the source.
"""

from __future__ import annotations

import ast

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}


def _stub_docstring_for_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    params = [a.arg for a in node.args.args if a.arg not in ("self", "cls")]
    lines = [f"TODO: describe what {node.name} does."]
    if params:
        lines.extend(["", "Args:"])
        lines.extend(f"    {p}: TODO" for p in params)
    return "\n".join(lines)


def _indent(line: str) -> str:
    return line[: len(line) - len(line.lstrip())]


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in _SUPPORTED:
        return CapabilityResult.ok(summary=f"CAP-008 has no generator yet for language '{context.language}'")
    try:
        tree = ast.parse(context.code)
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Could not parse source: {exc}")

    findings = []
    inserts = []
    lines = context.code.splitlines()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if ast.get_docstring(node) is not None:
            continue
        is_function = isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        kind = "function" if is_function else "class"
        stub = _stub_docstring_for_function(node) if is_function else f"TODO: describe what {node.name} represents."
        findings.append({
            "line": node.lineno,
            "issue": f"missing-{kind}-docstring",
            "detail": f"{kind.capitalize()} '{node.name}' has no docstring.",
            "proposed_docstring": stub,
        })
        if context.parameters.get("apply", False) and node.body and node.lineno <= getattr(node.body[0], "lineno", node.lineno):
            body_line = node.body[0].lineno - 1
            base_indent = _indent(lines[node.lineno - 1])
            doc_indent = base_indent + "    "
            doc_lines = stub.splitlines()
            quote_start = [doc_indent + '"""' + doc_lines[0]]
            quote_start.extend(doc_indent + line for line in doc_lines[1:])
            quote_start.append(doc_indent + '"""')
            inserts.append((body_line, quote_start))

    if not findings:
        return CapabilityResult.ok(summary="No undocumented functions/classes found by CAP-008's current rule set.")
    if not context.parameters.get("apply", False):
        return CapabilityResult.ok(summary=f"Found {len(findings)} undocumented function(s)/class(es).", findings=findings)

    updated = list(lines)
    for index, inserted_lines in sorted(inserts, reverse=True):
        updated[index:index] = inserted_lines
    modified = "\n".join(updated) + ("\n" if context.code.endswith("\n") else "")
    return CapabilityResult.ok(
        summary=f"Inserted documentation stubs for {len(inserts)} undocumented symbol(s).",
        modified_code=modified,
        findings=findings,
    )
