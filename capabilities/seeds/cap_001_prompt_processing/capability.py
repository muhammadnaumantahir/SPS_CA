"""CAP-001: Prompt Processing and Ollama brain routing."""

from __future__ import annotations

import json
import re
from typing import Any

from capabilities.base import CapabilityContext, CapabilityResult
from layers.layer_02_cognitive_core.llm_interface import LLMInterface, LLMQueryError

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)

_SYSTEM_INSTRUCTION = """You are the brain of SPS-CA.
Process the user's coding request and decide what the system should do next.
You MUST return JSON only with this exact shape:
{
  "intent": "short description",
  "steps": [
    {"capability_id": "CAP-NNN", "reason": "why this capability is needed"}
  ]
}

Rules:
1. CAP-001 is already running and must NOT appear in steps.
2. Select only capability IDs from the supplied allowlist.
3. Preserve the user's intent exactly. Do not turn a source-code modification
   request into test generation unless the user explicitly asks for tests.
4. Order steps from analysis/repair through modification/testing as appropriate.
5. Do not invent capability IDs.
6. If no capability is appropriate, return an empty steps array.
"""


def _parse_json(text: str) -> dict[str, Any]:
    value = text.strip()
    match = _JSON_RE.search(value)
    if not match:
        raise ValueError("Ollama did not return a JSON routing plan.")
    data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("Ollama routing response must be a JSON object.")
    return data


def run(context: CapabilityContext) -> CapabilityResult:
    """Use Ollama as the authoritative planning brain for the request."""
    request = str(context.metadata.get("request", "")).strip()
    catalog = context.parameters.get("capability_catalog", [])
    if not request:
        return CapabilityResult.fail(error="Prompt Processing requires a non-empty user request.")

    allowlist = []
    for item in catalog:
        if isinstance(item, dict) and item.get("id"):
            allowlist.append({
                "id": str(item["id"]),
                "name": str(item.get("name", "")),
                "description": str(item.get("description", "")),
                "tags": list(item.get("tags", [])),
            })
    if not allowlist:
        return CapabilityResult.fail(error="Prompt Processing received an empty capability allowlist.")

    instruction = (
        f"{_SYSTEM_INSTRUCTION}\n\n"
        f"TARGET LANGUAGE: {context.language}\n"
        f"TARGET FILE: {context.file_path}\n"
        f"USER REQUEST:\n{request}\n\n"
        f"AVAILABLE CAPABILITIES:\n{json.dumps(allowlist, ensure_ascii=False)}"
    )
    try:
        llm = LLMInterface(
            provider=context.parameters.get("llm_provider"),
            timeout_seconds=float(context.parameters.get("llm_timeout_seconds", 120.0)),
        )
        raw = llm.query(
            code=context.code,
            instruction=instruction,
            model=str(context.parameters.get("llm_model", "")),
            temperature=0.0,
        )
        plan = _parse_json(raw)
    except (LLMQueryError, ValueError, json.JSONDecodeError) as exc:
        return CapabilityResult.fail(error=f"Prompt Processing brain failure: {exc}")

    valid_ids = {item["id"] for item in allowlist}
    steps = plan.get("steps", [])
    if not isinstance(steps, list):
        return CapabilityResult.fail(error="Ollama returned an invalid 'steps' value.")

    normalized = []
    for step in steps:
        if not isinstance(step, dict):
            return CapabilityResult.fail(error="Ollama returned a malformed capability step.")
        capability_id = str(step.get("capability_id", ""))
        if capability_id == "CAP-001":
            return CapabilityResult.fail(error="Ollama attempted to recursively select CAP-001.")
        if capability_id not in valid_ids:
            return CapabilityResult.fail(
                error=f"Ollama selected capability outside the allowlist: {capability_id or '<empty>'}"
            )
        normalized.append({
            "capability_id": capability_id,
            "reason": str(step.get("reason", "")),
        })

    return CapabilityResult.ok(
        summary="CAP-001 processed the prompt using Ollama as the SPS-CA brain.",
        findings=[{
            "issue": "prompt-plan",
            "intent": str(plan.get("intent", "")),
            "steps": normalized,
            "brain": "Ollama",
        }],
    )
