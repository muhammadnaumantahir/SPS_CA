"""Closed-loop SPS Brain controller.

The Brain decides strategy, observes outcomes, reflects, and can request
replanning or Layer-8 capability creation. Deterministic SPS layers remain the
safety and enforcement boundaries.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

from layers.layer_03_cognitive_core.llm_interface import LLMInterface, LLMQueryError


STRATEGIES = {"reuse", "compose", "adapt", "improve", "create", "replan", "finish"}


@dataclass(frozen=True)
class SPSDecision:
    strategy: str
    reason: str
    task_instruction: str = ""
    success_criteria: tuple[str, ...] = ()
    max_iterations: int = 5


class SPSBrainController:
    """AI controller for strategy selection and closed-loop reflection."""

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
        start = text.find("{")
        while start >= 0:
            try:
                value, _ = decoder.raw_decode(text[start:])
                if isinstance(value, dict):
                    return value
            except json.JSONDecodeError:
                start = text.find("{", start + 1)
                continue
            start = text.find("{", start + 1)
        raise ValueError("Brain returned invalid decision JSON")

    def _query(self, prompt: str, code: str) -> dict[str, Any]:
        try:
            raw = self.llm.query(code=code, instruction=prompt, model=self.model, temperature=0.0)
            return self._parse(raw)
        except (LLMQueryError, ValueError, TypeError) as exc:
            raise RuntimeError(f"Brain decision failed: {exc}") from exc

    @staticmethod
    def _decision(data: dict[str, Any], default_strategy: str = "replan") -> SPSDecision:
        strategy = str(data.get("strategy") or default_strategy).strip().lower()
        if strategy not in STRATEGIES:
            strategy = default_strategy if default_strategy in STRATEGIES else "replan"
        try:
            maximum = max(1, min(10, int(data.get("max_iterations", 5))))
        except (TypeError, ValueError):
            maximum = 5
        criteria = data.get("success_criteria", [])
        if not isinstance(criteria, list):
            criteria = []
        return SPSDecision(
            strategy=strategy,
            reason=str(data.get("reason") or "No reason supplied."),
            task_instruction=str(data.get("task_instruction") or ""),
            success_criteria=tuple(str(item) for item in criteria),
            max_iterations=maximum,
        )

    def decide(self, *, goal: str, current_code: str, task_plan: dict[str, Any], capabilities: list[dict[str, Any]], observations: list[dict[str, Any]], iteration: int) -> SPSDecision:
        prompt = (
            "You are the autonomous SPS Brain controller. Decide what the system should do NEXT to satisfy the user's goal.\n"
            "Choose exactly one strategy: reuse (use existing capability), compose (coordinate multiple existing capabilities), "
            "adapt (change execution approach/context), improve (improve an existing capability), create (ask Layer 8 to create a new reusable capability), "
            "replan (discard/replace the current plan after evidence), or finish (the overall goal is proven satisfied).\n"
            "The Brain controls strategy but never bypasses Validation, Governance, Software DNA, or ExecutionEngine.\n"
            "Never choose finish merely because one task succeeded. Check the overall goal, success criteria, and remaining work.\n"
            "Return JSON only: {\"strategy\":\"reuse|compose|adapt|improve|create|replan|finish\",\"reason\":\"...\",\"task_instruction\":\"...\",\"success_criteria\":[\"...\"],\"max_iterations\":5}\n\n"
            f"GOAL:\n{goal}\n\nCURRENT CODE:\n{current_code}\n\nCURRENT PLAN:\n{json.dumps(task_plan, ensure_ascii=False, default=str)}\n\n"
            f"AVAILABLE CAPABILITIES:\n{json.dumps(capabilities, ensure_ascii=False, default=str)}\n\n"
            f"OBSERVATIONS:\n{json.dumps(observations, ensure_ascii=False, default=str)}\n\nITERATION: {iteration}\n"
        )
        try:
            return self._decision(self._query(prompt, current_code), default_strategy="replan")
        except RuntimeError as exc:
            return SPSDecision("reuse", f"Brain controller unavailable; preserve the current safe plan. {exc}", max_iterations=5)

    def reflect(self, *, goal: str, decision: SPSDecision, observation: dict[str, Any], current_code: str, remaining_tasks: list[dict[str, Any]], iteration: int) -> SPSDecision:
        prompt = (
            "You are the SPS Brain reflecting after a controlled step. Determine whether the USER GOAL is now satisfied. "
            "Remaining tasks are unfinished work unless evidence proves they are unnecessary. Do not invent success. "
            "If the current approach failed or cannot satisfy the goal, select replan/adapt/improve/create/compose/reuse. "
            "Return JSON only using the standard decision schema.\n\n"
            f"GOAL:\n{goal}\n\nPREVIOUS DECISION:\n{decision.__dict__}\n\nOBSERVATION:\n{json.dumps(observation, ensure_ascii=False, default=str)}\n\n"
            f"CURRENT CODE:\n{current_code}\n\nREMAINING TASKS:\n{json.dumps(remaining_tasks, ensure_ascii=False, default=str)}\n\nITERATION: {iteration}\n"
        )
        try:
            return self._decision(self._query(prompt, current_code), default_strategy="replan")
        except RuntimeError as exc:
            status = str(observation.get("status", "")).lower()
            if not remaining_tasks and status in {"completed", "success", "passed"}:
                return SPSDecision("finish", f"Conservative reflection accepted the successful final observation. {exc}")
            return SPSDecision("replan", f"Conservative reflection requested replanning after an incomplete/failed observation. {exc}")
