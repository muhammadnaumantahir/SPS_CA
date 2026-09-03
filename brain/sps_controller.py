"""Closed-loop SPS Brain controller.

The controller keeps the Brain responsible for strategy, reflection, and
replanning while deterministic subsystems remain the enforcement boundaries.
"""
from __future__ import annotations

import ast
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
    """AI controller that chooses SPS strategy and reflects after observations."""

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
        for candidate in (text,):
            try:
                value, _ = decoder.raw_decode(candidate)
                if isinstance(value, dict):
                    return value
            except json.JSONDecodeError:
                pass
            start = candidate.find("{")
            while start >= 0:
                try:
                    value, _ = decoder.raw_decode(candidate[start:])
                    if isinstance(value, dict):
                        return value
                except json.JSONDecodeError:
                    pass
                start = candidate.find("{", start + 1)
        raise ValueError("Brain returned invalid decision JSON")

    def decide(self, *, goal: str, current_code: str, task_plan: dict[str, Any], capabilities: list[dict[str, Any]], observations: list[dict[str, Any]], iteration: int) -> SPSDecision:
        prompt = (
            "You are the autonomous SPS Brain controller. Decide what the system should do NEXT to satisfy the user goal.\n"
            "The controller is allowed to reuse existing capabilities, compose them, adapt them, improve them, create a new capability through Layer 8 Evolution, replan after failure, or finish.\n"
            "Never claim work that has not happened. Never bypass validation, governance, Software DNA, or controlled execution.\n"
            "Return JSON only: {\"strategy\":\"reuse|compose|adapt|improve|create|replan|finish\",\"reason\":\"...\",\"task_instruction\":\"...\",\"success_criteria\":[\"...\"],\"max_iterations\":5}\n\n"
            f"GOAL:\n{goal}\n\nCURRENT CODE:\n{current_code}\n\nCURRENT TASK PLAN:\n{json.dumps(task_plan, ensure_ascii=False, default=str)}\n\n"
            f"AVAILABLE CAPABILITIES:\n{json.dumps(capabilities, ensure_ascii=False, default=str)}\n\nOBSERVATIONS SO FAR:\n{json.dumps(observations, ensure_ascii=False, default=str)}\n\n"
            f"ITERATION: {iteration}\n"
        )
        try:
            raw = self.llm.query(code=current_code, instruction=prompt, model=self.model, temperature=0.0)
            data = self._parse(raw)
        except (LLMQueryError, ValueError, TypeError) as exc:
            # Conservative fallback: let the existing task plan continue.
            return SPSDecision("reuse", f"Brain controller unavailable; continue existing plan safely: {exc}", max_iterations=5)
        strategy = str(data.get("strategy", "replan")).strip().lower()
        if strategy not in STRATEGIES:
            strategy = "replan"
        try:
            max_iterations = max(1, min(10, int(data.get("max_iterations", 5))))
        except (TypeError, ValueError):
            max_iterations = 5
        criteria = data.get("success_criteria", [])
        if not isinstance(criteria, list):
            criteria = []
        return SPSDecision(
            strategy=strategy,
            reason=str(data.get("reason") or "No reason supplied."),
            task_instruction=str(data.get("task_instruction") or ""),
            success_criteria=tuple(str(item) for item in criteria),
            max_iterations=max_iterations,
        )

    def reflect(self, *, goal: str, decision: SPSDecision, observation: dict[str, Any], current_code: str, iteration: int) -> SPSDecision:
        prompt = (
            "You are the SPS Brain reflecting after one controlled execution step. Determine whether the overall goal is satisfied. "
            "If not satisfied, choose the next strategy and explain what must change. Do not invent success. Return JSON only using the same decision schema.\n\n"
            f"GOAL:\n{goal}\n\nPREVIOUS DECISION:\n{decision.__dict__}\n\nOBSERVATION:\n{json.dumps(observation, ensure_ascii=False, default=str)}\n\nCURRENT CODE:\n{current_code}\n\nITERATION: {iteration}\n"
        )
        try:
            raw = self.llm.query(code=current_code, instruction=prompt, model=self.model, temperature=0.0)
            data = self._parse(raw)
        except (LLMQueryError, ValueError, TypeError) as exc:
            status = str(observation.get("status", "")).lower()
            if status in {"completed", "success", "passed"}:
                return SPSDecision("finish", f"Conservative reflection: execution reported success. {exc}")
            return SPSDecision("replan", f"Conservative reflection after failure. {exc}")
        strategy = str(data.get("strategy", "replan")).lower()
        if strategy not in STRATEGIES:
            strategy = "replan"
        return SPSDecision(
            strategy=strategy,
            reason=str(data.get("reason") or "Reflection completed."),
            task_instruction=str(data.get("task_instruction") or ""),
            success_criteria=tuple(str(item) for item in (data.get("success_criteria") or []) if item is not None),
            max_iterations=max(1, min(10, int(data.get("max_iterations", 5)))) if str(data.get("max_iterations", "5")).isdigit() else 5,
        )
