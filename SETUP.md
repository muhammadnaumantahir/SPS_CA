# Setup

Install dependencies as described in the repository requirements, then run the test suite with `pytest`.

## Architecture sanity check

The authoritative layer vocabulary is in `layers/architecture.py`. Implementation packages use these canonical directory names:

```text
layer_01_software_dna_core
layer_02_governance_core
layer_03_cognitive_core
layer_04_knowledge_core
layer_05_experience_core
layer_06_meta_learning_core
layer_07_adaptation_core
layer_08_evolution_core
layer_09_verification_validation_core
layer_10_execution_core
```

Use `pytest layers/tests/test_architecture_manifest.py` to verify the vocabulary. Legacy import aliases are retained only for migration compatibility.
