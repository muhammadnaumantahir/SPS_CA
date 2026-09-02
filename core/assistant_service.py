"""Shared conversational coding-assistant service for SPS-CA.

This module keeps request/session orchestration out of the web UI and CLI.
The Brain remains a separate AI service; capabilities remain executable SPS
skills; experience is persisted as evidence for later learning layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Optional

from brain import Brain, BrainError
from capabilities.base import CapabilityContext
from capabilities.seed_registry import load_entry_point
from layers.architecture import architecture_manifest
from layers.layer_03_experience import ExperienceLog, Task
from layers.layer_09_capability_registry import CapabilityRegistryManager


@dataclass
class AssistantTurn:
    """Structured result returned to every SPS-CA interface."""

    intent: str = ""
    reasoning: str = ""
    assistant_message: str = ""
    steps: list[dict[str, str]] = field(default_factory=list)
    capability_results: list[dict[str, Any]] = field(default_factory=list)
    output_code: str = ""
    original_code: str = ""
    diff: str = ""
    layers: list[dict[str, Any]] = field(default_factory=list)
    brain: dict[str, str] = field(default_factory=dict)
    conversation: list[dict[str, str]] = field(default_factory=list)
    success: bool = False
    error: Optional[str] = None
    elapsed_ms: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "reasoning": self.reasoning,
            "assistant_message": self.assistant_message,
            "steps": self.steps,
            "capability_results": self.capability_results,
            "output_code": self.output_code,
            "original_code": self.original_code,
            "diff": self.diff,
            "layers": self.layers,
            "brain": self.brain,
            "conversation": self.conversation,
            "success": self.success,
            "error": self.error,
            "elapsed_ms": round(self.elapsed_ms, 2),
        }


class SpsAssistantService:
    """Orchestrates a conversational coding turn using the SPS boundaries."""

    def __init__(
        self,
        *,
        registry_path: str = "capabilities/registry.json",
        experience_path: str = "experience/logs/experience_log.json",
        provider: Optional[Any] = None,
        model: str = "",
        timeout_seconds: float = 120.0,
    ) -> None:
        self.registry = CapabilityRegistryManager(registry_path)
        self.experience = ExperienceLog.load_from_json(experience_path)
        self.experience_path = experience_path
        self.brain = Brain(provider=provider, model=model, timeout_seconds=timeout_seconds)
        self.timeout_seconds = timeout_seconds

    def capability_catalog(self) -> list[dict[str, Any]]:
        return [
            {
                "id": cap.id,
                "name": cap.name,
                "description": cap.description,
                "version": cap.version,
                "generated": bool(cap.generated),
                "tags": list(getattr(cap, "tags", []) or []),
            }
            for cap in self.registry.list_all_capabilities()
            if cap.status == "active"
        ]

    def run_turn(
        self,
        *,
        request: str,
        code: str,
        language: str,
        filename: str,
        conversation: Optional[list[dict[str, str]]] = None,
    ) -> AssistantTurn:
        start = perf_counter()
        original = code
        history = list(conversation or [])[-12:]
        base = self._base_layers()
        try:
            plan = self.brain.plan(
                request=request,
                code=code,
                language=language,
                file_path=filename,
                capability_catalog=self.capability_catalog(),
                conversation=history,
            )
            current = code
            results: list[dict[str, Any]] = []

            for step in plan.steps:
                template = next(
                    (cap for cap in self.registry.list_all_capabilities() if cap.id == step["capability_id"]),
                    None,
                )
                if template is None or template.status != "active":
                    raise BrainError(f"Brain selected unavailable capability: {step['capability_id']}")

                result = load_entry_point(template)(
                    CapabilityContext(
                        code=current,
                        language=language,
                        file_path=filename,
                        project_path="",
                        parameters={
                            "llm_provider": self.brain.llm.provider,
                            "llm_model": self.brain.model,
                            "llm_timeout_seconds": self.timeout_seconds,
                        },
                        metadata={
                            "request": request,
                            "brain_reason": step.get("reason", ""),
                            "conversation": history,
                        },
                    )
                )
                results.append(
                    {
                        "id": template.id,
                        "capability_id": template.id,
                        "name": template.name,
                        "status": "completed" if result.success else "failed",
                        "summary": result.summary,
                        "error": result.error,
                        "reason": step.get("reason", ""),
                    }
                )
                if not result.success:
                    break
                if result.modified_code is not None:
                    current = result.modified_code

            changed = current != original
            success = all(item["status"] == "completed" for item in results) if results else True
            selected = results[-1]["id"] if results else ""
            assistant_message = self._assistant_message(plan.intent, plan.reasoning, results, changed)
            updated_conversation = [
                *history,
                {"role": "user", "content": request},
                {"role": "assistant", "content": assistant_message},
            ]

            self._record_experience(
                request=request,
                language=language,
                selected_capability=selected,
                success=success,
                outcome=assistant_message,
                elapsed=perf_counter() - start,
            )
            layers = self._completed_layers(base, results, changed)
            return AssistantTurn(
                intent=plan.intent,
                reasoning=plan.reasoning,
                assistant_message=assistant_message,
                steps=list(plan.steps),
                capability_results=results,
                output_code=current,
                original_code=original,
                diff=self._diff(original, current, filename),
                layers=layers,
                brain={"provider": plan.provider, "model": plan.model},
                conversation=updated_conversation,
                success=success,
                error=(results[-1]["error"] if results and not success else None),
                elapsed_ms=(perf_counter() - start) * 1000.0,
            )
        except BrainError as exc:
            message = f"I could not safely plan this turn: {exc}"
            self._record_experience(
                request=request,
                language=language,
                selected_capability="",
                success=False,
                outcome=message,
                elapsed=perf_counter() - start,
                failure_category="BrainPlanningError",
            )
            return AssistantTurn(
                original_code=original,
                output_code=original,
                layers=self._failed_layers(base),
                brain={"provider": self.brain.provider_name, "model": self.brain.model},
                conversation=[*history, {"role": "user", "content": request}],
                success=False,
                error=str(exc),
                assistant_message=message,
                elapsed_ms=(perf_counter() - start) * 1000.0,
            )

    def _record_experience(
        self,
        *,
        request: str,
        language: str,
        selected_capability: str,
        success: bool,
        outcome: str,
        elapsed: float,
        failure_category: Optional[str] = None,
    ) -> None:
        next_id = f"chat_{len(self.experience.tasks) + 1:05d}"
        self.experience.add_task(
            Task(
                id=next_id,
                user_request=request,
                target_project="web-chat",
                target_language=language,
                status="success" if success else "failure",
                selected_capability=selected_capability,
                outcome=outcome,
                failure_category=failure_category,
                time_taken_seconds=elapsed,
            )
        )
        self.experience.save_to_json(self.experience_path)

    @staticmethod
    def _assistant_message(
        intent: str,
        reasoning: str,
        results: list[dict[str, Any]],
        changed: bool,
    ) -> str:
        failed = next((r for r in results if r["status"] == "failed"), None)
        if failed:
            return f"I analyzed the request but {failed['name']} could not complete it. {failed.get('error') or ''}".strip()
        names = ", ".join(r["name"] for r in results if r.get("name"))
        if changed and names:
            return f"Done. I applied {names.lower()} to the current working code. {reasoning or intent}".strip()
        if names:
            return f"I analyzed the request with {names.lower()}. {reasoning or intent}".strip()
        return reasoning or intent or "I analyzed the request and no capability change was required."

    @staticmethod
    def _diff(before: str, after: str, filename: str) -> str:
        import difflib

        return "".join(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                fromfile=f"a/{filename}",
                tofile=f"b/{filename}",
            )
        )

    @staticmethod
    def _base_layers() -> list[dict[str, Any]]:
        return [dict(layer, status="ready") for layer in architecture_manifest()["layers"]]

    @staticmethod
    def _completed_layers(base: list[dict[str, Any]], results: list[dict[str, Any]], changed: bool) -> list[dict[str, Any]]:
        status = {
            1: "constraints loaded",
            2: "policy context checked",
            3: "reasoned by Brain",
            4: "knowledge context used",
            5: "experience recorded",
            6: "learning evidence available",
            7: "adaptation context evaluated",
            8: "evolution opportunity evaluated",
            9: "verification preview complete" if changed else "verification ready",
            10: "execution boundary ready",
        }
        for layer in base:
            layer["status"] = status[layer["number"]]
        if results and any(r["status"] == "failed" for r in results):
            base[8]["status"] = "verification blocked by capability failure"
        return base

    @staticmethod
    def _failed_layers(base: list[dict[str, Any]]) -> list[dict[str, Any]]:
        status = {1: "constraints loaded", 2: "policy context checked", 3: "Brain blocked"}
        for layer in base:
            layer["status"] = status.get(layer["number"], "waiting")
        return base
