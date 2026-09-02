"""Layer 5: Adaptation.

``Adaptation`` reuses existing capabilities across tasks and languages by
adjusting their runtime parameters (timeout, aggressiveness, language),
rather than generating new capabilities. This is always a Type 6 change
(Change Type Taxonomy, Section 11) — it never triggers Layer 8 (Evolution).

Sandbox execution proper belongs to Layer 6 (Validation) and
``execution/`` (controlled execution infrastructure). ``test_adaptation``
here is a lightweight pre-check Layer 5 can run on its own before handing
an adapted capability off to validation — it is intentionally conservative
about what it claims to verify.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from layers.layer_03_experience.models import Task

from .models import AdaptationRecord

DEFAULT_ADAPTATIONS_PATH = "experience/logs/adaptations.json"
DEFAULT_TIMEOUT_SECONDS = 5.0
# Compiled/statically-typed target languages tend to need longer capability
# timeouts than interpreted ones (compilation step, slower toolchains).
SLOWER_LANGUAGES = {"java", "csharp", "go"}
SLOW_LANGUAGE_TIMEOUT_SECONDS = 15.0
DEFAULT_SIMILARITY_THRESHOLD = 0.3


class Adaptation:
    """Reuses capabilities across tasks by adjusting parameters, not code."""

    def can_reuse_capability(
        self,
        current_task: Task,
        past_task: Task,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ) -> bool:
        """True if ``past_task``'s capability looks reusable for ``current_task``.

        A past task is only a candidate for reuse if it succeeded. Beyond
        that, this checks semantic similarity between the two requests using
        word-overlap (Jaccard similarity) rather than embeddings/an LLM
        call — SPS-CA's only LLM is the local Ollama model (Section 9),
        and this check needs to be fast and deterministic enough to run
        for every task before deciding whether a full LLM query is even
        needed.
        """
        if past_task.status != "success" or not past_task.selected_capability:
            return False

        current_words = self._tokenize(current_task.user_request)
        past_words = self._tokenize(past_task.user_request)
        if not current_words or not past_words:
            return False

        intersection = current_words & past_words
        union = current_words | past_words
        similarity = len(intersection) / len(union) if union else 0.0
        return similarity >= similarity_threshold

    def adjust_parameters(
        self,
        capability_params: Dict[str, object],
        task_context: Dict[str, object],
    ) -> Tuple[Dict[str, object], Dict[str, str]]:
        """Return ``(adjusted_params, parameters_changed)``.

        ``parameters_changed`` maps each changed key to a human-readable
        ``"old -> new"`` string, ready to drop into an
        :class:`~.models.AdaptationRecord`.
        """
        adjusted = dict(capability_params)
        changes: Dict[str, str] = {}

        target_language = task_context.get("target_language")
        if target_language:
            old_language = adjusted.get("language")
            if old_language != target_language:
                changes["language"] = f"{old_language} -> {target_language}"
                adjusted["language"] = target_language

            if target_language in SLOWER_LANGUAGES:
                raw_timeout = adjusted.get(
                    "timeout_seconds", DEFAULT_TIMEOUT_SECONDS
                )  # type: ignore[arg-type]
                old_timeout = float(raw_timeout)  # type: ignore[arg-type]
                new_timeout = max(old_timeout, SLOW_LANGUAGE_TIMEOUT_SECONDS)
                if new_timeout != old_timeout:
                    changes["timeout_seconds"] = f"{old_timeout}s -> {new_timeout}s"
                    adjusted["timeout_seconds"] = new_timeout

        if task_context.get("complex", False):
            old_aggressiveness = adjusted.get("aggressiveness", "normal")
            if old_aggressiveness != "conservative":
                changes["aggressiveness"] = f"{old_aggressiveness} -> conservative"
                adjusted["aggressiveness"] = "conservative"

        return adjusted, changes

    def test_adaptation(
        self, adapted_params: Dict[str, object], target_code: str
    ) -> bool:
        """Lightweight pre-check that an adapted capability is plausible to run.

        This is *not* a substitute for Layer 6 (Validation)'s sandboxed
        regression testing — it only rejects adaptations that are
        obviously unusable (no code to operate on, non-positive timeout)
        before any real execution is attempted.
        """
        if not target_code or not target_code.strip():
            return False
        timeout = adapted_params.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)
        try:
            timeout_value = float(timeout)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return False
        return timeout_value > 0

    def adapt_and_record(
        self,
        record_id: str,
        base_capability_id: str,
        capability_params: Dict[str, object],
        task_context: Dict[str, object],
        target_code: str,
        applied_to_task_id: str = "",
    ) -> Tuple[Dict[str, object], AdaptationRecord]:
        """Run adjust_parameters + test_adaptation and package the result.

        Convenience method combining the individual steps into the single
        :class:`AdaptationRecord` the design's ``adaptation_NNN`` JSON
        format expects, so callers don't have to wire the three steps
        together themselves.
        """
        adjusted, changes = self.adjust_parameters(capability_params, task_context)
        success = self.test_adaptation(adjusted, target_code)
        record = AdaptationRecord(
            id=record_id,
            base_capability_id=base_capability_id,
            applied_to_task_id=applied_to_task_id,
            parameters_changed=changes,
            success=success,
        )
        return adjusted, record

    @staticmethod
    def _tokenize(text: str) -> set:
        return {
            w.strip(".,!?:;()[]").lower() for w in text.split() if w.strip(".,!?:;()[]")
        }


class AdaptationLog:
    """Append-only, persisted history of :class:`AdaptationRecord` records."""

    def __init__(self, records: Optional[List[AdaptationRecord]] = None) -> None:
        self.records: List[AdaptationRecord] = list(records) if records else []

    def add_record(self, record: AdaptationRecord) -> None:
        self.records.append(record)

    def save_to_json(self, path: Union[str, Path] = DEFAULT_ADAPTATIONS_PATH) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {r.id: r.to_dict() for r in self.records}
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load_from_json(
        cls, path: Union[str, Path] = DEFAULT_ADAPTATIONS_PATH
    ) -> "AdaptationLog":
        path = Path(path)
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        records = [AdaptationRecord.from_dict(r) for r in data.values()]
        return cls(records)
