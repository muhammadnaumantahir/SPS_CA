"""Canonical SPS-CA ten-layer architecture vocabulary.

Layer names are canonical and must not be changed. New behavior belongs in
sub-components. The Brain is a separate replaceable model service and is not
a layer or capability.
"""
from __future__ import annotations
from typing import Final

LAYERS = (
    (1, "Software DNA Core", "Acts as the absolute source of truth, defining constraints and meta-rules that all evolution must obey", ("Goals", "Policies", "Constraints", "Learning Rules", "Repair Rules", "Safety Rules", "Ethical Rules", "Evolution Rules", "Meta-Rules")),
    (2, "Governance Core", "Executive gatekeeper that authorizes proposed changes against the Software DNA before deployment", ("Authorization", "Evolution Approval", "Compliance Checking", "Risk Management")),
    (3, "Cognitive core", "Synthesizes goals and system state into tactical decisions, reasoning, and plans", ("Goal Manager", "Reasoning Engine", "Planning Engine", "Decision Engine", "Explainability Engine")),
    (4, "Knowledge core", "Manages structured, evolving domain knowledge", ("Knowledge Base", "Knowledge Acquisition Engine", "Knowledge Validation", "Knowledge Evolution")),
    (5, "Experience core", "Collects and stores feedback and runtime signals as historical memory", ("Memory", "Feedback", "Monitoring", "Learning Engine")),
    (6, "Meta-learning core", "Evaluates and improves the system's own learning process", ("Learning Evaluation", "Strategy Optimization", "Learning Improvement")),
    (7, "Adaptation core", "Shifts behavior instantly by context, without modifying source code", ("Context Awareness", "Personalization", "Capability Activation", "Strategy Selection")),
    (8, "Evolution core", "The engine of genuine structural self-growth", ("Self-Modification", "Self-Regeneration", "Capability Preservation", "Capability Differentiation", "Capability Creation", "SPS Growth Decision")),
    (9, "Verification & Validation Core", "Screens new or mutated code in a sandbox before it reaches production", ("Testing", "Simulation", "Safety Validation", "Performance Validation")),
    (10, "Execution Core", "Translates validated decisions into real, observable action", ("Action Executor", "Services", "APIs", "User Interaction")),
)
LAYER_NAMES: Final = {number: name for number, name, _, _ in LAYERS}
LAYER_DESCRIPTIONS: Final = {number: purpose for number, _, purpose, _ in LAYERS}
LAYER_SUBCOMPONENTS: Final = {number: list(subcomponents) for number, _, _, subcomponents in LAYERS}
BRAIN = {"name": "SPS-CA Brain", "role": "reasoning, prompt analysis, planning, code generation, debugging, strategy analysis", "default_provider": "Ollama", "replaceable": True, "boundary": "separate model service"}
SUPPORTING_SUBSYSTEMS = ("Capability Registry", "Capability Lineage", "LLM Provider Abstraction")

def architecture_manifest() -> dict:
    return {"layers": [{"number": n, "name": name, "purpose": purpose, "description": purpose, "sub_components": list(parts)} for n, name, purpose, parts in LAYERS], "brain": dict(BRAIN), "supporting_subsystems": list(SUPPORTING_SUBSYSTEMS)}
