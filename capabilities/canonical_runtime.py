"""Execution helpers for the ten canonical SPS-CA capabilities."""

from __future__ import annotations

import ast
import json
import re
from typing import Any

from capabilities.base import CapabilityContext, CapabilityResult
from layers.layer_03_cognitive.llm_interface import LLMInterface, LLMQueryError

_FENCE_RE = re.compile(r"```(?:[A-Za-z0-9_+#.-]+)?\s*\n?(.*?)\n?```", re.DOTALL)


def _provider(context: CapabilityContext) -> LLMInterface:
    provider = context.parameters.get("llm_provider")
    timeout = float(context.parameters.get("llm_timeout_seconds", 120.0))
    return LLMInterface(provider=provider, timeout_seconds=timeout)


def _model(context: CapabilityContext) -> str:
    return str(context.parameters.get("llm_model", ""))


def _clean_code(text: str) -> str:
    value = str(text or "").strip()
    fences = _FENCE_RE.findall(value)
    if fences:
        value = max(fences, key=len).strip()
    for prefix in ("modified code:", "here's the code:", "here is the code:"):
        if value.lower().startswith(prefix):
            value = value.split(":", 1)[1].lstrip()
            break
    return value.strip()


def _llm_code(context: CapabilityContext, instruction: str, *, require_source: bool = True) -> CapabilityResult:
    if require_source and not context.code.strip():
        return CapabilityResult.fail(error="This capability requires existing source code.")
    try:
        output = _provider(context).query(code=context.code, instruction=instruction, model=_model(context), temperature=0.0)
    except LLMQueryError as exc:
        return CapabilityResult.fail(error=str(exc))
    modified = _clean_code(output)
    if not modified:
        return CapabilityResult.fail(error="The reasoning model returned no source code.")
    if require_source and modified == context.code.strip():
        return CapabilityResult.fail(error="The requested operation produced no source-code change.")
    newline = "\n" if context.code.endswith("\n") else ""
    return CapabilityResult.ok(summary="Applied the requested source-code operation.", modified_code=modified + newline)


def _llm_report(context: CapabilityContext, instruction: str) -> CapabilityResult:
    try:
        output = _provider(context).query(code=context.code, instruction=instruction, model=_model(context), temperature=0.0)
    except LLMQueryError as exc:
        return CapabilityResult.fail(error=str(exc))
    text = str(output or "").strip()
    if not text:
        return CapabilityResult.fail(error="The reasoning model returned an empty analysis.")
    return CapabilityResult.ok(summary=text, findings=[{"report": text}])


def code_generation(context: CapabilityContext) -> CapabilityResult:
    request = str(context.metadata.get("request", "")).strip()
    if not request:
        return CapabilityResult.fail(error="Code Generation requires a user request.")
    return _llm_code(
        context,
        "Create the complete source code requested by the user. The working source may be empty. "
        "Implement only the requested program; preserve useful supplied source when the user asks for an extension. "
        "Do not generate tests unless the user explicitly asks for tests. Return ONLY the complete source file, "
        "without Markdown fences or explanations.\n\nUSER REQUEST:\n" + request,
        require_source=False,
    )


def code_modification(context: CapabilityContext) -> CapabilityResult:
    return _llm_code(
        context,
        "Modify the supplied source exactly as requested. Preserve unrelated behavior. Return ONLY the complete "
        "modified source file, without tests, explanations, Markdown fences, or unrelated changes.\n\nUSER REQUEST:\n"
        + str(context.metadata.get("request", "")).strip(),
    )


def code_analysis(context: CapabilityContext) -> CapabilityResult:
    return _llm_report(
        context,
        "Explain and analyze this source for the user. Cover purpose, important symbols/functions, control flow, "
        "inputs/outputs, and notable design or complexity observations. Do not modify code. Do not generate tests.\n\n"
        "USER REQUEST:\n" + str(context.metadata.get("request", "")).strip(),
    )


def bug_diagnosis(context: CapabilityContext) -> CapabilityResult:
    return _llm_report(
        context,
        "Diagnose defects in the supplied source. Identify the likely bug, evidence, root cause, and a concise "
        "recommended fix. Do not change the source and do not generate tests unless explicitly requested.\n\n"
        "USER REQUEST:\n" + str(context.metadata.get("request", "")).strip(),
    )


def bug_fixing(context: CapabilityContext) -> CapabilityResult:
    return _llm_code(
        context,
        "Fix the diagnosed bug in the supplied source. Preserve unrelated behavior. Return ONLY the complete "
        "corrected source file. Do not add tests or unrelated features.\n\nUSER REQUEST:\n"
        + str(context.metadata.get("request", "")).strip(),
    )


def refactoring(context: CapabilityContext) -> CapabilityResult:
    return _llm_code(
        context,
        "Refactor or optimize the supplied source according to the user's request while preserving intended behavior. "
        "Return ONLY the complete source file. Do not generate tests unless explicitly requested.\n\nUSER REQUEST:\n"
        + str(context.metadata.get("request", "")).strip(),
    )


