"""Persistent, append-only research trace for SPS-CA evolution.

The supervisor-facing prototype needs to explain not only *what* code changed,
but also why the system selected a capability, why a new capability was
needed, what was created, when it happened, and how the resulting stage
changed. This module provides that audit trail without coupling it to the CLI
or any particular LLM provider.

Two JSON artifacts are maintained under the supplied root directory:

* ``evolution_history.json`` -- scenario records.
* ``stage_state.json`` -- current stage/scenario counters.

The records are intentionally structured as research data rather than free-
form logs so that later analysis can compare Stage 0 .. Stage N scenarios.
"""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_TRACE_DIR = "experience/traces"
DEFAULT_HISTORY_PATH = f"{DEFAULT_TRACE_DIR}/evolution_history.json"
DEFAULT_STAGE_PATH = f"{DEFAULT_TRACE_DIR}/stage_state.json"


class EvolutionTraceStore:
    """Persist supervisor/research trace records and the current SPS stage."""

    SCHEMA_VERSION = "1.0"

    def __init__(
        self,
        history_path: str | Path = DEFAULT_HISTORY_PATH,
        stage_path: str | Path = DEFAULT_STAGE_PATH,
    ) -> None:
        self.history_path = Path(history_path)
        self.stage_path = Path(stage_path)
        self._lock = threading.RLock()
        self._ensure_files()

    def current_stage(self) -> int:
        """Return the current SPS stage, defaulting to Stage 0."""
        with self._lock:
            return int(self._load_stage_state().get("current_stage", 0))

    def next_scenario_id(self) -> str:
        """Return the next deterministic scenario id (SC-001, SC-002, ...)."""
        with self._lock:
            number = int(self._load_stage_state().get("next_scenario_number", 1))
            return f"SC-{number:03d}"

    def start_scenario(
        self,
        *,
        user_request: str,
        code: str = "",
        language: str = "unknown",
        file_path: str = "",
        scenario_id: Optional[str] = None,
        stage: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a scenario-start record and reserve its id.

        Source text is represented by a SHA-256 hash and length. The raw code
        stays outside the trace unless a later storage policy explicitly keeps
        source snapshots.
        """
        if not user_request.strip():
            raise ValueError("user_request must be non-empty")

        with self._lock:
            state = self._load_stage_state()
            scenario_id = scenario_id or f"SC-{int(state['next_scenario_number']):03d}"
            stage = self.current_stage() if stage is None else int(stage)
            now = datetime.now(timezone.utc).isoformat()

            from hashlib import sha256

            record = {
                "schema_version": self.SCHEMA_VERSION,
                "trace_id": str(uuid.uuid4()),
                "scenario_id": scenario_id,
                "stage_before": stage,
                "stage_after": stage,
                "status": "started",
                "timestamp_start": now,
                "timestamp_end": None,
                "user_request": user_request,
                "input": {
                    "language": language,
                    "file_path": file_path,
                    "code_sha256": sha256(code.encode("utf-8")).hexdigest() if code else None,
                    "code_length": len(code),
                },
                "analysis": {},
                "capability_search": {},
                "capability_generation": {},
                "modification": {},
                "validation": {},
                "governance": {},
                "result": {},
                "metadata": dict(metadata or {}),
                "events": [],
            }

            self._append_history(record)
            state["next_scenario_number"] = self._next_number_after(scenario_id)
            state["last_scenario_id"] = scenario_id
            state["updated_at"] = now
            self._save_stage_state(state)
            return record

    def complete_scenario(
        self,
        scenario_id: str,
        *,
        stage_after: Optional[int] = None,
        status: str = "completed",
        analysis: Optional[Dict[str, Any]] = None,
        capability_search: Optional[Dict[str, Any]] = None,
        capability_generation: Optional[Dict[str, Any]] = None,
        modification: Optional[Dict[str, Any]] = None,
        validation: Optional[Dict[str, Any]] = None,
        governance: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Complete the most recent record matching ``scenario_id``."""
        with self._lock:
            records = self._load_history()
            index = self._find_record_index(records, scenario_id)
            if index is None:
                raise KeyError(f"Unknown scenario: {scenario_id}")

            record = records[index]
            if analysis is not None:
                record["analysis"] = dict(analysis)
            if capability_search is not None:
                record["capability_search"] = dict(capability_search)
            if capability_generation is not None:
                record["capability_generation"] = dict(capability_generation)
            if modification is not None:
                record["modification"] = dict(modification)
            if validation is not None:
                record["validation"] = dict(validation)
            if governance is not None:
                record["governance"] = dict(governance)
            if result is not None:
                record["result"] = dict(result)
            if metadata is not None:
                record.setdefault("metadata", {}).update(metadata)

            final_stage = int(record.get("stage_before", 0)) if stage_after is None else int(stage_after)
            record["stage_after"] = final_stage
            record["status"] = status
            record["timestamp_end"] = datetime.now(timezone.utc).isoformat()
            self._save_history(records)

            state = self._load_stage_state()
            state["current_stage"] = final_stage
            state["last_scenario_id"] = scenario_id
            state["updated_at"] = record["timestamp_end"]
            self._save_stage_state(state)
            return record

    def append_event(
        self,
        scenario_id: str,
        event: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append a timestamped event to a scenario's trace."""
        if not event.strip():
            raise ValueError("event must be non-empty")
        with self._lock:
            records = self._load_history()
            index = self._find_record_index(records, scenario_id)
            if index is None:
                raise KeyError(f"Unknown scenario: {scenario_id}")
            records[index].setdefault("events", []).append(
                {
                    "event_id": str(uuid.uuid4()),
                    "event": event,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": dict(details or {}),
                }
            )
            self._save_history(records)

    def list_records(self, *, stage: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return trace records, optionally filtered by stage-before."""
        records = self._load_history()
        if stage is None:
            return records
        target_stage = int(stage)
        return [record for record in records if int(record.get("stage_before", 0)) == target_stage]

    def save_stage(self, stage: int) -> int:
        """Set the current SPS stage explicitly and return it."""
        if stage < 0:
            raise ValueError("stage must be >= 0")
        with self._lock:
            state = self._load_stage_state()
            state["current_stage"] = int(stage)
            state["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._save_stage_state(state)
        return int(stage)

    def _append_history(self, record: Dict[str, Any]) -> None:
        records = self._load_history()
        records.append(record)
        self._save_history(records)

    def _ensure_files(self) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.stage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_path.exists():
            self._save_history([])
        if not self.stage_path.exists():
            self._save_stage_state(
                {
                    "schema_version": self.SCHEMA_VERSION,
                    "current_stage": 0,
                    "next_scenario_number": 1,
                    "last_scenario_id": None,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            )

    def _load_history(self) -> List[Dict[str, Any]]:
        try:
            data = json.loads(self.history_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return data if isinstance(data, list) else []

    def _save_history(self, records: Iterable[Dict[str, Any]]) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        payload = list(records)
        self.history_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )

    def _load_stage_state(self) -> Dict[str, Any]:
        try:
            data = json.loads(self.stage_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        return {
            "schema_version": self.SCHEMA_VERSION,
            "current_stage": int(data.get("current_stage", 0)),
            "next_scenario_number": int(data.get("next_scenario_number", 1)),
            "last_scenario_id": data.get("last_scenario_id"),
            "updated_at": data.get("updated_at"),
        }

    def _save_stage_state(self, state: Dict[str, Any]) -> None:
        self.stage_path.parent.mkdir(parents=True, exist_ok=True)
        self.stage_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _find_record_index(records: List[Dict[str, Any]], scenario_id: str) -> Optional[int]:
        for index in range(len(records) - 1, -1, -1):
            if records[index].get("scenario_id") == scenario_id:
                return index
        return None

    @staticmethod
    def _next_number_after(scenario_id: str) -> int:
        try:
            return int(scenario_id.split("-", 1)[1]) + 1
        except (IndexError, ValueError):
            return 1
