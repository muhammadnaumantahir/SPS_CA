"""SPS-CA Brain: model intelligence kept separate from capabilities.

The Brain is a replaceable intelligence service. Ollama is the default
provider, but SPS-CA capabilities never become the Brain and the Brain is
never registered as a capability.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from layers.layer_02_cognitive_core.llm_interface import LLMInterface, LLMQueryError

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)

_SYSTEM_PROMPT = """You are the AI brain of SPS-CA, a governed self-programming coding assistant.
The Brain provides reasoning and planning; it is NOT a capability and it does
NOT execute code or directly apply source changes.

Given the user's request, target code, optional conversation history, and the
available capability catalog, produce an ordered execution plan. Return JSON only:
{
  "intent": "short description of what the user actually wants",
  "reasoning": "brief reasoning summary",
  "steps": [
    {"capability_id": "CAP-NNN", "reason": "why this capability is needed"}
  ]
}

Rules:
1. Select only IDs in the supplied capability catalog.
2. Never invent a capability.
3. Do not select a test-generation capability merely because the request
   mentions validation, function, code, or correctness. Generate tests only
   when testing is requested or clearly required by the plan.
4. Prefer the smallest set of capabilities that satisfies the request.
5. Preserve the user's requested intent exactly, while using conversation
   context to understand follow-up feedback such as "make that stricter" or
   "also handle negative values".
6. Treat the supplied code as the current working state. A follow-up request
   may refer to changes made in an earlier turn.
7. Order capabilities logically: analysis -> repair/transformation -> tests
   when requested/needed.
8. The Brain itself must never be represented as CAP-001 or any CAP-NNN.
"""


class BrainError(Exception):
    """Raised when the Brain cannot produce a safe routing plan."""


@dataclass(frozen=True)
class BrainPlan:
    intent: str
    reasoning: str
    steps: list[dict[str, str]] = field(default_factory=list)
    provider: str = "Ollama"
    model: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "brain": {"provider": self.provider, "model": self.model},
            "intent": self.intent,
            "reasoning": self.reasoning,
            "steps": list(self.steps),
        }


class Brain:
    """Provider-neutral reasoning brain used by the Cognitive Core."""

    def __init__(
        self,
        provider: Optional[Any] = None,
        model: str = "",
        timeout_seconds: float = 120.0,
    ) -> None:
        self.provider = provider
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.llm = LLMInterface(provider=provider, timeout_seconds=timeout_seconds)

    @property
    def provider_name(self) -> str:
        return type(self.llm.provider).__name__.replace("Provider", "")

    def is_available(self) -> bool:
        return self.llm.is_available()

    def plan(
        self,
        *,
        request: str,
        code: str,
        language: str,
        file_path: str,
        capability_catalog: list[dict[str, Any]],
        conversation: Optional[list[dict[str, str]]] = None,
    ) -> BrainPlan:
        request = request.strip()
        if not request:
            raise BrainError("Brain requires a non-empty request.")
        if not capability_catalog:
            raise BrainError("Brain received an empty capability catalog.")

        catalog = [
            {
                "id": str(item.get("id", "")),
                "name": str(item.get("name", "")),
                "description": str(item.get("description", "")),
                "tags": list(item.get("tags", [])),
            }
            for item in capability_catalog
            if item.get("id")
        ]
        history = conversation or []
        # Keep the prompt bounded while preserving the most recent conversation turns.
        history = history[-12:]
        conversation_text = "\n".join(
            f"{item.get('role', 'user').upper()}: {str(item.get('content', '')).strip()}"
            for item in history
            if str(item.get("content", "")).strip()
        ) or "(no previous conversation)"

        prompt = (
            f"{_SYSTEM_PROMPT}\n\n"
            f"TARGET LANGUAGE: {language}\n"
            f"TARGET FILE: {file_path}\n"
            f"CONVERSATION HISTORY:\n{conversation_text}\n\n"
            f"LATEST USER REQUEST:\n{request}\n\n"
            f"CURRENT WORKING SOURCE:\n{code}\n\n"
            f"AVAILABLE CAPABILITIES:\n{json.dumps(catalog, ensure_ascii=False)}"
        )
        try:
            raw = self.llm.query(
                code=code,
                instruction=prompt,
                model=self.model,
                temperature=0.0,
            )
        except LLMQueryError as exc:
            raise BrainError(str(exc)) from exc

        try:
            match = _JSON_RE.search(raw.strip())
            if not match:
                raise ValueError("model did not return JSON")
            data = json.loads(match.group(0))
        except (ValueError, json.JSONDecodeError) as exc:
            raise BrainError(f"Brain returned invalid planning JSON: {exc}") from exc

        if not isinstance(data, dict) or not isinstance(data.get("steps", []), list):
            raise BrainError("Brain returned an invalid plan structure.")

        valid_ids = {item["id"] for item in catalog}
        steps: list[dict[str, str]] = []
        for step in data.get("steps", []):
            if not isinstance(step, dict):
                raise BrainError("Brain returned a malformed plan step.")
            capability_id = str(step.get("capability_id", ""))
            if capability_id not in valid_ids:
                raise BrainError(f"Brain selected unavailable capability: {capability_id or '<empty>'}")
            steps.append({
                "capability_id": capability_id,
                "reason": str(step.get("reason", "")),
            })

        return BrainPlan(
            intent=str(data.get("intent", "")),
            reasoning=str(data.get("reasoning", "")),
            steps=steps,
            provider=self.provider_name,
            model=self.model,
        )
