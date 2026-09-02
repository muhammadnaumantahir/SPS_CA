# SPS-CA — Self-Programming Code Assistant

**Version:** 1.0.0  
**Status:** Phase 10 — Evaluation Harness  
**Goal:** Research prototype for governed, traceable and reversible self-programming.

SPS-CA investigates whether an AI coding system can improve future performance by accumulating experience, adapting strategies, and safely developing reusable capabilities.

## Current implementation status

Phases 0–8 established the ten-layer foundation, validation/governance/evolution pipeline, capability registry, execution boundary, seed capabilities, prompt-based CLI, and three equivalent benchmark target projects. **Phase 9 adds two same-model comparison baselines; Phase 10 adds the reproducible evaluation harness.**

- **Baseline A:** Naive LLM — direct request + project context, no tools or learning.
- **Baseline B:** Coding Agent — deterministic analysis/syntax/test tool boundaries, no learning or capability generation.
- **SPS-CA:** Full ten-layer framework.
- **Shared local model:** `qwen2.5-coder:7b` through the provider-neutral LLM interface.
- **Evaluation catalog:** S1–S25 with source-defined project/baseline distribution.
- **Measurement:** JSONL execution records plus common success/time aggregation.
- **Research boundary:** real Ollama experiments are run in the controlled local environment; CI verifies the harness without fabricating model results.

See [`docs/PHASE_9_STATUS.md`](docs/PHASE_9_STATUS.md) and [`docs/PHASE_10_STATUS.md`](docs/PHASE_10_STATUS.md) for the experiment contracts and evidence boundary.

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
├── baselines/               # Phase-9 comparison agents and result contract
├── evaluation/              # Scenario matrix, execution harness and metrics
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

## Phase 10 evaluation

```text
evaluation/
├── scenarios.py             # 25-scenario source catalog + matrix builder
├── phase10_runner.py        # Controlled execution harness
├── metrics.py               # Common experiment metrics
└── tests/                   # Harness contract tests
```

The master protocol calls for 25 scenarios with source-defined project/baseline scope and empirical collection of success, time, reuse, regression, coverage, rollback and governance metrics. The implementation does not assert the target performance numbers until the controlled runs have actually produced evidence.

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
