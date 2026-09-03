from layers.layer_05_experience import ExperienceLog

from core.canonical_sps_pipeline import CanonicalSPSPipeline


def test_canonical_pipeline_exposes_exactly_ten_layers_and_brain_boundary():
    pipeline = CanonicalSPSPipeline._build_pipeline(
        result={
            "dna": {"allowed": True},
            "governance": "approved",
            "validation": "success",
            "execution": "success",
            "capability_id": "CAP-002",
            "generated": False,
        },
        brain_intent="code_modification",
        knowledge_valid=True,
        experience=ExperienceLog(),
        failure_patterns={},
        reusable_capabilities=[],
        adaptation_changes={},
        adaptation_ok=True,
    )

    assert [item["number"] for item in pipeline["layers"]] == list(range(1, 11))
    assert pipeline["layers"][2]["component"] == "CognitiveCore + Brain"
    assert pipeline["layers"][7]["component"] == "EvolutionEngine + Capability Registry"
    assert pipeline["layers"][8]["component"] == "Validator"
    assert pipeline["layers"][9]["component"] == "ExecutionEngine"
    assert pipeline["brain"]["component"] == "SPS-CA Brain"
    assert pipeline["brain"]["replaceable"] is True
