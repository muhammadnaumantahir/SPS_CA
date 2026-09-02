from __future__ import annotations

import json
from pathlib import Path

from models.base import LLMResponse
from core.assistant_service import SpsAssistantService


class FakeProvider:
    name = "test-provider"

    def __init__(self, payload: dict):
        self.payload = payload

    def is_available(self):
        return True

    def generate(self, request):
        return LLMResponse(
            text=json.dumps(self.payload),
            model=request.model or "test-model",
            provider=self.name,
        )


def test_conversational_turn_uses_brain_and_persists_experience(tmp_path: Path):
    registry = Path("capabilities/registry.json")
    experience = tmp_path / "experience.json"
    provider = FakeProvider({
        "intent": "inspect code for a bug",
        "reasoning": "The task asks for analysis.",
        "steps": [{"capability_id": "CAP-001", "reason": "bug analysis requested"}],
    })
    service = SpsAssistantService(
        registry_path=str(registry),
        experience_path=str(experience),
        provider=provider,
        model="test-model",
    )

    turn = service.run_turn(
        request="Please find the bug.",
        code="def add(a,b):\n    return a-b\n",
        language="python",
        filename="main.py",
    )

    assert turn.success is True
    assert turn.steps[0]["capability_id"] == "CAP-001"
    assert turn.learning_context["experience_count"] == 0
    saved = json.loads(experience.read_text(encoding="utf-8"))
    assert saved["tasks"][0]["user_request"] == "Please find the bug."


def test_follow_up_turn_includes_previous_conversation(tmp_path: Path):
    provider = FakeProvider({
        "intent": "inspect current code",
        "reasoning": "Follow-up request uses the current working context.",
        "steps": [],
    })
    service = SpsAssistantService(
        registry_path="capabilities/registry.json",
        experience_path=str(tmp_path / "experience.json"),
        provider=provider,
        model="test-model",
    )
    conversation = [
        {"role": "user", "content": "Add validation."},
        {"role": "assistant", "content": "Done."},
    ]
    turn = service.run_turn(
        request="Also handle negative values.",
        code="def f(x):\n    return x\n",
        language="python",
        filename="main.py",
        conversation=conversation,
    )
    assert turn.success is True
    assert turn.conversation[-2]["content"] == "Also handle negative values."
