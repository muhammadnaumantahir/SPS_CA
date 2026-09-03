"""Canonical Stage-0 capability catalogue for SPS-CA.

The baseline is deliberately small and intent-oriented. Each capability has one
primary responsibility; broader behavior is achieved by composing these
capabilities after Brain intent classification.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

SUPPORTED_LANGUAGES = [
    "python",
    "java",
    "javascript",
    "typescript",
    "go",
    "csharp",
    "cpp",
    "rust",
]

INTENT_CLASSES = (
    "code_generation",
    "code_modification",
    "analysis",
    "bug_diagnosis",
    "bug_fixing",
    "refactoring",
    "test_generation",
    "documentation",
    "validation",
    "project_operations",
    "mixed",
    "unknown",
)

CANONICAL_CAPABILITIES: tuple[dict[str, Any], ...] = (
    {
        "id": "CAP-001",
        "name": "Code Generation",
        "description": "Create new source code from an explicit natural-language requirement.",
        "type": "generation",
        "intent_class": "code_generation",
        "allowed_intents": ["code_generation", "mixed"],
        "forbidden_intents": ["test_generation", "analysis", "bug_diagnosis"],
        "risk_level": "medium",
        "side_effects": ["replaces working source when the request explicitly asks for a new program"],
        "supported_languages": SUPPORTED_LANGUAGES,
        "version": "1.0.0",
        "entry_point": "capabilities.seeds.cap_001_code_generation.capability.run",
        "documentation_path": "capabilities/seeds/cap_001_code_generation/README.md",
        "metadata_path": "capabilities/seeds/cap_001_code_generation/metadata.json",
        "tags": ["canonical", "generation", "source-creation"],
    },
    {
        "id": "CAP-002",
        "name": "Code Modification",
        "description": "Apply an explicit change to existing source code while preserving unrelated behavior.",
        "type": "modification",
        "intent_class": "code_modification",
        "allowed_intents": ["code_modification", "mixed"],
        "forbidden_intents": ["test_generation"],
        "risk_level": "medium",
        "side_effects": ["modifies supplied working source"],
        "supported_languages": SUPPORTED_LANGUAGES,
        "version": "1.0.0",
        "entry_point": "capabilities.seeds.cap_002_code_modification.capability.run",
        "documentation_path": "capabilities/seeds/cap_002_code_modification/README.md",
        "metadata_path": "capabilities/seeds/cap_002_code_modification/metadata.json",
        "tags": ["canonical", "modification", "feature"],
    },
    {
        "id": "CAP-003",
        "name": "Code Explanation & Analysis",
        "description": "Explain source structure, behavior, symbols, flow, and relevant implementation characteristics without changing code.",
        "type": "analysis",
        "intent_class": "analysis",
        "allowed_intents": ["analysis", "mixed"],
        "forbidden_intents": ["code_generation", "test_generation", "bug_fixing"],
        "risk_level": "low",
        "side_effects": [],
        "supported_languages": SUPPORTED_LANGUAGES,
        "version": "1.0.0",
        "entry_point": "capabilities.seeds.cap_003_code_analysis.capability.run",
        "documentation_path": "capabilities/seeds/cap_003_code_analysis/README.md",
        "metadata_path": "capabilities/seeds/cap_003_code_analysis/metadata.json",
        "tags": ["canonical", "analysis", "explanation"],
    },
    {
        "id": "CAP-004",
        "name": "Bug Detection & Diagnosis",
        "description": "Find and diagnose likely defects, their causes, and evidence without applying a fix.",
        "type": "bug_detection",
        "intent_class": "bug_diagnosis",
        "allowed_intents": ["bug_diagnosis", "mixed"],
        "forbidden_intents": ["code_generation", "test_generation"],
        "risk_level": "low",
        "side_effects": [],
        "supported_languages": SUPPORTED_LANGUAGES,
        "version": "1.0.0",
        "entry_point": "capabilities.seeds.cap_004_bug_diagnosis.capability.run",
        "documentation_path": "capabilities/seeds/cap_004_bug_diagnosis/README.md",
        "metadata_path": "capabilities/seeds/cap_004_bug_diagnosis/metadata.json",
        "tags": ["canonical", "bug", "diagnosis"],
    },
    {
        "id": "CAP-005",
        "name": "Bug Fixing",
        "description": "Repair a diagnosed defect in supplied source code and return the corrected source.",
        "type": "fix",
        "intent_class": "bug_fixing",
        "allowed_intents": ["bug_fixing", "mixed"],
        "forbidden_intents": ["test_generation"],
        "risk_level": "high",
        "side_effects": ["modifies supplied working source"],
        "supported_languages": SUPPORTED_LANGUAGES,
        "version": "1.0.0",
        "entry_point": "capabilities.seeds.cap_005_bug_fixing.capability.run",
        "documentation_path": "capabilities/seeds/cap_005_bug_fixing/README.md",
        "metadata_path": "capabilities/seeds/cap_005_bug_fixing/metadata.json",
        "tags": ["canonical", "bug", "repair"],
    },
    {
        "id": "CAP-006",
        "name": "Refactoring & Optimization",
        "description": "Improve code structure, maintainability, or performance while preserving intended behavior.",
        "type": "refactoring",
        "intent_class": "refactoring",
        "allowed_intents": ["refactoring", "mixed"],
        "forbidden_intents": ["test_generation"],
        "risk_level": "medium",
        "side_effects": ["modifies supplied working source"],
        "supported_languages": SUPPORTED_LANGUAGES,
        "version": "1.0.0",
        "entry_point": "capabilities.seeds.cap_006_refactoring.capability.run",
        "documentation_path": "capabilities/seeds/cap_006_refactoring/README.md",
        "metadata_path": "capabilities/seeds/cap_006_refactoring/metadata.json",
        "tags": ["canonical", "refactoring", "optimization"],
    },
    {
        "id": "CAP-007",
        "name": "Test Generation",
        "description": "Create automated tests only when the user explicitly requests tests or the classified task is test generation.",
        "type": "testing",
        "intent_class": "test_generation",
        "allowed_intents": ["test_generation", "mixed"],
        "forbidden_intents": ["code_generation", "code_modification", "analysis", "bug_diagnosis", "bug_fixing", "refactoring"],
        "risk_level": "low",
        "side_effects": ["creates test source"],
        "supported_languages": SUPPORTED_LANGUAGES,
        "version": "1.0.0",
        "entry_point": "capabilities.seeds.cap_007_test_generation.capability.run",
        "documentation_path": "capabilities/seeds/cap_007_test_generation/README.md",
        "metadata_path": "capabilities/seeds/cap_007_test_generation/metadata.json",
        "tags": ["canonical", "testing", "generation"],
    },
    {
        "id": "CAP-008",
        "name": "Documentation Generation",
        "description": "Generate docstrings, comments, API descriptions, or focused documentation from supplied source.",
        "type": "documentation",
        "intent_class": "documentation",
        "allowed_intents": ["documentation", "mixed"],
        "forbidden_intents": ["test_generation"],
        "risk_level": "low",
        "side_effects": ["may modify supplied source when documentation is embedded"],
        "supported_languages": SUPPORTED_LANGUAGES,
        "version": "1.0.0",
        "entry_point": "capabilities.seeds.cap_008_documentation.capability.run",
        "documentation_path": "capabilities/seeds/cap_008_documentation/README.md",
        "metadata_path": "capabilities/seeds/cap_008_documentation/metadata.json",
        "tags": ["canonical", "documentation"],
    },
    {
        "id": "CAP-009",
        "name": "Code Validation & Review",
        "description": "Validate syntax and review supplied code for correctness, quality, and obvious risks without silently modifying it.",
        "type": "validation",
        "intent_class": "validation",
        "allowed_intents": ["validation", "mixed"],
        "forbidden_intents": ["code_generation", "test_generation"],
        "risk_level": "low",
        "side_effects": [],
        "supported_languages": SUPPORTED_LANGUAGES,
        "version": "1.0.0",
        "entry_point": "capabilities.seeds.cap_009_validation.capability.run",
        "documentation_path": "capabilities/seeds/cap_009_validation/README.md",
        "metadata_path": "capabilities/seeds/cap_009_validation/metadata.json",
        "tags": ["canonical", "validation", "review"],
    },
    {
        "id": "CAP-010",
        "name": "Project/File Operations",
        "description": "Plan safe project and file changes such as target paths, file creation, deletion, and project structure updates.",
        "type": "project_operations",
        "intent_class": "project_operations",
        "allowed_intents": ["project_operations", "mixed"],
        "forbidden_intents": ["test_generation"],
        "risk_level": "high",
        "side_effects": ["may create, update, or remove project files when an execution adapter is enabled"],
        "supported_languages": SUPPORTED_LANGUAGES,
        "version": "1.0.0",
        "entry_point": "capabilities.seeds.cap_010_project_operations.capability.run",
        "documentation_path": "capabilities/seeds/cap_010_project_operations/README.md",
        "metadata_path": "capabilities/seeds/cap_010_project_operations/metadata.json",
        "tags": ["canonical", "project", "files"],
    },
)

CANONICAL_BY_ID = {item["id"]: item for item in CANONICAL_CAPABILITIES}


def canonical_catalog() -> list[dict[str, Any]]:
    """Return a detached catalog safe to pass to Brain/provider prompts."""
    return deepcopy(list(CANONICAL_CAPABILITIES))


def capability_ids_for_intent(intent_class: str) -> list[str]:
    """Return capabilities eligible for one classified intent."""
    intent = intent_class if intent_class in INTENT_CLASSES else "unknown"
    if intent == "unknown":
        return [item["id"] for item in CANONICAL_CAPABILITIES]
    if intent == "mixed":
        return [item["id"] for item in CANONICAL_CAPABILITIES]
    return [
        item["id"]
        for item in CANONICAL_CAPABILITIES
        if intent in item["allowed_intents"] and intent not in item["forbidden_intents"]
    ]
