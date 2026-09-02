"""CAP-003: Unit Test Generation.

Generates executable pytest smoke tests for simple, statically understandable
function shapes. Inputs are inferred from defaults, annotations, or a narrow
string-concatenation pattern. Ambiguous signatures are left untouched.
"""

from __future__ import annotations

import ast

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}


def _top_level_functions(tree: ast.AST):
    return [
        node for node in ast.iter_child_nodes(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")
    ]


def _is_string_concat(expr: ast.expr) -> bool:
    return isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add) and any(
        isinstance(n, ast.Constant) and isinstance(n.value, str) for n in ast.walk(expr)
    )


def _literal_for_parameter(arg: ast.arg, default: ast.expr | None, *, string_mode: bool = False):
    if default is not None:
        return ast.unparse(default)
    if string_mode:
        return "'x'"
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
    if node.args.vararg or node.args.kwarg or node.args.kwonlyargs:
        return None

    return_expr = node.body[-1].value if node.body and isinstance(node.body[-1], ast.Return) else None
    string_mode = bool(return_expr is not None and _is_string_concat(return_expr))
    defaults = [None] * (len(node.args.args) - len(node.args.defaults)) + list(node.args.defaults)
    args = []
    for arg, default in zip(node.args.args, defaults):
        if arg.arg in {"self", "cls"}:
            return None
        value = _literal_for_parameter(arg, default, string_mode=string_mode)
        if value is None:
            return None
        args.append(value)

    call = f"{node.name}({', '.join(args)})"
    if isinstance(return_expr, ast.Constant):
        return f"assert {call} == {ast.unparse(return_expr)}"
    if string_mode:
        try:
            local_values = {arg.arg: "x" for arg in node.args.args}
            expected = eval(compile(ast.Expression(return_expr), "<cap003>", "eval"), {"__builtins__": {}}, local_values)
            return f"assert {call} == {expected!r}"
        except Exception:
            return None
    if isinstance(return_expr, ast.BinOp) and isinstance(return_expr.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
        try:
            local_values = {
                arg.arg: ast.literal_eval(ast.parse(value, mode="eval").body)
                for arg, value in zip(node.args.args, args)
            }
            expected = eval(compile(ast.Expression(return_expr), "<cap003>", "eval"), {"__builtins__": {}}, local_values)
            return f"assert {call} == {expected!r}"
        except Exception:
            return None
    if not node.args.args:
        return f"assert {call} is not None"
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

    module_name = (context.file_path or "module").rsplit("/", 1)[-1].removesuffix(".py")
    names = [fn.name for fn in functions]
    test_lines = ["import pytest", "", f"from {module_name} import {', '.join(names)}", ""]
    findings = []
    for fn in functions:
        assertion = _infer_smoke_assertion(fn)
        if assertion is None:
            findings.append({"function": fn.name, "issue": "cannot-infer-safe-inputs"})
            continue
        test_lines.extend([f"def test_{fn.name}():", f"    {assertion}", ""])
        findings.append({"function": fn.name, "issue": "generated-smoke-test"})

    if not any(item["issue"] == "generated-smoke-test" for item in findings):
        return CapabilityResult.fail(
            error="Could not safely infer executable tests for the discovered functions.",
            summary="No executable tests were generated.",
        )
    return CapabilityResult.ok(
        summary=f"Generated {sum(item['issue'] == 'generated-smoke-test' for item in findings)} executable smoke test(s).",
        modified_code="\n".join(test_lines).rstrip() + "\n",
        findings=findings,
    )
