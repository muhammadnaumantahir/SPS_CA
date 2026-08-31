"""CAP-003: Unit Test Generation.

Structure-only seed capability. Generates a pytest stub module listing one
placeholder test per top-level function/method found in the source. The
generated tests are intentionally left as ``TODO`` bodies: filling them in
with real assertions requires understanding intended behaviour, which is
out of scope for a seed capability and is a natural candidate for later
capability generation/evolution (Layer 8).
"""

from __future__ import annotations

import ast

from capabilities.base import CapabilityContext, CapabilityResult

_SUPPORTED = {"python"}


def _top_level_functions(tree: ast.AST):
    names = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                names.append(node.name)
    return names


def run(context: CapabilityContext) -> CapabilityResult:
    if context.language not in _SUPPORTED:
        return CapabilityResult.ok(
            summary=f"CAP-003 has no generator yet for language '{context.language}'",
        )

    try:
        tree = ast.parse(context.code)
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Could not parse source: {exc}")

    functions = _top_level_functions(tree)
    if not functions:
        return CapabilityResult.ok(
            summary="No top-level functions found; nothing to generate tests for.",
        )

    module_name = (context.file_path or "module").rsplit("/", 1)[-1].removesuffix(".py")
    lines = [
        "import pytest",
        "",
        f"from {module_name} import {', '.join(functions)}" if module_name else "",
        "",
    ]
    for fn in functions:
        lines.append(f"def test_{fn}():")
        lines.append(f"    # TODO: exercise {fn}() with representative inputs")
        lines.append("    pytest.skip('generated stub: implement assertions')")
        lines.append("")

    generated = "\n".join(lines)
    return CapabilityResult.ok(
        summary=f"Generated {len(functions)} stub test(s).",
        modified_code=generated,
        findings=[{"function": fn} for fn in functions],
    )
