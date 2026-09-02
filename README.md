# SPS-CA — Self-Programming Code Assistant

**Version:** 0.8.0  
**Status:** Phase 8 — Target Projects  
**Goal:** Research prototype for governed, traceable and reversible self-programming.

SPS-CA investigates whether an AI coding system can improve future performance by accumulating experience, adapting strategies, and safely developing reusable capabilities.

## Current implementation status

Phases 0–7 established the ten-layer foundation, validation/governance/evolution pipeline, capability registry, execution boundary, seed capabilities and prompt-based CLI. **Phase 8 adds three equivalent benchmark target projects.**

- **Project A:** Python / FastAPI
- **Project B:** Java / Spring Boot
- **Project C:** TypeScript / Express
- Shared Task API: health plus CRUD operations.
- Shared seeded defect: `/tasks/{id}/exists` incorrectly ignores the requested ID.
- Equivalent tests and standalone run instructions are included for each target.
- `.github/workflows/phase8-tests.yml` verifies all three targets plus the TypeScript build.

See [`docs/PHASE_8_STATUS.md`](docs/PHASE_8_STATUS.md) for the benchmark contract and requirement mapping.

## Architecture

The ten SPS layers are first-class packages under `layers/`. Cross-layer orchestration is under `core/`. Supporting subsystems are deliberately separated.

```text
SPS_CA/
├── core/                    # Orchestration, state, events, interfaces
├── layers/                  # Ten SPS layers; each owns its implementation
├── models/                  # Provider/model abstraction
├── coding/                  # Repository intelligence and code manipulation
├── capabilities/            # Capability lifecycle and lineage
├── execution/               # Controlled execution infrastructure
├── governance/              # Policy/risk/approval infrastructure
├── validation/              # Verification infrastructure
├── memory/                  # Runtime conversations/experiences/memories/traces
├── projects/                # Equivalent benchmark target projects
├── data/                    # Runtime database/users/sessions/exports
├── ui/                      # Prompt UI and future presentation layers
├── testing/                 # Cross-layer and research tests
├── analytics/               # Metrics, graphs, growth and evolution datasets
└── docs/                    # Architecture, research and experiment docs
```

## Target projects

```text
projects/
├── project_a_python/        # FastAPI + pytest
├── project_b_java/          # Spring Boot + JUnit/MockMvc
└── project_c_typescript/    # Express + Vitest/Supertest
```

All three implement the same Task API so later phases can compare repair behavior across languages without changing the problem domain.

## Phase 7 CLI

```bash
python ui/cli_interface.py
```

Commands include `load`, `show project`, `show registry`, `show experience`, `help`, and `quit`.

## Development rules

1. Each SPS layer keeps its own implementation and layer-local tests.
2. Cross-layer communication uses explicit interfaces/events or injected service boundaries.
3. User code and runtime execution snapshots stay outside SPS source control.
4. Generated capabilities require provenance and versioning.
5. Evolution proposals pass Governance and Validation before activation.
6. Research scenarios, target projects and baselines remain reproducible and separate from runtime code.
7. Every implementation phase requires tests and verification.
