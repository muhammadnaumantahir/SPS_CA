# Phase 4 — Layer 8 Evolution Engine

## Status

Implementation branch: `phase-4-evolution`

Base commit: `dcf7474b1be82cbc2b74d0dcaefad86ed299da81`

## Implemented

- Deterministic repeated-failure detection with configurable occurrence threshold.
- Capability planning with generated capability IDs, trigger pattern, parent capability lineage, supported languages, and test cases.
- Provider-neutral LLM generation through the existing `models.base.LLMProvider` interface.
- Strict JSON response parsing with markdown-fence tolerance.
- Static safety validation for generated Python before staging.
- Pending/staged capability lifecycle under `evaluation/evolution/pending/`.
- Generated capability artifact contract:
  - `capability.py`
  - `tests.py`
  - `metadata.json`
  - `README.md`
- Test execution through pytest with optional coverage extraction and the thesis-required 80% threshold when coverage is reported.
- Governance approval boundary: staged artifacts cannot be promoted unless explicitly approved.
- Promotion into `capabilities/generated/CAP-*` after approval.
- Model/provider and lineage metadata recorded with the generated artifact.

## Architecture Decision

Layer 8 lives under `layers/layer_08_evolution/`, matching the Phase 0 as-built package-per-layer architecture. `core/` remains reserved for cross-layer orchestration, shared state, and event contracts.

## Safety Boundary

The engine does **not** automatically promote model-generated source. Generation and promotion are separate operations. A future orchestration path should call Layer 7 Governance after Layer 6 validation and only then invoke `promote_capability(..., approved=True)`.

Generated source is also rejected when it contains syntax errors or selected dangerous operations/imports. This is defense-in-depth, not a substitute for sandboxing.

## Test Coverage

`layers/layer_08_evolution/tests/test_evolution_engine.py` covers detection, planning, ID allocation, model response parsing, source validation, staging, approval gating, promotion, missing artifacts, and coverage parsing.

Run locally with:

```bash
pytest layers/layer_08_evolution/tests -q
```

## Remaining Phase 4 Integration Work

The engine is intentionally isolated from the cross-layer runtime until the next integration step. The remaining work is to wire Layer 8 into the SPS orchestration/event flow, connect real Layer 6 sandbox results and Layer 7 governance decisions, update Layer 9 registration, and add an end-to-end evolution scenario using Ollama.
