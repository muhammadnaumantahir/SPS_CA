from layers.architecture import BRAIN, LAYERS, architecture_manifest


def test_canonical_layers_match_requested_structure():
    names = [name for _, name, _, _ in LAYERS]
    assert names == [
        "Software DNA Core",
        "Governance Core",
        "Cognitive core",
        "Knowledge core",
        "Experience core",
        "Meta-learning core",
        "Adaptation core",
        "Evolution core",
        "Verification & Validation Core",
        "Execution Core",
    ]


def test_each_layer_has_purpose_and_optional_subcomponents():
    manifest = architecture_manifest()
    assert len(manifest["layers"]) == 10
    for layer in manifest["layers"]:
        assert layer["purpose"]
        assert isinstance(layer["sub_components"], list)
        assert all(isinstance(item, str) and item for item in layer["sub_components"])


def test_growth_decision_is_an_evolution_subcomponent():
    manifest = architecture_manifest()
    evolution = manifest["layers"][7]
    assert evolution["name"] == "Evolution core"
    assert "SPS Growth Decision" in evolution["sub_components"]


def test_brain_is_separate_from_layers_and_capabilities():
    manifest = architecture_manifest()
    assert BRAIN["replaceable"] is True
    assert BRAIN["boundary"] == "separate model service"
    assert all("Brain" not in layer["name"] for layer in manifest["layers"])
