# Architecture Reference

SPS-CA's ten canonical layers are defined in `layers/architecture.py`. The implementation directories are:

```text
layers/
├── layer_01_software_dna_core/
├── layer_02_governance_core/
├── layer_03_cognitive_core/
├── layer_04_knowledge_core/
├── layer_05_experience_core/
├── layer_06_meta_learning_core/
├── layer_07_adaptation_core/
├── layer_08_evolution_core/
├── layer_09_verification_validation_core/
└── layer_10_execution_core/
```

Each package exposes its existing implementation through meaningful sub-components. `layers/architecture.py` is the vocabulary source used by the UI and architecture tests.

The separate Brain performs model-backed reasoning and planning. Supporting subsystems include Capability Registry, Capability Lineage, and LLM Provider Abstraction.

See `docs/PIPELINE.md` for runtime sequencing and `docs/SELF_PROGRAMMING.md` for the growth lifecycle.
