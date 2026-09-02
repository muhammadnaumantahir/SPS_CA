"""Shared execution and result contract for Phase 9 baseline agents."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

DEFAULT_MODEL = "qwen2.5-coder:7b"

@dataclass
class BaselineResult:
    baseline_id: str
    user_request: str
    project: str
    model: str
    response: str
    tool_calls: list[str] = field(default_factory=list)
    retries: int = 0
    duration_seconds: float = 0.0
    tests_passed: bool | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class ResultStore:
    """Append-only JSONL store suitable for Phase 10 experiment records."""
    def __init__(self, path: str | Path = "evaluation/baselines/results.jsonl") -> None:
        self.path = Path(path)

    def append(self, result: BaselineResult) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result.to_dict(), sort_keys=True) + "\n")

class BaselineRunner:
    """Shared wrapper contract for Baseline A and Baseline B."""
    baseline_id = "base"

    def __init__(self, llm: Callable[[str], str], model: str = DEFAULT_MODEL, store: ResultStore | None = None) -> None:
        self.llm = llm
        self.model = model
        self.store = store

    def process_request(self, user_request: str, project_context: str, project: str = "unknown") -> BaselineResult:
        raise NotImplementedError
