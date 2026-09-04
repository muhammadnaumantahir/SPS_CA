from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from layers.layer_08_evolution.growth_decision import GrowthDecisionEngine
from layers.capability_registry.models import CapabilityType
from layers.capability_registry.registry import CapabilityRegistryManager

ROOT = Path(__file__).resolve().parents[2]
EVENTS_PATH = ROOT / "runtime" / "evolution_events.json"


class EvolutionEvidenceStore:
    """Persistent evidence ledger for explainable Layer-8 decisions."""
    def __init__(self, path: str | Path = EVENTS_PATH, registry_path: str | Path = ROOT / "capabilities" / "registry.json") -> None:
        self.path = Path(path)
        self.registry = CapabilityRegistryManager(str(registry_path))
        self.growth_decision = GrowthDecisionEngine()

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def _save(self, events: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(events, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _next_id(events: list[dict[str, Any]]) -> str:
        return f"EVOL-{len(events) + 1:05d}"

    def record_agreement(self, *, session_id, turn_id, request, language, capability_id="", code=""):
        events = self._load()
        evidence = {
            "event_id": self._next_id(events), "event_type": "agreement", "timestamp": self._now(),
            "session_id": session_id, "turn_id": turn_id, "request": request, "language": language,
            "capability_id": capability_id, "code_length": len(code or ""),
            "evidence_summary": f"User accepted the result for {capability_id or 'the current turn'}; retained as positive reuse evidence.",
            "decision": "retain", "reasoning": "Positive feedback strengthens confidence in the selected behavior but does not justify creating a new capability.",
        }
        events.append(evidence); self._save(events); return evidence

    def record_disagreement(self, *, session_id, turn_id, request, language, language_confidence, previous_capability_id, code=""):
        events = self._load()
        same_cap = [e for e in events if e.get("event_type") == "disagreement" and e.get("previous_capability_id") == previous_capability_id]
        count = len(same_cap) + 1
        evidence = {
            "event_id": self._next_id(events), "event_type": "disagreement", "timestamp": self._now(),
            "session_id": session_id, "turn_id": turn_id, "request": request, "language": language,
            "language_confidence": language_confidence, "previous_capability_id": previous_capability_id,
            "disagreement_count": count, "failure_pattern": self._failure_pattern(request, code),
            "evidence_summary": self._evidence_summary(previous_capability_id, count),
        }
        events.append(evidence); self._save(events); return evidence

    def analyze(self, event):
        """Make an explicit SPS Growth Decision from scored evidence."""
        count = int(event.get("disagreement_count") or 0)
        parent = event.get("previous_capability_id") or ""
        pattern = bool(event.get("failure_pattern"))
        decision = self.growth_decision.decide(
            existing_capability_id=parent,
            disagreement_count=count,
            capability_match=bool(parent),
            repeated_pattern=count >= 3 and pattern,
            adaptation_viable=count == 2,
            composition_viable=False,
            improvement_viable=False,
            capability_fitness=event.get("capability_fitness"),
            recurrence=event.get("recurrence_score"),
            adaptation_viability=event.get("adaptation_viability"),
            improvement_viability=event.get("improvement_viability"),
            composition_viability=event.get("composition_viability"),
            creation_need=event.get("creation_need"),
            confidence=event.get("confidence_score"),
            regression_risk=event.get("regression_risk"),
            evidence={"source_event_id": event.get("event_id", ""), "failure_pattern_detected": pattern},
        )
        events = self._load()
        result = dict(event)
        result.update({
            "decision": decision.decision.value, "reason_code": decision.reason_code, "reasoning": decision.reasoning,
            "growth_decision": {"decision": decision.decision.value, "reason_code": decision.reason_code, "reasoning": decision.reasoning, "evidence": decision.evidence, "scores": decision.scores},
            "validation_status": "pending" if decision.decision.value == "create" else "not_applicable",
            "event_type": "evolution_analysis", "event_id": self._next_id(events), "timestamp": self._now(),
        })
        events.append(result); self._save(events); return result

    def record_creation(self, analysis):
        events = self._load()
        existing = [int(c.id.split("-")[-1]) for c in self.registry.list_all_capabilities() if c.id.startswith("CAP-") and c.id.split("-")[-1].isdigit()]
        next_num = max([10, *existing]) + 1
        cap_id = f"CAP-{next_num:03d}"
        parent = analysis.get("previous_capability_id") or None
        name = self._capability_name(analysis.get("request", ""), parent, cap_id)
        provenance = {
            "decision": "create", "created_at": self._now(), "parent_capability_id": parent,
            "trigger_event_ids": [analysis.get("event_id", "")], "reasoning": analysis.get("reasoning", ""),
            "reason_code": analysis.get("reason_code", "capability_gap"), "evidence_summary": analysis.get("evidence_summary", ""),
            "validation_status": "registered", "source_request": analysis.get("request", ""),
        }
        metadata = {
            "id": cap_id, "name": name, "description": f"Generated reusable skill for the repeated pattern: {analysis.get('failure_pattern', 'observed user requirement')}",
            "type": CapabilityType.MODIFICATION.value, "entry_point": "capabilities.generated.evolved_runtime.run",
            "supported_languages": [analysis.get("language") or "python"], "version": "1.0.0", "created_date": self._now(),
            "last_modified": self._now(), "generated": True, "origin": "capability_evolution",
            "failure_pattern": analysis.get("failure_pattern"), "trigger_tasks": [str(analysis.get("session_id", ""))],
            "reuse_count": 0, "test_coverage": 0.0, "status": "active", "canonical": False,
            "extra_metadata": {"provenance": provenance, "tags": ["evolved", "explainable"], "decision_scores": analysis.get("growth_decision", {}).get("scores", {})},
        }
        self.registry.register_from_dict(metadata)
        creation = dict(analysis)
        creation.update({"event_type": "capability_created", "event_id": self._next_id(events), "timestamp": self._now(), "created_capability_id": cap_id, "validation_status": "registered", "capability_name": name, "provenance": provenance})
        events.append(creation); self._save(events); return creation

    def list_events(self, limit=100):
        return self._load()[-max(1, limit):][::-1]

    def get_capability_lineage(self, capability_id):
        capability = self.registry.get_capability(capability_id)
        events = self._load()
        related = [e for e in events if e.get("created_capability_id") == capability_id]
        provenance = ((capability.extra_metadata or {}).get("provenance") if capability else None) or {}
        if not provenance and related:
            created = related[-1]
            provenance = dict(created.get("provenance") or {})
            provenance.setdefault("decision", "create"); provenance.setdefault("created_at", created.get("timestamp"))
            provenance.setdefault("parent_capability_id", created.get("previous_capability_id") or None)
            provenance.setdefault("trigger_event_ids", [created.get("event_id", "")]); provenance.setdefault("reasoning", created.get("reasoning", ""))
            provenance.setdefault("evidence_summary", created.get("evidence_summary", "")); provenance.setdefault("validation_status", created.get("validation_status", "registered"))
            provenance.setdefault("source_request", created.get("request", ""))
        return {"capability": capability.to_dict() if capability else None, "provenance": provenance, "events": related, "parent": provenance.get("parent_capability_id")}

    @staticmethod
    def _failure_pattern(request, code):
        text = f"{request} {code}".lower()
        keywords = [("parameter", "parameterized test/behavior pattern"), ("async", "asynchronous code pattern"), ("validation", "input validation pattern"), ("type", "type-handling pattern"), ("exception", "exception-handling pattern"), ("test", "test-generation pattern")]
        for token, label in keywords:
            if token in text: return label
        return "repeated unmet user requirement"

    @staticmethod
    def _evidence_summary(capability_id, count):
        return f"{count} disagreement(s) associated with {capability_id or 'no capability'} were observed; evidence is accumulated before structural evolution."

    @staticmethod
    def _capability_name(request, parent, cap_id):
        words = [w.strip(".,:;!?\"'") for w in request.split() if w.strip()]
        title = " ".join(words[:5]).title() if words else "Evolved Coding Skill"
        return f"{title} ({cap_id})"
