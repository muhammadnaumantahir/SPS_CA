"""Durable execution-memory sub-component for Layer 5 Experience."""
from __future__ import annotations

import uuid
from pathlib import Path

from .experience_log import ExperienceLog
from .models import Task

DEFAULT_EXECUTION_EXPERIENCE_PATH = "experience/logs/experience_log.json"


class ExecutionExperienceStore:
    """Record and retrieve real execution outcomes through the Layer 5 log."""

    def __init__(self, path: str | Path = DEFAULT_EXECUTION_EXPERIENCE_PATH) -> None:
        self.path = Path(path)

    def load(self) -> ExperienceLog:
        return ExperienceLog.load_from_json(self.path)

    def record_execution(
        self,
        *,
        request: str,
        language: str,
        status: str,
        capability_id: str = "",
        outcome: str = "",
        failure_category: str | None = None,
        time_taken_seconds: float = 0.0,
        source: str = "",
        scenario_id: str = "",
        run_id: str = "",
        feedback: str = "",
        error: str | None = None,
        metadata: dict | None = None,
        target_project: str = "sps_workspace",
    ) -> Task:
        task = Task(
            id=f"exec_{uuid.uuid4().hex}",
            user_request=request,
            target_project=target_project,
            target_language=language,
            status=status,  # type: ignore[arg-type]
            selected_capability=capability_id,
            outcome=outcome,
            failure_category=failure_category,
            time_taken_seconds=float(time_taken_seconds or 0.0),
            source=source,
            scenario_id=scenario_id,
            run_id=run_id,
            feedback=feedback,
            error=error,
            metadata=dict(metadata or {}),
        )
        log = self.load()
        log.add_task(task)
        log.save_to_json(self.path)
        return task

    def find_relevant(
        self,
        request: str,
        *,
        capability_id: str = "",
        language: str = "",
        limit: int = 12,
    ) -> list[Task]:
        log = self.load()
        query_tokens = {token for token in request.lower().split() if len(token) > 2}
        ranked: list[tuple[int, Task]] = []
        for task in log.tasks:
            if capability_id and task.selected_capability != capability_id:
                continue
            if language and task.target_language.lower() != language.lower():
                continue
            text_tokens = set(task.user_request.lower().split())
            overlap = len(query_tokens & text_tokens)
            if overlap:
                ranked.append((overlap, task))
        ranked.sort(key=lambda item: (-item[0], item[1].timestamp), reverse=False)
        return [task for _, task in ranked[: max(1, limit)]]

    def capability_evidence(self, capability_id: str, *, language: str = "") -> dict[str, float | int]:
        history = self.find_relevant("", capability_id=capability_id, language=language, limit=10000)
        # Empty query intentionally bypasses token filtering here.
        if not history:
            log = self.load()
            history = [
                task for task in log.tasks
                if task.selected_capability == capability_id
                and (not language or task.target_language.lower() == language.lower())
            ]
        uses = len(history)
        failures = sum(task.status == "failure" for task in history)
        successes = sum(task.status == "success" for task in history)
        return {
            "uses": uses,
            "failures": failures,
            "successes": successes,
            "success_rate": (successes / uses) if uses else 0.0,
            "failure_rate": (failures / uses) if uses else 0.0,
        }


__all__ = ["DEFAULT_EXECUTION_EXPERIENCE_PATH", "ExecutionExperienceStore"]
