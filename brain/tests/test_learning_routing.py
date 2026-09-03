"""Phase 2 integration tests for evidence-aware Brain routing."""

from __future__ import annotations

import json

from brain import Brain
from models.base import LLMResponse


class FakeProvider:
    def __init__(self, text: str) -> None:
        self.text = text

    def is_available(self) -> bool:
        return True

    def generate(self, request):
        return LLMResponse(text=self.text, model=request.model, provider="fake")


def test_evidence_qualified_generated_capability_can_replace_seeded_default():
    response = json.dumps({
        "language": "python",
        "language_confidence": 0.95,
        "intent_class": "code_modification",
        "intent": "add validation",
        "reasoning": "explicit source modification requested",
        "steps": [{"capability_id": "CAP-002", "reason": "canonical default"}],
    })
    experience = [
        {"id": "a1", "user_request": "modify code", "status": "failure", "selected_capability": "CAP-002", "target_language": "python", "target_project": "chat", "outcome": "failed", "time_taken_seconds": 5},
        {"id": "a2", "user_request": "modify code", "status": "failure", "selected_capability": "CAP-002", "target_language": "python", "target_project": "chat", "outcome": "failed", "time_taken_seconds": 5},
        {"id": "a3", "user_request": "modify code", "status": "failure", "selected_capability": "CAP-002", "target_language": "python", "target_project": "chat", "outcome": "failed", "time_taken_seconds": 5},
        {"id": "b1", "user_request": "modify code", "status": "success", "selected_capability": "CAP-011", "target_language": "python", "target_project": "chat", "outcome": "success", "time_taken_seconds": 1},
        {"id": "b2", "user_request": "modify code", "status": "success", "selected_capability": "CAP-011", "target_language": "python", "target_project": "chat", "outcome": "success", "time_taken_seconds": 1},
        {"id": "b3", "user_request": "modify code", "status": "success", "selected_capability": "CAP-011", "target_language": "python", "target_project": "chat", "outcome": "success", "time_taken_seconds": 1},
    ]
    catalog = [
        {"id": "CAP-002", "name": "Code Modification", "status": "active"},
        {
            "id": "CAP-011",
            "name": "Generated Safe Modification",
            "status": "active",
            "generated": True,
            "intent_class": "code_modification",
            "allowed_intents": ["code_modification"],
            "forbidden_intents": ["test_generation"],
        },
    ]

    brain = Brain(provider=FakeProvider(response), model="test-model")
    plan = brain.plan(
        request="Add input validation to this function",
        code="def add(a, b):\n    return a + b\n",
        language="python",
        file_path="main.py",
        capability_catalog=catalog,
        experience_context=experience,
    )

    assert plan.intent_class == "code_modification"
    assert plan.steps[0]["capability_id"] == "CAP-011"
    assert "Layer 6 evidence recommended CAP-011" in plan.reasoning
