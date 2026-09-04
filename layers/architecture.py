"""Authoritative SPS-CA ten-layer architecture vocabulary.

The ten layer names are canonical. Sub-components describe responsibilities
implemented by the corresponding layer packages. The Brain is a separate,
replaceable reasoning service and is not a layer or capability.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Final

LAYERS = (
    (1, "Software DNA Core", "Absolute source of truth for constraints and meta-rules", ("DNA Policy Rules", "Software DNA Model", "Capability Contract Templates")),
    (2, "Governance Core", "Authorizes proposed changes against Software DNA before deployment", ("Governance Gate", "Risk Assessment", "Compliance & Decision Audit")),
    (3, "Cognitive core", "Synthesizes goals and system state into reasoning, analysis, and plans", ("Cognitive Reasoning", "LLM Provider Interface", "Project Analyzer", "Cognitive Data Models")),
    (4, "Knowledge core", "Manages structured and evolving domain knowledge", ("Knowledge Core", "Knowledge Snapshot", "Knowledge Validation")),
    (5, "Experience core", "Stores runtime outcomes, feedback, and historical learning signals", ("Experience Log", "Long-Term Learning", "Experience Data Models")),
    (6, "Meta-learning core", "Evaluates and improves how the system learns", ("Capability Evaluator", "Meta-Learner", "Strategy Policy", "A/B Experimentation", "Optimization Cycle Controller")),
    (7, "Adaptation core", "Changes behavior by context without modifying source code", ("Adaptation Engine", "Adaptation Records", "Contextual Strategy Adjustment")),
    (8, "Evolution core", "Performs governed structural self-growth and capability lifecycle management", ("Controlled Evolution Engine", "Evolution Cycle", "Capability Gap Planning", "SPS Growth Decision", "Evolution Evidence", "Evolution Transaction", "Evolution Execution Authority", "Self-Programming", "Capability Retirement", "Measured Capability Improvement")),
    (9, "Verification & Validation Core", "Screens candidate changes before production execution", ("Validation Engine", "Validation Data Models", "Sandbox & Test Execution")),
    (10, "Execution Core", "Translates validated decisions into observable action", ("Execution Engine", "Execution Data Models", "Action Execution")),
)
LAYER_NAMES: Final = {n: name for n, name, _, _ in LAYERS}
LAYER_DESCRIPTIONS: Final = {n: purpose for n, _, purpose, _ in LAYERS}
LAYER_SUBCOMPONENTS: Final = {n: list(parts) for n, _, _, parts in LAYERS}
BRAIN: Final = {"name": "SPS-CA Brain", "role": "reasoning, prompt analysis, planning, code generation, debugging, strategy analysis", "default_provider": "Ollama", "replaceable": True, "boundary": "separate model service"}
SUPPORTING_SUBSYSTEMS: Final = ("Capability Registry", "Capability Lineage", "LLM Provider Abstraction")

@dataclass(frozen=True)
class LayerManifest:
    number: int
    name: str
    purpose: str
    sub_components: tuple[str, ...]

    @property
    def description(self) -> str:
        return self.purpose


def architecture_manifest() -> dict:
    return {
        "layers": [{"number": n, "name": name, "purpose": purpose, "description": purpose, "sub_components": list(parts)} for n, name, purpose, parts in LAYERS],
        "brain": dict(BRAIN),
        "supporting_subsystems": list(SUPPORTING_SUBSYSTEMS),
    }


LAYER_MANIFEST: Final = tuple(
    LayerManifest(number=n, name=name, purpose=purpose, sub_components=tuple(parts))
    for n, name, purpose, parts in LAYERS
)


def get_layer(number: int) -> LayerManifest:
    for layer in LAYER_MANIFEST:
        if layer.number == number:
            return layer
    raise KeyError(f"Unknown SPS layer: {number}")
