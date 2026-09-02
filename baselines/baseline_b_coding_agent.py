"""Baseline B: tool-augmented coding agent without SPS learning."""
from __future__ import annotations

import time
from typing import Callable

from baselines.runner import BaselineResult, BaselineRunner

class BaselineB_CodingAgent(BaselineRunner):
    baseline_id = "baseline_b_coding_agent"

    def __init__(
        self,
        llm: Callable[[str], str],
        model: str = "qwen2.5-coder:7b",
        store=None,
        tools: dict[str, Callable[[str], str]] | None = None,
    ) -> None:
        super().__init__(llm=llm, model=model, store=store)
        self.tool_registry = tools or {
            "analyze_code": self.analyze_code,
            "syntax_check": self.syntax_check,
            "run_tests": self.run_tests,
        }

    @staticmethod
    def analyze_code(project_context: str) -> str:
        return f"Project contains {len(project_context.splitlines())} context lines."

    @staticmethod
    def syntax_check(project_context: str) -> str:
        return "not_run: language-specific syntax checker is supplied by the target-project adapter"

    @staticmethod
    def run_tests(project_context: str) -> str:
        return "not_run: target-project test command must be supplied by the experiment harness"

    def process_request(self, user_request: str, project_context: str, project: str = "unknown") -> BaselineResult:
        started = time.perf_counter()
        tool_calls: list[str] = []
        analysis = self.tool_registry["analyze_code"](project_context)
        tool_calls.append("analyze_code")
        syntax = self.tool_registry["syntax_check"](project_context)
        tool_calls.append("syntax_check")
        tests = self.tool_registry["run_tests"](project_context)
        tool_calls.append("run_tests")
        prompt = (
            "You are a tool-augmented coding assistant. Use the supplied tool findings to answer the user. "
            "Do not invent execution results, learning, or reusable capabilities.\n\n"
            f"USER REQUEST:\n{user_request}\n\nPROJECT CONTEXT:\n{project_context}\n\n"
            f"TOOL FINDINGS:\n{analysis}\n{syntax}\n{tests}"
        )
        retries = 0
        response = self.llm(prompt)
        result = BaselineResult(
            baseline_id=self.baseline_id,
            user_request=user_request,
            project=project,
            model=self.model,
            response=response,
            tool_calls=tool_calls,
            retries=retries,
            duration_seconds=time.perf_counter() - started,
        )
        if self.store:
            self.store.append(result)
        return result
