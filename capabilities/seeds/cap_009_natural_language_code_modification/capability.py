"""CAP-011: explicit natural-language code modification."""

from __future__ import annotations

import re

from capabilities.base import CapabilityContext, CapabilityResult
from layers.layer_03_cognitive.llm_interface import LLMInterface, LLMQueryError

_SYSTEM_INSTRUCTION = """Modify the supplied source code to satisfy the user's request exactly.

Rules:
1. The request is authoritative: implement the requested change, not a generic test/demo.
2. Preserve all existing behavior unless the request explicitly changes it.
3. Return ONLY the complete modified source file. No Markdown fences, explanations, tests, labels, or commentary.
4. Do not invent unrelated features.
5. If the request says to add a function, actually add that function to the source file.
6. If the request specifies validation, implement input validation in the requested function rather than merely generating tests for it.
"""

_CODE_FENCE_RE = re.compile(r"```(?:[A-Za-z0-9_+-]+)?\s*\n?(.*?)\n?```", re.DOTALL)
_LEADING_PREAMBLE_RE = re.compile(
    r"^\s*(here'?s|here is|sure,?|okay,?|below is|the following is)[^\n]*:?\s*\n+",
    re.IGNORECASE,
)
_TRAILING_NOTE_RE = re.compile(
    r"\n+(this (adds|change|modification|implementation)|note:|explanation:).*$",
    re.IGNORECASE | re.DOTALL,
)


def _clean_model_output(text: str) -> str:
    """Extract just the source code from a model response.

    Real models — including local ones via Ollama — rarely return a
    perfectly bare fenced block. They commonly add a one-line preamble
    ("Here's the modified code:") or a trailing note after the fence.
    This pulls out the actual code wherever it is, instead of returning
    the whole messy response (prose + fences included) as if it were
    the file content.
    """
    value = text.strip()

    # Prefer the largest fenced code block anywhere in the response —
    # if the model wrapped the code in ``` fences at all, that block is
    # almost always the real answer, regardless of what surrounds it.
    fences = _CODE_FENCE_RE.findall(value)
    if fences:
        value = max(fences, key=len).strip("\n")
    else:
        # No fences at all — the model likely returned bare code (or
        # bare code with a short preamble/trailing note). Strip those.
        value = _LEADING_PREAMBLE_RE.sub("", value)
        value = _TRAILING_NOTE_RE.sub("", value)

    if value.lower().startswith("modified code:"):
        value = value.split(":", 1)[1].lstrip()
    return value.strip()


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
