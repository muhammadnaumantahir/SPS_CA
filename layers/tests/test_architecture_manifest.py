from pathlib import Path

from layers.architecture import BRAIN, LAYER_NAMES, LAYER_SUBCOMPONENTS, LAYERS

CANONICAL_NAMES = [
    "Software DNA Core", "Governance Core", "Cognitive core", "Knowledge core",
    "Experience core", "Meta-learning core", "Adaptation core", "Evolution core",
    "Verification & Validation Core", "Execution Core",
]

IMPLEMENTATION_DIRECTORIES = [
    "layer_01_software_dna", "layer_02_governance", "layer_03_cognitive",
    "layer_04_knowledge", "layer_05_experience", "layer_06_meta_learning",
    "layer_07_adaptation", "layer_08_evolution", "layer_09_validation", "layer_10_execution",
]

DUPLICATE_CORE_DIRECTORIES = {
    "layer_01_software_dna_core", "layer_02_governance_core", "layer_03_cognitive_core",
    "layer_04_knowledge_core", "layer_05_experience_core", "layer_06_meta_learning_core",
    "layer_07_adaptation_core", "layer_08_evolution_core", "layer_09_verification_validation_core",
    "layer_10_execution_core",
}


def test_architecture_has_exactly_ten_canonical_layers():
    assert [name for _, name, _, _ in LAYERS] == CANONICAL_NAMES
    assert tuple(LAYER_NAMES[n] for n in range(1, 11)) == tuple(CANONICAL_NAMES)


def test_subcomponents_are_authoritative_and_meaningful():
    assert "SPS Growth Decision" in LAYER_SUBCOMPONENTS[8]
    for number in range(1, 11):
        assert LAYER_SUBCOMPONENTS[number]
        assert all(component.strip() for component in LAYER_SUBCOMPONENTS[number])


def test_brain_is_outside_the_ten_layers():
    assert BRAIN["name"] == "SPS-CA Brain"
    assert all("Brain" not in name for name in CANONICAL_NAMES)


def test_each_layer_has_one_implementation_directory():
    layers_root = Path(__file__).parents[1]
    for directory in IMPLEMENTATION_DIRECTORIES:
        assert (layers_root / directory).is_dir(), directory
    for duplicate in DUPLICATE_CORE_DIRECTORIES:
        assert not (layers_root / duplicate).exists(), duplicate
    implementation_dirs = sorted(
        path.name
        for path in layers_root.iterdir()
        if path.is_dir() and path.name.startswith("layer_")
    )
    assert implementation_dirs == sorted(IMPLEMENTATION_DIRECTORIES)
