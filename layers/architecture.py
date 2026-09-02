"""Canonical SPS-CA ten-layer architecture vocabulary.

The public architecture is intentionally independent from Python package names.
Each layer has a canonical name, purpose, and optional sub-components. The
Brain is a separate model service used by the SPS layers and is never treated
as either a layer or a capability.
"""

from __future__ import annotations

from typing import Final

# (number, canonical name, purpose, sub-components)
LAYERS = (
    (
        1,
        "Software DNA Layer",
        "Acts as the absolute source of truth, defining constraints and meta-rules that all evolution must obey.",
        ("Goals", "Policies", "Constraints", "Learning Rules", "Repair Rules", "Safety Rules", "Ethical Rules", "Evolution Rules", "Meta-Rules"),
    ),
    (
        2,
        "Governance Layer",
        "Executive gatekeeper that authorizes proposed changes against the Software DNA before deployment.",
        ("Authorization", "Evolution Approval", "Compliance Checking", "Risk Management"),
    ),
    (
        3,
        "Cognitive Layer",
        "Synthesizes goals and system state into tactical decisions, reasoning, and plans.",
        ("Goal Manager", "Reasoning Engine", "Planning Engine", "Decision Engine", "Explainability Engine"),
    ),
    (
        4,
        "Knowledge Layer",
        "Manages structured, evolving domain knowledge.",
        ("Knowledge Base", "Knowledge Acquisition Engine", "Knowledge Validation", "Knowledge Evolution"),
    ),
    (
        5,
        "Experience Layer",
        "Collects and stores feedback and runtime signals as historical memory.",
        ("Memory", "Feedback", "Monitoring", "Learning Engine"),
    ),
    (
        6,
        "Meta-Learning Layer",
        "Evaluates and improves the system's own learning process.",
        ("Learning Evaluation", "Strategy Optimization", "Learning Improvement"),
    ),
    (
        7,
        "Adaptation Layer",
        "Shifts behavior instantly by context, without modifying source code.",
        ("Context Awareness", "Personalization", "Capability Activation", "Strategy Selection"),
    ),
    (
        8,
        "Evolution Layer",
        "The engine of genuine structural self-growth.",
        ("Self-Modification", "Self-Regeneration", "Capability Preservation", "Capability Differentiation", "Capability Creation"),
    ),
    (
        9,
        "Verification & Validation Layer",
        "Screens new or mutated code in a sandbox before it reaches production.",
        ("Testing", "Simulation", "Safety Validation", "Performance Validation"),
    ),
    (
        10,
        "Execution Layer",
        "Translates validated decisions into real, observable action.",
        ("Action Executor", "Services", "APIs", "User Interaction"),
    ),
)

LAYER_NAMES: Final = {number: name for number, name, _, _ in LAYERS}
LAYER_DESCRIPTIONS: Final = {number: purpose for number, _, purpose, _ in LAYERS}
LAYER_SUBCOMPONENTS: Final = {number: list(subcomponents) for number, _, _, subcomponents in LAYERS}

# The model is a service used primarily by the Cognitive core. It is not a
# layer and is not registered as a capability. Any provider can implement it.
BRAIN = {
    "name": "SPS-CA Brain",
    "role": "reasoning, prompt analysis, planning, code generation, debugging, strategy analysis",
    "default_provider": "Ollama",
    "replaceable": True,
    "boundary": "separate model service",
}

# Capability management is a supporting subsystem, deliberately separate from
# both the Brain and the ten architectural layers.
SUPPORTING_SUBSYSTEMS = (
    "Capability Registry",
    "Capability Lineage",
    "LLM Provider Abstraction",
)


def architecture_manifest() -> dict:
    """Return a JSON-serializable public architecture manifest for UI/API use."""
    return {
        "layers": [
            {
                "number": number,
                "name": name,
                "purpose": purpose,
                "description": purpose,
                "sub_components": list(subcomponents),
            }
            for number, name, purpose, subcomponents in LAYERS
        ],
        "brain": dict(BRAIN),
        "supporting_subsystems": list(SUPPORTING_SUBSYSTEMS),
    }
