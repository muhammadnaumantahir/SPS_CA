"""Lightweight persistent chat session storage for SPS-CA."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SessionStore:
    def __init__(self, path: str | Path = "runtime/sessions.json") -> None:
        self.path = Path(path)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists(): return {"sessions": {}}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) and isinstance(data.get("sessions"), dict) else {"sessions": {}}
        except (OSError, json.JSONDecodeError): return {"sessions": {}}

    def _save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def create(self, title: str = "New chat") -> dict[str, Any]:
        session = {"id": uuid.uuid4().hex[:12], "title": title.strip() or "New chat", "created_at": self._now(),
                   "updated_at": self._now(), "conversation": [], "code": "", "filename": "main.py",
                   "detected_language": "unknown", "language_confidence": 0.0,
                   # Empty model means AUTO: the Ollama provider discovers the live model.
                   "model": ""}
        data = self._load(); data["sessions"][session["id"]] = session; self._save(data); return session

    def list(self) -> list[dict[str, Any]]:
        sessions = list(self._load()["sessions"].values()); sessions.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
        return [self._summary(item) for item in sessions]

    def get(self, session_id: str) -> dict[str, Any] | None: return self._load()["sessions"].get(session_id)

    def save(self, session_id: str, conversation: list[dict[str, str]], code: str, filename: str, language: str,
             language_confidence: float, model: str, title: str | None = None) -> dict[str, Any]:
        data = self._load(); session = data["sessions"].get(session_id)
        if session is None:
            session = self.create(title or "New chat"); data = self._load()
        session.update({"updated_at": self._now(), "conversation": conversation, "code": code,
                        "filename": filename or "main.py", "detected_language": language,
                        "language_confidence": float(language_confidence), "model": model or ""})
        if title: session["title"] = title.strip()[:80] or session["title"]
        elif session.get("title") == "New chat":
            user_turns = [m.get("content", "") for m in conversation if m.get("role") == "user"]
            if user_turns: session["title"] = user_turns[0].strip().replace("\n", " ")[:60] or "New chat"
        data["sessions"][session_id] = session; self._save(data); return session

    def delete(self, session_id: str) -> bool:
        data = self._load()
        if session_id not in data["sessions"]: return False
        del data["sessions"][session_id]; self._save(data); return True

    @staticmethod
    def _summary(session: dict[str, Any]) -> dict[str, Any]:
        messages = session.get("conversation", []); last = next((m for m in reversed(messages) if m.get("role") == "user"), None)
        return {"id": session.get("id"), "title": session.get("title", "New chat"), "created_at": session.get("created_at", ""),
                "updated_at": session.get("updated_at", ""), "message_count": len(messages), "preview": (last or {}).get("content", "")[:100],
                "detected_language": session.get("detected_language", "unknown")}
