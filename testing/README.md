# Testing Architecture

Run the focused architecture test:

```bash
pytest layers/tests/test_architecture_manifest.py
```

The test verifies exactly ten canonical layers, exact canonical names, the authoritative sub-component vocabulary, the separate Brain boundary, and the absence of legacy layer directory names.

## Scenario suite

The canonical growth suite is `evaluation/scenarios/growth.json`. It contains exactly **1,000 scenarios**:

- 490 capability-routing cases
- 500 autonomous-evolution strategy cases (100 each for create, improve, adapt, replan, compose)
- 10 evolution-proof lifecycle cases

The suite is already committed to the repository. Tests and the Colab notebook read this file directly; they do not need to generate a new suite.

Run the complete test suite with:

```bash
pytest
```

The architecture manifest is the source of truth; tests should import it rather than duplicate layer names.
