# PHASE 0 — Architecture & Environment Foundation

**Status:** In Progress  
**Updated:** 2026-08-31

## Local environment

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] `pip install -r requirements.txt` succeeds
- [x] Ollama installed
- [ ] Ollama API verified
- [ ] Local coding model installed

### Current recommended office model

For the current 16 GB RAM / Intel HD 620 / i7 7th Gen machine:

```bash
ollama pull qwen2.5-coder:7b
ollama run qwen2.5-coder:7b
```

Qwen3-Coder is a future target for stronger hardware. Do not describe `qwen2.5-coder:7b` as Qwen3-Coder; they are different models.

## Repository architecture

- [x] Ten first-class layer packages under `layers/`
- [x] Cross-layer orchestration boundary under `core/`
- [x] Provider-neutral model boundary under `models/`
- [x] Coding subsystem under `coding/`
- [x] Capability lifecycle and lineage boundary
- [x] Dedicated execution infrastructure
- [x] Dedicated validation infrastructure
- [x] Runtime memory/data boundary
- [x] User project boundary
- [x] Dedicated UI and visualization boundary
- [x] Dedicated cross-layer/research testing boundary
- [x] Analytics/graph boundary
- [x] Architecture v2 documentation
- [x] Removed `sqlite3` from pip requirements
- [x] Removed obsolete CLI entry-point assumption from package setup
- [ ] Implement typed cross-layer event contracts
- [ ] Implement state machine
- [ ] Implement Layer 1
- [ ] Implement Layer 2

## Architecture contract

```text
User Request
    ↓
Cognitive Core
    ↓
Repository / Experience / Capability Context
    ↓
Adaptation
    ↓
Governance
    ↓
Execution
    ↓
Validation
    ↓
Experience + Trace
    ↓
Meta-Learning / Evolution
    ↓
Capability Registry
    ↓
Reuse
```

Evolution must not bypass Governance or Validation. Generated capabilities must have provenance and versioning.

## Verification

Run after environment setup:

```bash
python --version
python -c "import tree_sitter, pytest, pydantic; print('dependencies OK')"
pytest -q
ollama list
```

## Phase 0 completion criteria

Phase 0 is complete when the local environment works, the architecture skeleton is present, the documentation matches the implementation, and the basic repository/import/test verification passes.

**Next:** Phase 1 — implement Layers 1–2 plus their layer-local tests and typed interfaces/events.