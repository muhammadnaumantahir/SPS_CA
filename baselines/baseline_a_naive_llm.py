"""Baseline A: naive LLM with no tools, learning, or capability reuse."""
from __future__ import annotations

import time
from typing import Callable

from baselines.runner import BaselineResult, BaselineRunner

class BaselineA_NaiveLLM(BaselineRunner):
    baseline_id = "baseline_a_naive_llm"

    def __init__(self, llm: Callable[[str], str], model: str = "qwen2.5-coder:7b", store=None) -> None:
        super().__init__(llm=llm, model=model, store=store)

    def process_request(self, user_request: str, project_context: str, project: str = "unknown") -> BaselineResult:
        prompt = (
            "You are a naive coding assistant. Return the best direct answer to the user's request. "
            "Do not use tools, do not claim to have executed code, and do not invent test results.\n\n"
            f"USER REQUEST:\n{user_request}\n\nPROJECT CONTEXT:\n{project_context}"
        )
        started = time.perf_counter()
        response = self.llm(prompt)
        result = BaselineResult(
            baseline_id=self.baseline_id,
            user_request=user_request,
            project=project,
            model=self.model,
            response=response,
            duration_seconds=time.perf_counter() - started,
        )
        if self.store:
            self.store.append(result)
        return result
