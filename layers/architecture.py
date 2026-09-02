"""Canonical SPS-CA ten-layer architecture vocabulary.

These names are the public architectural model. Existing Python package paths
remain stable for compatibility; this manifest prevents implementation path
names from redefining the research architecture.
"""

from __future__ import annotations

LAYERS = (
    (1, "Software DNA layer", "Identity, invariants, constraints and seed-system rules."),
    (2, "Governance layer", "Policy, risk, approval/rejection and audit decisions."),
    (3, "Cognitive core", "Prompt understanding, reasoning, planning and code context."),
    (4, "Knowledge core", "Structured knowledge about code, capabilities, patterns and system state."),
    (5, "Experience core", "Persistent outcomes, failures, successes, traces and lessons."),
    (6, "Meta-learning core", "Learning which strategies and capabilities work across scenarios."),
    (7, "Adaptation core", "Context-sensitive strategy adjustment and capability composition."),
    (8, "Evolution core", "Design and generation of new/improved SPS capabilities."),
    (9, "Verification & Validation", "Syntax, tests, regression, sandbox and evidence checks."),
    (10, "Execution layer", "Controlled application of approved changes and tool operations."),
)

LAYER_NAMES = {number: name for number, name, _ in LAYERS}
LAYER_DESCRIPTIONS = {number: description for number, _, description in LAYERS}

# The model is a service used primarily by the Cognitive core. It is not a
# layer and is not registered as a capability.
BRAIN = {
    "name": "SPS-CA Brain",
    "role": "reasoning, prompt analysis, planning, code generation, debugging, strategy analysis",
    "default_provider": "Ollama",
    "replaceable": True,
}

# Capability registry is a supporting subsystem, deliberately separate from
# both the Brain and the ten architectural layers.
SUPPORTING_SUBSYSTEMS = ("Capability Registry", "Capability Lineage", "LLM Provider Abstraction")
