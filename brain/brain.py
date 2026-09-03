"""SPS-CA Brain: replaceable model intelligence with intent-safe capability planning."""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from capabilities.canonical import CANONICAL_BY_ID, INTENT_CLASSES, capability_ids_for_intent
from layers.layer_03_cognitive.llm_interface import LLMInterface, LLMQueryError

_CODE_FENCE_RE = re.compile(r"```([\w+#.-]*)\s*\n([\s\S]*?)```", re.MULTILINE)

_SYSTEM_PROMPT = """You are the AI Brain of SPS-CA, a governed self-programming coding assistant.
The Brain provides intelligence for the SPS architecture. It is NOT a capability,
does NOT execute code, and does NOT directly apply source changes.

First classify the user's request intent. Then choose capabilities only from the
intent-eligible catalog supplied below. Return JSON only:
{
  "language": "python|java|javascript|typescript|go|csharp|cpp|rust|unknown",
  "language_confidence": 0.0,
  "intent_class": "code_generation|code_modification|analysis|bug_diagnosis|bug_fixing|refactoring|test_generation|documentation|validation|project_operations|mixed|unknown",
  "intent": "short description of what the user actually wants",
  "reasoning": "brief reasoning summary",
  "steps": [{"capability_id": "CAP-NNN", "reason": "why this capability is needed"}]
}

Rules:
1. Select only IDs in the supplied eligible capability catalog.
2. Never invent a capability.
3. Test Generation is forbidden for a request whose intent is code generation, modification, analysis, diagnosis, fixing, refactoring, documentation, validation, or project operations.
4. Prefer the smallest set of capabilities that satisfies the request.
5. Preserve the user's intent exactly.
6. Treat the supplied source as the current working state.
7. Do not add tests merely because code was generated or changed.
8. The Brain itself must never be represented as CAP-NNN.
"""


class BrainError(Exception):
    """Raised when the Brain cannot safely produce a plan."""


@dataclass(frozen=True)
class BrainPlan:
    intent: str
    reasoning: str
    steps: list[dict[str, str]] = field(default_factory=list)
    provider: str = "Ollama"
    model: str = ""
    language: str = "unknown"
    language_confidence: float = 0.0
    intent_class: str = "unknown"

    def as_dict(self) -> dict[str, Any]:
        return {
            "brain": {"provider": self.provider, "model": self.model},
            "language": self.language,
            "language_confidence": self.language_confidence,
            "intent_class": self.intent_class,
            "intent": self.intent,
            "reasoning": self.reasoning,
            "steps": list(self.steps),
        }