def _test_assertion(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    if fn.args.vararg or fn.args.kwarg or fn.args.kwonlyargs or not fn.args.args:
        return None
    ret = fn.body[-1].value if fn.body and isinstance(fn.body[-1], ast.Return) else None
    call = f"{fn.name}({', '.join('2' for _ in fn.args.args)})"
    if ret is None:
        return f"assert {call} is None"
    try:
        values = {arg.arg: 2 for arg in fn.args.args}
        if isinstance(ret, ast.Constant):
            return f"assert {call} == {ast.unparse(ret)}"
        expected = eval(compile(ast.Expression(ret), "<cap007>", "eval"), {"__builtins__": {}}, values)
        return f"assert {call} == {expected!r}"
    except Exception:
        return f"assert {call} is not None"


def generate_tests(context: CapabilityContext) -> CapabilityResult:
    request = str(context.metadata.get("request", "")).lower()
    if not re.search(r"\b(test|pytest|unit test|tests)\b", request):
        return CapabilityResult.fail(error="Test Generation requires an explicit test-generation request.")
    if context.language != "python":
        return CapabilityResult.ok(summary=f"Test generation is not implemented for '{context.language}' yet.")
    if not context.code.strip():
        return CapabilityResult.fail(error="Test Generation requires source code to test.")
    try:
        tree = ast.parse(context.code)
    except SyntaxError as exc:
        return CapabilityResult.fail(error=f"Cannot generate tests from invalid Python source: {exc}")
    functions = [
        node for node in ast.iter_child_nodes(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")
    ]
    if not functions:
        return CapabilityResult.ok(summary="No public top-level Python functions were found to test.")
    module_name = (context.file_path or "main.py").rsplit("/", 1)[-1].removesuffix(".py")
    names = [fn.name for fn in functions]
    lines = [f"from {module_name} import {', '.join(names)}", ""]
    findings = []
    for fn in functions:
        assertion = _test_assertion(fn)
        if assertion is None:
            continue
        lines.extend([f"def test_{fn.name}():", f"    {assertion}", ""])
        findings.append({"function": fn.name, "generated": True})
    if not findings:
        return CapabilityResult.fail(error="No safe executable test could be inferred.")
    return CapabilityResult.ok(summary=f"Generated {len(findings)} pytest smoke test(s).", modified_code="\n".join(lines).rstrip() + "\n", findings=findings)


def documentation(context: CapabilityContext) -> CapabilityResult:
    return _llm_code(
        context,
        "Add focused documentation to the supplied source: docstrings/comments for important public functions or "
        "classes. Preserve behavior. Return ONLY the complete modified source file. Do not generate tests or unrelated "
        "features.\n\nUSER REQUEST:\n" + str(context.metadata.get("request", "")).strip(),
    )


def validation(context: CapabilityContext) -> CapabilityResult:
    if not context.code.strip():
        return CapabilityResult.fail(error="Code Validation & Review requires source code.")
    findings: list[dict[str, Any]] = []
    syntax_ok = True
    if context.language == "python":
        try:
            ast.parse(context.code)
            compile(context.code, context.file_path or "<source>", "exec")
        except SyntaxError as exc:
            syntax_ok = False
            findings.append({"category": "syntax", "severity": "error", "message": str(exc)})
    pairs = {"(": ")", "[": "]", "{": "}"}
    stack: list[str] = []
    in_string = False
    quote = ""
    escaped = False
    for char in context.code:
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_string:
            escaped = True
            continue
        if char in {"'", '"'}:
            if in_string and char == quote:
                in_string = False
            elif not in_string:
                in_string, quote = True, char
            continue
        if in_string:
            continue
        if char in pairs:
            stack.append(pairs[char])
        elif char in pairs.values():
            if not stack or stack.pop() != char:
                findings.append({"category": "structure", "severity": "error", "message": "Unbalanced delimiters."})
                break
    if stack:
        findings.append({"category": "structure", "severity": "error", "message": "Unbalanced delimiters."})
    if syntax_ok and not findings:
        findings.append({"category": "syntax", "severity": "info", "message": "Source passed basic validation."})
    return CapabilityResult.ok(summary="Validation completed." if syntax_ok and not any(f["severity"] == "error" for f in findings) else "Validation found issues.", findings=findings)


def project_operations(context: CapabilityContext) -> CapabilityResult:
    request = str(context.metadata.get("request", "")).strip()
    if not request:
        return CapabilityResult.fail(error="Project/File Operations requires a request.")
    try:
        output = _provider(context).query(code=context.code, instruction=("Plan the requested project/file operation without applying it. Return JSON only with keys operation, target, files, and notes. Never invent credentials or destructive commands.\n\nUSER REQUEST:\n" + request), model=_model(context), temperature=0.0)
    except LLMQueryError as exc:
        return CapabilityResult.fail(error=str(exc))
    raw = str(output or "").strip()
    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(match.group(0)) if match else {"operation": "plan", "target": "", "files": [], "notes": raw}
    except json.JSONDecodeError:
        data = {"operation": "plan", "target": "", "files": [], "notes": raw}
    return CapabilityResult.ok(summary="Project/file operation plan prepared; no filesystem mutation was performed.", findings=[data])


DISPATCH = {"CAP-001": code_generation, "CAP-002": code_modification, "CAP-003": code_analysis, "CAP-004": bug_diagnosis, "CAP-005": bug_fixing, "CAP-006": refactoring, "CAP-007": generate_tests, "CAP-008": documentation, "CAP-009": validation, "CAP-010": project_operations}


def run_canonical(capability_id: str, context: CapabilityContext) -> CapabilityResult:
    function = DISPATCH.get(capability_id)
    if function is None:
        return CapabilityResult.fail(error=f"Unknown canonical capability: {capability_id}")
    return function(context)
