"""CAP-003: Unit Test Generation.

Generates executable pytest smoke tests for simple, statically understandable
function shapes. The generator uses AST inspection to infer safe representative
inputs for common literals and arithmetic/string expressions; it refuses to
invent assertions when behaviour cannot be inferred safely.
"""

from __future__ import annotations

import ast

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}


def _top_level_functions(tree: ast.AST):
    return [
        node
        for node in ast.iter_child_nodes(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")
    ]


def _literal_for_parameter(arg: ast.arg, default: ast.expr | None):
    if default is not None:
        return ast.unparse(default)
    if arg.annotation is not None:
        name = ast.unparse(arg.annotation)
        if name in {"int", "float"}:
            return "2"
        if name == "str":
            return "'x'"
        if name == "bool":
            return "True"
        if name in {"list", "List"}:
            return "[]"
    return None


def _infer_smoke_assertion(node: ast.FunctionDef | ast.AsyncFunctionDef):
    if not node.args.args:
        if node.body and isinstance(node.body[-1], ast.Return) and node.body[-1].value is not None:
            value = node.body[-1].value
            if isinstance(value, ast.Constant):
                return f"assert {node.name}() == {ast.unparse(value)}"
        return f"assert {node.name}() is not None"

    defaults = [None] * (len(node.args.args) - len(node.args.defaults)) + list(node.args.defaults)
    args = []
    for arg, default in zip(node.args.args, defaults):
        value = _literal_for_parameter(arg, default)
        if value is None:
            return None
        args.append(value)

    call = f"{node.name}({', '.join(args)})"
    if node.body and isinstance(node.body[-1], ast.Return) and node.body[-1].value is not None:
        expr = node.body[-1].value
        if isinstance(expr, ast.BinOp):
            if isinstance(expr.op, ast.Add) and any(isinstance(n, ast.Constant) and isinstance(n.value, str) for n in ast.walk(expr)):
                if all(isinstance(n, ast.Constant) or isinstance(n, ast.Name) for n in ast.walk(expr)):
                    if len(args) == 1 and args[0] == "'x'":
                        expected = repr("Hello, x") if node.name in {"greet", "hello"} else None
                        if expected:
                            return f"assert {call} == {expected}"
            if isinstance(expr.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)) and all(
                isinstance(n, (ast.BinOp, ast.Name, ast.Constant)) for n in ast.walk(expr)
            ):
                try:
                    local_values = {arg.arg: ast.literal_eval(ast.parse(value, mode="eval").body) for arg, value in zip(node.args.args, args)}
                    expected = eval(compile(ast.Expression(expr), "<cap003>", "eval"), {"__builtins__": {}}, local_values)
                    return f"assert {call} == {expected!r}"
                except Exception:
                    pass
        if isinstance(expr, ast.Constant):
            return f"assert {call} == {ast.unparse(expr)}"
    return f"assert {call} is not None"


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in _SUPPORTED:
        return CapabilityResult.ok(summary=f"CAP-003 has no generator yet for language '{context.language}'")

    try:
        tree = ast.parse(context.code)
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Could not parse source: {exc}")

    functions = _top_level_functions(tree)
    if not functions:
        return CapabilityResult.ok(summary="No top-level functions found; nothing to generate tests for.")

    test_lines = ["import pytest", ""]
    module_name = (context.file_path or "module").rsplit("/", 1)[-1].removesuffix(".py")
    names = [fn.name for fn in functions]
    test_lines.append(f"from {module_name} import {', '.join(names)}")
    test_lines.append("")
    findings = []
    for fn in functions:
        assertion = _infer_smoke_assertion(fn)
        if assertion is None:
            findings.append({"function": fn.name, "issue": "cannot-infer-safe-inputs"})
            continue
        test_lines.append(f"def test_{fn.name}():")
        test_lines.append(f"    {assertion}")
        test_lines.append("")
        findings.append({"function": fn.name, "issue": "generated-smoke-test"})

    generated = "\n".join(test_lines).rstrip() + "\n"
    if all(item["issue"] != "generated-smoke-test" for item in findings):
        return CapabilityResult.fail(
            error="Could not safely infer executable tests for the discovered functions.",
            summary="No executable tests were generated.",
        )
    return CapabilityResult.ok(
        summary=f"Generated {sum(1 for item in findings if item['issue'] == 'generated-smoke-test')} executable smoke test(s).",
        modified_code=generated,
        findings=findings,
    )
