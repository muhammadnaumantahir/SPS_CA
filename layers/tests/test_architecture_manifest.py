from layers.architecture import BRAIN, LAYERS, architecture_manifest


def test_canonical_layers_match_requested_structure():
    names = [name for _, name, _, _ in LAYERS]
    assert names == [
        "Software DNA Layer",
        "Governance Layer",
        "Cognitive Layer",
        "Knowledge Layer",
        "Experience Layer",
        "Meta-Learning Layer",
        "Adaptation Layer",
        "Evolution Layer",
        "Verification & Validation Layer",
        "Execution Layer",
    ]


def test_each_layer_has_purpose_and_optional_subcomponents():
    manifest = architecture_manifest()
    assert len(manifest["layers"]) == 10
    for layer in manifest["layers"]:
        assert layer["purpose"]
        assert isinstance(layer["sub_components"], list)
        assert all(isinstance(item, str) and item for item in layer["sub_components"])


def test_brain_is_separate_from_layers_and_capabilities():
    manifest = architecture_manifest()
    assert BRAIN["replaceable"] is True
    assert BRAIN["boundary"] == "separate model service"
    assert all("Brain" not in layer["name"] for layer in manifest["layers"])
