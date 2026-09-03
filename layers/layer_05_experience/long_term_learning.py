"""Persistent long-term learning summaries for SPS-CA.

Raw Experience remains append-only. This store keeps compact, durable evidence
that can be loaded into later planning without replaying the entire history.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .models import Task

DEFAULT_LONG_TERM_PATH = "experience/logs/long_term_learning.json"


class LongTermLearningStore:
    """Maintain bounded, queryable summaries derived from real Experience."""

    SCHEMA_VERSION = 1

    def __init__(self, path: str | Path = DEFAULT_LONG_TERM_PATH) -> None:
        self.path = Path(path)

    def rebuild(self, tasks: Iterable[Task], *, feedback: Iterable[dict[str, Any]] = (), evolution: Iterable[dict[str, Any]] = ()) -> dict[str, Any]:
        task_list = list(tasks)
        by_capability: dict[str, dict[str, Any]] = defaultdict(lambda: {"uses": 0, "successes": 0, "failures": 0, "partial": 0, "last_used": None, "requests": []})
        failures = Counter()
        languages = Counter()
        for task in task_list:
            if task.selected_capability:
                item = by_capability[task.selected_capability]
                item["uses"] += 1
                if task.status == "success": item["successes"] += 1
                elif task.status == "failure": item["failures"] += 1
                else: item["partial"] += 1
                item["last_used"] = task.timestamp.isoformat()
                if task.user_request and len(item["requests"]) < 8:
                    item["requests"].append(task.user_request[:240])
            if task.failure_category:
                failures[task.failure_category] += 1
            if task.target_language:
                languages[task.target_language] += 1

        capability_summary = {}
        for cap_id, item in by_capability.items():
            uses = item["uses"] or 1
            capability_summary[cap_id] = {
                **item,
                "success_rate": round(item["successes"] / uses, 4),
            }

        feedback_counts = Counter(str(x.get("feedback", "")).lower() for x in feedback if x.get("feedback"))
        evolution_events = list(evolution)[-100:]
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_tasks": len(task_list),
            "overall_success_rate": round(sum(t.status == "success" for t in task_list) / len(task_list), 4) if task_list else 0.0,
            "capabilities": capability_summary,
            "failure_patterns": dict(failures),
            "languages": dict(languages),
            "feedback": dict(feedback_counts),
            "evolution_events": evolution_events,
            "recent_outcomes": [
                {"id": t.id, "status": t.status, "capability_id": t.selected_capability, "failure_category": t.failure_category, "timestamp": t.timestamp.isoformat()}
                for t in task_list[-20:]
            ],
        }
        self.save(payload)
        return payload

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"schema_version": self.SCHEMA_VERSION}
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"schema_version": self.SCHEMA_VERSION}
        return value if isinstance(value, dict) else {"schema_version": self.SCHEMA_VERSION}

    def save(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(self.path)

    def context(self, *, max_capabilities: int = 12) -> dict[str, Any]:
        data = self.load()
        caps = data.get("capabilities", {})
        ranked = sorted(caps.items(), key=lambda item: (float(item[1].get("success_rate", 0.0)), int(item[1].get("uses", 0))), reverse=True)
        return {
            "total_tasks": data.get("total_tasks", 0),
            "overall_success_rate": data.get("overall_success_rate", 0.0),
            "top_capabilities": [{"capability_id": k, **v} for k, v in ranked[:max_capabilities]],
            "failure_patterns": data.get("failure_patterns", {}),
            "feedback": data.get("feedback", {}),
            "updated_at": data.get("updated_at"),
        }


__all__ = ["DEFAULT_LONG_TERM_PATH", "LongTermLearningStore"]
