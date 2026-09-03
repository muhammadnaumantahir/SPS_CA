"""AI-driven capability design for SPS Layer-8 evolution."""
from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from typing import Any, Optional

from layers.layer_03_cognitive_core.llm_interface import LLMInterface, LLMQueryError


@dataclass(frozen=True)
class AICapabilityDesign:
    name: str
    description: str
    entry_point: str
    supported_languages: list[str]
    source_code: str
    tests_code: str
    success_criteria: list[str]
    rationale: str


class AICapabilityDesigner:
    """Ask the Brain model to design a reusable capability from an observed gap."""

    def __init__(self, *, provider: Optional[Any] = None, model: str = "", timeout_seconds: Optional[float] = 120.0) -> None:
        self.llm = LLMInterface(provider=provider, timeout_seconds=timeout_seconds)
        self.model = model

    @property
    def provider_name(self) -> str:
        return type(self.llm.provider).__name__.replace("Provider", "")

    @staticmethod
    def _parse(raw: str) -> dict[str, Any]:
        text = str(raw or "").strip()
        decoder = json.JSONDecoder()
        try:
            value, _ = decoder.raw_decode(text)
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            pass
        for match in re.finditer(r"\{", text):
            try:
                value, _ = decoder.raw_decode(text[match.start():])
                if isinstance(value, dict):
                    return value
            except json.JSONDecodeError:
                continue
        raise ValueError("AI capability design was not valid JSON")

    @staticmethod
    def _require_source(source: str) -> str:
        value = str(source or "").strip()
        if "def run(" not in value or "CapabilityContext" not in value or "CapabilityResult" not in value:
            raise ValueError("generated capability must implement run(CapabilityContext) with CapabilityResult")
        ast.parse(value)
        return value

    @staticmethod
    def _require_tests(tests: str) -> str:
        value = str(tests or "").strip()
        if not value:
            raise ValueError("generated capability must include tests")
        ast.parse(value)
        return value

    def design(self, *, gap: str, language: str, capability_id: str, existing_capabilities: list[dict[str, Any]], observations: list[dict[str, Any]]) -> AICapabilityDesign:
        prompt = (
            "You are the SPS Brain capability-evolution designer. An unmet reusable capability requirement has been observed. "
            "Design ONE reusable capability to address the requirement. Layer 8 will govern, sandbox-test, and register it.\n\n"
            "Return JSON only:\n"
            "{\"name\":\"...\",\"description\":\"...\",\"supported_languages\":[\"python\"],"
            "\"source_code\":\"complete Python module\",\"tests_code\":\"complete pytest module\","
            "\"success_criteria\":[\"...\"],\"rationale\":\"...\"}\n\n"
            "Rules:\n"
            "1. Make the capability reusable, not a one-off hard-coded response.\n"
            "2. Implement run(context: CapabilityContext) -> CapabilityResult.\n"
            "3. Preserve unrelated behavior and fail safely when input is unsupported.\n"
            "4. Do not use network access, subprocesses, secrets, or destructive system APIs.\n"
            "5. Tests must cover success, invalid/empty input, and unsupported language when applicable.\n"
            "6. Return actual source and tests, not a description of them.\n\n"
            f"CAPABILITY ID: {capability_id}\nLANGUAGE: {language}\n\nGAP:\n{gap}\n\n"
            f"EXISTING CAPABILITIES:\n{json.dumps(existing_capabilities, ensure_ascii=False, default=str)}\n\n"
            f"OBSERVATIONS:\n{json.dumps(observations, ensure_ascii=False, default=str)}"
        )
        try:
            raw = self.llm.query(code="", instruction=prompt, model=self.model, temperature=0.0)
            data = self._parse(raw)
            source = self._require_source(data.get("source_code", ""))
            tests = self._require_tests(data.get("tests_code", ""))
        except (LLMQueryError, ValueError, SyntaxError, TypeError) as exc:
            raise RuntimeError(f"AI capability design failed: {exc}") from exc
        supported = data.get("supported_languages") or [language]
        if not isinstance(supported, list) or not supported:
            supported = [language]
        return AICapabilityDesign(
            name=str(data.get("name") or f"AI Generated {capability_id}"),
            description=str(data.get("description") or gap),
            entry_point=f"capabilities.generated.{capability_id.lower().replace('-', '_')}.capability.run",
            supported_languages=[str(item).lower() for item in supported],
            source_code=source,
            tests_code=tests,
            success_criteria=[str(item) for item in (data.get("success_criteria") or [])],
            rationale=str(data.get("rationale") or "Brain designed a reusable capability for the observed gap."),
        )


__all__ = ["AICapabilityDesign", "AICapabilityDesigner"]
