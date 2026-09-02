"""CAP-011: explicit natural-language code modification."""

from __future__ import annotations

import re

from capabilities.base import CapabilityContext, CapabilityResult
from layers.layer_02_cognitive_core.llm_interface import LLMInterface, LLMQueryError

_SYSTEM_INSTRUCTION = """Modify the supplied source code to satisfy the user's request exactly.

Rules:
1. The request is authoritative: implement the requested change, not a generic test/demo.
2. Preserve all existing behavior unless the request explicitly changes it.
3. Return ONLY the complete modified source file. No Markdown fences, explanations, tests, labels, or commentary.
4. Do not invent unrelated features.
5. If the request says to add a function, actually add that function to the source file.
6. If the request specifies validation, implement input validation in the requested function rather than merely generating tests for it.
"""

_CODE_FENCE_RE = re.compile(r"^\s*```(?:[A-Za-z0-9_+-]+)?\s*\n?(.*?)\n?```\s*$", re.DOTALL)


def _clean_model_output(text: str) -> str:
    value = text.strip()
    match = _CODE_FENCE_RE.match(value)
    if match:
        value = match.group(1).strip("\n")
    if value.lower().startswith("modified code:"):
        value = value.split(":", 1)[1].lstrip()
    return value


def run(context: CapabilityContext) -> CapabilityResult:
    provider = context.parameters.get("llm_provider")
    timeout = float(context.parameters.get("llm_timeout_seconds", 120.0))
    model = str(context.parameters.get("llm_model", ""))
    request = str(context.metadata.get("request", "")).strip()
    if not request:
        return CapabilityResult.fail(error="Natural Language Code Modification requires a user request.")
    try:
        llm = LLMInterface(provider=provider, timeout_seconds=timeout)
        output = llm.query(
            code=context.code,
            instruction=f"{_SYSTEM_INSTRUCTION}\n\nUSER REQUEST:\n{request}",
            model=model,
            temperature=0.0,
        )
    except LLMQueryError as exc:
        return CapabilityResult.fail(error=str(exc))

    modified = _clean_model_output(output)
    if not modified:
        return CapabilityResult.fail(error="The code modification model returned empty source code.")
    if modified == context.code.strip():
        return CapabilityResult.fail(error="The requested code change produced no source-code change.")

    return CapabilityResult.ok(
        summary="Applied the explicit natural-language code modification with the Ollama brain.",
        modified_code=modified + ("\n" if context.code.endswith("\n") else ""),
    )
