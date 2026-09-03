"""AI Brain task decomposition and result composition for compound requests."""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from capabilities.canonical import CANONICAL_BY_ID, capability_ids_for_intent
from layers.layer_03_cognitive.llm_interface import LLMInterface, LLMQueryError

_CODE_FENCE_RE = re.compile(r"```(?:[\\w+#.-]+)?\\s*\\n([\\s\\S]*?)```", re.MULTILINE)

_INTENTS = {
    "code_generation", "code_modification", "analysis", "bug_diagnosis", "bug_fixing",
    "refactoring", "test_generation", "documentation", "validation", "project_operations",
}

_PLANNER_PROMPT = """You are the planning/orchestration Brain of SPS-CA.
The Brain is the AI orchestrator. It must decompose a compound user request into the smallest useful ordered tasks,
assign exactly one canonical capability to each task, and express dependencies between tasks.

Return JSON only:
{
  "intent_class": "mixed|one of the canonical intent classes",
  "intent": "what the user wants overall",
  "reasoning": "brief planning rationale",
  "tasks": [
    {
      "id": "task_001",
      "instruction": "self-contained instruction for this task",
      "intent_class": "analysis|bug_diagnosis|bug_fixing|...",
      "capability_id": "CAP-NNN",
      "depends_on": ["task_000"]
    }
  ]
}

Planning rules:
1. For compound requests, create one task per distinct action. Example: "Analyze this function, then fix the bug" MUST become analysis first, then bug fixing.
2. Preserve the user's ordering when the wording establishes ordering.
3. A later task must depend on the earlier task when it needs that task's output.
4. Each task gets exactly one capability ID from the supplied catalog.
5. Do not invent capabilities. Do not create test tasks unless the user explicitly asks for tests.
6. Do not collapse multiple requested actions into a single generic capability.
7. A task instruction must tell the capability exactly what to do and may refer to dependency results.
8. The Brain plans; capabilities execute. The Brain never directly edits source code.
"""


@dataclass(frozen=True)
class BrainTask:
    id: str
    instruction: str
    intent_class: str
    capability_id: str
    depends_on: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "instruction": self.instruction,
            "intent_class": self.intent_class,
            "capability_id": self.capability_id,
            "depends_on": list(self.depends_on),
        }


@dataclass(frozen=True)
class BrainTaskPlan:
    intent: str
    reasoning: str
    intent_class: str
    tasks: list[BrainTask]
    provider: str
    model: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "brain": {"provider": self.provider, "model": self.model},
            "intent_class": self.intent_class,
            "intent": self.intent,
            "reasoning": self.reasoning,
            "tasks": [task.as_dict() for task in self.tasks],
        }


