from __future__ import annotations

from typing import Any

from capabilities.base import CapabilityContext, CapabilityResult
from layers.layer_03_cognitive.llm_interface import LLMInterface, LLMQueryError


def run(context: CapabilityContext) -> CapabilityResult:
    """Generic generated capability runtime.

    Evolution creates metadata/lineage first; this runtime turns that learned
    pattern into a reusable LLM-backed skill while keeping the standard
    capability interface used by the existing registry.
    """
    request = str(context.metadata.get("request", "")).strip()
    if not request:
        return CapabilityResult.fail("Generated capability requires the original request in context metadata.")
    timeout = float(context.parameters.get("llm_timeout_seconds", 120.0))
    model = str(context.parameters.get("llm_model", ""))
    provider = context.parameters.get("llm_provider_instance")
    llm = LLMInterface(provider=provider, timeout_seconds=timeout)
    instruction = (
        "You are executing a generated SPS capability created from a previously observed failure pattern. "
        "Apply the requested improvement to the supplied source code. Return only the complete updated source code.\n\n"
        f"Capability pattern: {context.metadata.get('failure_pattern', '')}\n"
        f"Original request: {request}\n"
        f"Language: {context.language}\n"
    )
    try:
        raw = llm.query(code=context.code, instruction=instruction, model=model, temperature=0.1)
    except LLMQueryError as exc:
        return CapabilityResult.fail(str(exc))
    output = raw.strip()
    if "```" in output:
        lines = output.splitlines()
        fenced = [line for line in lines if not line.strip().startswith("```")]
        output = "\n".join(fenced).strip()
    if not output:
        return CapabilityResult.fail("Generated capability produced empty output.")
    return CapabilityResult.ok("Applied the evolved capability pattern.", modified_code=output)
