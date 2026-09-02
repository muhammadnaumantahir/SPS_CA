"""Shared local-LLM adapter used by Baseline A and Baseline B."""
from __future__ import annotations

from models.ollama.provider import DEFAULT_MODEL
from layers.layer_02_cognitive_core.llm_interface import LLMInterface


def build_local_llm(model: str = DEFAULT_MODEL):
    """Return a callable backed by the project's provider-neutral LLM interface."""
    interface = LLMInterface()

    def query(prompt: str) -> str:
        return interface.query(code="", instruction=prompt, model=model)

    return query
