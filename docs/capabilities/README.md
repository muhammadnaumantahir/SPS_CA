# Capability Documentation

The canonical Stage-0 capability contracts are documented in `CANONICAL_CAPABILITIES.md`.

Each canonical capability has its own directory under `capabilities/seeds/` with `capability.py`, `metadata.json`, and `README.md`. Shared implementation helpers live in `capabilities/canonical_runtime.py`.

Generated capabilities produced by Layer 8 live under `capabilities/generated/` and use IDs beginning at CAP-011. They keep provenance and lineage so the baseline IDs remain stable.