class BrainTaskPlanner:
    """Uses the same local/replaceable LLM as Brain to plan and compose workflows."""

    def __init__(self, *, provider: Optional[Any] = None, model: str = "", timeout_seconds: Optional[float] = 120.0) -> None:
        self.llm = LLMInterface(provider=provider, timeout_seconds=timeout_seconds)
        self.model = model

    @property
    def provider_name(self) -> str:
        return type(self.llm.provider).__name__.replace("Provider", "")

    @staticmethod
    def _parse(raw: str) -> dict[str, Any]:
        text = str(raw or "").strip()
        if not text:
            raise ValueError("empty model response")
        candidates = [text] + [block for block in _CODE_FENCE_RE.findall(text)]
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
        raise ValueError("model did not return a JSON object")

    @staticmethod
    def _validate(data: dict[str, Any], *, allowed_ids: set[str]) -> list[BrainTask]:
        raw_tasks = data.get("tasks")
        if not isinstance(raw_tasks, list) or not raw_tasks:
            raise ValueError("Brain must return at least one task")
        tasks: list[BrainTask] = []
        seen: set[str] = set()
        for raw in raw_tasks:
            if not isinstance(raw, dict):
                raise ValueError("malformed Brain task")
            task_id = str(raw.get("id", "")).strip()
            instruction = str(raw.get("instruction", "")).strip()
            intent = str(raw.get("intent_class", "")).strip()
            capability_id = str(raw.get("capability_id", "")).strip()
            deps = raw.get("depends_on", [])
            if not task_id or task_id in seen or not instruction:
                raise ValueError("Brain task IDs must be unique and instructions non-empty")
            if intent not in _INTENTS:
                raise ValueError(f"Unsupported task intent: {intent or '<empty>'}")
            if capability_id not in allowed_ids:
                raise ValueError(f"Brain selected unavailable capability: {capability_id or '<empty>'}")
            eligible = set(capability_ids_for_intent(intent))
            if capability_id not in eligible:
                raise ValueError(f"Capability {capability_id} is not eligible for intent {intent}")
            if not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps):
                raise ValueError(f"Invalid dependencies for {task_id}")
            seen.add(task_id)
            tasks.append(BrainTask(task_id, instruction, intent, capability_id, list(dict.fromkeys(deps))))
        ids = {task.id for task in tasks}
        for task in tasks:
            if task.id in task.depends_on or any(dep not in ids for dep in task.depends_on):
                raise ValueError(f"Invalid dependency graph for {task.id}")
        # Require dependencies to reference an earlier task; this preserves the
        # Brain's ordered workflow and prevents accidental cyclic plans.
        index = {task.id: pos for pos, task in enumerate(tasks)}
        for task in tasks:
            if any(index[dep] >= index[task.id] for dep in task.depends_on):
                raise ValueError(f"Dependency must refer to an earlier task: {task.id}")
        return tasks

    def plan(
        self,
        *,
        request: str,
        code: str,
        language: str,
        file_path: str,
        capability_catalog: list[dict[str, Any]],
        intent_class: str,
    ) -> BrainTaskPlan:
        allowed = {str(item.get("id")) for item in capability_catalog if isinstance(item, dict) and item.get("id")}
        prompt = (
            f"{_PLANNER_PROMPT}\n\n"
            f"CLASSIFIED OVERALL INTENT: {intent_class}\nLANGUAGE: {language}\nTARGET FILE: {file_path}\n"
            f"LATEST USER REQUEST:\n{request}\n\nCURRENT WORKING SOURCE:\n{code}\n\n"
            f"AVAILABLE CAPABILITIES:\n{json.dumps([CANONICAL_BY_ID[cid] for cid in sorted(allowed) if cid in CANONICAL_BY_ID], ensure_ascii=False)}"
        )
        try:
            raw = self.llm.query(code=code, instruction=prompt, model=self.model, temperature=0.0)
            data = self._parse(raw)
            tasks = self._validate(data, allowed_ids=allowed)
        except (LLMQueryError, ValueError, TypeError) as exc:
            raise RuntimeError(f"Brain task planning failed: {exc}") from exc
        return BrainTaskPlan(
            intent=str(data.get("intent") or request),
            reasoning=str(data.get("reasoning") or "Brain decomposed the request into capability tasks."),
            intent_class=str(data.get("intent_class") or intent_class),
            tasks=tasks,
            provider=self.provider_name,
            model=self.model,
        )

    def compose_results(self, *, request: str, original_code: str, final_code: str, task_results: list[dict[str, Any]]) -> str:
        """Ask the Brain to turn ordered capability outputs into the user-facing result."""
        prompt = (
            "You are the SPS-CA Brain composing the final response from executed capability results. "
            "Do not invent work that did not happen. Summarize what was done, preserve important findings, "
            "and state the final code status clearly.\n\n"
            f"USER REQUEST:\n{request}\n\nORIGINAL CODE:\n{original_code}\n\nFINAL CODE:\n{final_code}\n\n"
            f"EXECUTED TASK RESULTS:\n{json.dumps(task_results, ensure_ascii=False, default=str)}"
        )
        try:
            return str(self.llm.query(code=final_code, instruction=prompt, model=self.model, temperature=0.0)).strip()
        except LLMQueryError:
            completed = [f"{item.get('task_id')}: {item.get('summary') or item.get('error') or 'completed'}" for item in task_results]
            return "\n".join(completed)