class Brain:
    """Provider-neutral reasoning Brain used by SPS-CA's Cognitive Layer."""

    SUPPORTED = ("python", "java", "javascript", "typescript", "go", "csharp", "cpp", "rust")
    EXTENSIONS = {
        "py": "python", "pyw": "python", "java": "java", "js": "javascript", "jsx": "javascript",
        "ts": "typescript", "tsx": "typescript", "go": "go", "cs": "csharp", "cpp": "cpp",
        "cc": "cpp", "cxx": "cpp", "rs": "rust",
    }

    def __init__(self, provider: Optional[Any] = None, model: str = "", timeout_seconds: float = 120.0) -> None:
        self.provider = provider
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.llm = LLMInterface(provider=provider, timeout_seconds=timeout_seconds)

    @property
    def provider_name(self) -> str:
        return type(self.llm.provider).__name__.replace("Provider", "")

    def is_available(self) -> bool:
        return self.llm.is_available()

    @classmethod
    def detect_language(cls, code: str, request: str = "", filename: str = "") -> tuple[str, float, str]:
        text = code or ""
        fenced = _CODE_FENCE_RE.findall(request or "")
        if not text and fenced:
            tagged = fenced[0][0].lower()
            if tagged in cls.SUPPORTED:
                return tagged, 0.99, "explicit fenced-code language tag in prompt"
            text = "\n".join(block for _, block in fenced)
        checks = {
            "python": [r"\bdef\s+\w+\s*\(", r"\bimport\s+\w+", r"\bfrom\s+\w+\s+import\b", r"if\s+__name__\s*=="],
            "javascript": [r"\b(const|let|var)\s+\w+", r"=>\s*[{(]", r"console\.log\s*\("],
            "typescript": [r":\s*(string|number|boolean|unknown|any)(\[\])?\b", r"\binterface\s+\w+", r"\btype\s+\w+\s*="],
            "java": [r"\bpublic\s+class\s+\w+", r"\bpublic\s+static\s+void\s+main\b", r"System\.out\.print"],
            "go": [r"\bpackage\s+\w+", r"\bfunc\s+\w+\s*\(", r"fmt\.Print"],
            "csharp": [r"\busing\s+System\b", r"\bnamespace\s+\w+", r"\bpublic\s+(class|interface)\s+\w+"],
            "cpp": [r"#include\s*<iostream>", r"\bstd::\w+", r"\bint\s+main\s*\("],
            "rust": [r"\bfn\s+main\s*\(", r"\blet\s+mut\b", r"println!\s*!?\s*\("],
        }
        scores = {lang: sum(bool(re.search(pattern, text, re.MULTILINE)) for pattern in patterns) for lang, patterns in checks.items()}
        best = max(scores, key=scores.get) if scores else "unknown"
        score = scores.get(best, 0)
        if score > 0:
            return best, min(0.95, 0.68 + 0.08 * (score - 1)), f"code syntax ({score} matching signal{'s' if score != 1 else ''})"
        name = (filename or "").lower()
        if "." in name:
            ext = name.rsplit(".", 1)[-1]
            if ext in cls.EXTENSIONS:
                return cls.EXTENSIONS[ext], 0.82, f"filename .{ext}"
        req = (request or "").lower()
        for lang in cls.SUPPORTED:
            if re.search(rf"\b{re.escape(lang)}\b", req):
                return lang, 0.70, "language mentioned in request"
        return "unknown", 0.25, "insufficient concrete language evidence"

    @staticmethod
    def infer_intent_class(request: str, code: str = "", file_path: str = "") -> str:
        """Classify task intent before capability selection."""
        req = " ".join((request or "").lower().split())
        has_code = bool((code or "").strip())
        if not req:
            return "unknown"
        if re.search(r"\b(generate|write|create|add|make)\b.*\b(test|tests|pytest|unit tests?)\b", req) or re.search(r"\b(generate|write|create)\s+(pytest|unit tests?)\b", req):
            return "test_generation"
        if re.search(r"\b(fix|repair|resolve)\b.*\b(bug|error|issue|exception|failure)\b", req):
            return "bug_fixing"
        if re.search(r"\b(find|detect|diagnos|debug|identify)\w*\b.*\b(bug|error|issue|exception|failure)\b", req):
            return "bug_diagnosis"
        if re.search(r"\b(refactor|optimi[sz]e|cleanup|clean up|improve performance)\b", req):
            return "refactoring"
        if re.search(r"\b(document|documentation|docstring|docstrings|comments?|readme)\b", req):
            return "documentation"
        if has_code and re.search(r"\b(add|change|modify|update|extend|implement|replace|remove|insert|delete)\b", req):
            return "code_modification"
        if re.search(r"\b(validate|validation|review|check syntax|check correctness|code quality|security review)\b", req):
            return "validation"
        if re.search(r"\b(create|add|delete|remove|move|rename)\b.*\b(file|folder|directory|project|module|package)\b", req) or "project structure" in req:
            return "project_operations"
        if re.search(r"\b(explain|explanation|analy[sz]e|understand|what does|how does)\b", req):
            return "analysis"
        if re.search(r"\b(write|create|build|generate|make|develop|implement)\b.*\b(code|program|script|application|app|function|calculator|solution)\b", req) and not has_code:
            return "code_generation"
        if re.search(r"\b(write|create|build|generate|make|develop|implement)\b.*\b(code|program|script|application|app|function|calculator|solution)\b", req):
            return "code_generation"
        if re.search(r"\b(add|change|modify|update|extend|implement|replace|remove)\b", req) and has_code:
            return "code_modification"
        return "unknown"

    @staticmethod
    def _enriched_catalog(capability_catalog: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        by_id = {str(item.get("id")): dict(item) for item in capability_catalog if item.get("id")}
        for cid, canonical in CANONICAL_BY_ID.items():
            if cid in by_id:
                merged = dict(canonical)
                merged.update(by_id[cid])
                by_id[cid] = merged
        return by_id

    @staticmethod
    def _parse_planning_response(raw: Any) -> dict[str, Any]:
        """Parse strict JSON plus common local-LLM formatting variants safely.

        Local models sometimes return a Python-dict representation with single
        quotes or wrap JSON in prose/fences. We first attempt strict JSON and
        then use ast.literal_eval (never eval) on balanced object candidates.
        """
        text = str(raw or "").strip()
        if not text:
            raise ValueError("model returned an empty response")

        candidates: list[str] = [text]
        candidates.extend(block for _, block in _CODE_FENCE_RE.findall(text))
        decoder = json.JSONDecoder()
        for source in candidates:
            source = source.strip()
            try:
                value, _ = decoder.raw_decode(source)
                if isinstance(value, dict):
                    return value
            except json.JSONDecodeError:
                pass
            for index, char in enumerate(source):
                if char != "{":
                    continue
                try:
                    value, _ = decoder.raw_decode(source[index:])
                    if isinstance(value, dict):
                        return value
                except json.JSONDecodeError:
                    pass
                try:
                    value = ast.literal_eval(source[index:])
                    if isinstance(value, dict):
                        return value
                except (SyntaxError, ValueError, TypeError):
                    continue
        raise ValueError("model did not return a valid JSON object")

    def plan(
        self,
        *,
        request: str,
        code: str,
        language: str,
        file_path: str,
        capability_catalog: list[dict[str, Any]],
        conversation: Optional[list[dict[str, str]]] = None,
        knowledge_context: Optional[dict[str, Any]] = None,
        experience_context: Optional[list[dict[str, Any]]] = None,
    ) -> BrainPlan:
        request = request.strip()
        if not request:
            raise BrainError("Brain requires a non-empty request.")
        if not capability_catalog:
            raise BrainError("Brain received an empty capability catalog.")
        inferred_language, inferred_confidence, inferred_evidence = self.detect_language(code, request, file_path)
        intent_class = self.infer_intent_class(request, code, file_path)
        enriched = self._enriched_catalog(capability_catalog)
        eligible_ids = set(capability_ids_for_intent(intent_class)) if intent_class != "unknown" else set(enriched)
        eligible = [enriched[cid] for cid in enriched if cid in eligible_ids]
        if not eligible:
            raise BrainError(f"No active capability is eligible for intent '{intent_class}'.")
        history = list(conversation or [])[-12:]
        experience = list(experience_context or [])[-8:]
        prompt = (
            f"{_SYSTEM_PROMPT}\n\nPRELIMINARY LANGUAGE EVIDENCE: {inferred_language} ({inferred_confidence:.2f}) — {inferred_evidence}\n"
            f"CLASSIFIED INTENT: {intent_class}\nTARGET FILE: {file_path}\n"
            f"CONVERSATION HISTORY:\n{json.dumps(history, ensure_ascii=False)}\n"
            f"RELEVANT SPS EXPERIENCE:\n{json.dumps(experience, ensure_ascii=False) if experience else '(none)'}\n"
            f"SPS KNOWLEDGE:\n{json.dumps(knowledge_context or {}, ensure_ascii=False)}\n\n"
            f"LATEST USER REQUEST:\n{request}\n\nCURRENT WORKING SOURCE:\n{code}\n\n"
            f"INTENT-ELIGIBLE CAPABILITIES:\n{json.dumps(eligible, ensure_ascii=False)}"
        )
        try:
            raw = self.llm.query(code=code, instruction=prompt, model=self.model, temperature=0.0)
        except LLMQueryError as exc:
            raise BrainError(str(exc)) from exc
        try:
            data = self._parse_planning_response(raw)
        except (ValueError, TypeError) as exc:
            raise BrainError(f"Brain returned invalid planning JSON: {exc}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("steps", []), list):
            raise BrainError("Brain returned an invalid plan structure.")
        valid_ids = set(enriched)
        steps: list[dict[str, str]] = []
        for step in data.get("steps", []):
            if not isinstance(step, dict):
                raise BrainError("Brain returned a malformed plan step.")
            cid = str(step.get("capability_id", ""))
            if cid not in valid_ids:
                raise BrainError(f"Brain selected unavailable capability: {cid or '<empty>'}")
            if cid in eligible_ids:
                steps.append({"capability_id": cid, "reason": str(step.get("reason", ""))})
        if intent_class not in {"unknown", "mixed"}:
            primary = capability_ids_for_intent(intent_class)[0]
            if not steps or all(step["capability_id"] != primary for step in steps):
                steps = [{"capability_id": primary, "reason": f"intent eligibility enforcement for '{intent_class}'"}]
            else:
                steps = [step for step in steps if step["capability_id"] == primary]
        elif not steps and eligible:
            steps = [{"capability_id": eligible[0]["id"], "reason": "first eligible capability after Brain planning"}]
        model_language = str(data.get("language") or inferred_language).lower()
        if model_language not in self.SUPPORTED and model_language != "unknown":
            model_language = inferred_language
        try:
            confidence = float(data.get("language_confidence", inferred_confidence))
        except (TypeError, ValueError):
            confidence = inferred_confidence
        confidence = max(0.0, min(1.0, confidence))
        return BrainPlan(
            intent=str(data.get("intent") or request),
            reasoning=str(data.get("reasoning") or "Intent classified and eligible capabilities selected."),
            steps=steps,
            provider=self.provider_name,
            model=self.model,
            language=model_language,
            language_confidence=confidence,
            intent_class=intent_class,
        )
