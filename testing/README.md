# Testing Architecture

Run the focused architecture test:

```bash
pytest layers/tests/test_architecture_manifest.py
```

The test verifies exactly ten canonical layers, exact canonical names, the authoritative sub-component vocabulary, the separate Brain boundary, and the absence of legacy layer directory names.

Then run the full suite:

```bash
pytest
```

The architecture manifest is the source of truth; tests should import it rather than duplicate layer names.
