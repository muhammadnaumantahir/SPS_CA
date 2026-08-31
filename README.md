# SPS-CA — Self-Programming Code Assistant

**Version:** 0.3.0  
**Status:** Architecture Foundation  
**Goal:** Research prototype for governed, traceable and reversible self-programming.

SPS-CA investigates whether an AI coding system can improve future performance by accumulating experience, adapting strategies, and safely developing reusable capabilities.

## Core research distinction

A conventional coding agent is approximately:

`Task → Model → Tools → Tests → Result`

SPS-CA adds persistent experience, meta-learning, adaptation, governed evolution, capability lineage and feedback:

`Task → Cognition → Context → Adaptation → Governance → Execution → Validation → Experience → Evolution → Reuse`

Self-modification must never bypass governance or validation.

## Architecture

The ten SPS layers are first-class packages under `layers/`. Cross-layer orchestration is under `core/`. Supporting subsystems are deliberately separated.

```text
SPS_CA/
├── core/                    # Orchestration, state, events, interfaces
├── layers/                  # Ten SPS layers; each owns its implementation
│   ├── layer_01_software_dna/
│   ├── layer_02_cognitive_core/
│   ├── layer_03_experience/
│   ├── layer_04_meta_learning/
│   ├── layer_05_adaptation/
│   ├── layer_06_validation/
│   ├── layer_07_governance/
│   ├── layer_08_evolution/
│   ├── layer_09_capability_registry/
│   └── layer_10_execution/
├── models/                  # Provider/model abstraction
├── coding/                  # Repository intelligence and code manipulation
├── capabilities/            # Capability lifecycle and lineage
├── execution/               # Controlled execution infrastructure
├── governance/              # Policy/risk/approval infrastructure
├── validation/              # Verification infrastructure
├── memory/                  # Runtime conversations/experiences/memories/traces
├── projects/                # User target projects; never mix with SPS source
├── data/                    # Runtime database/users/sessions/exports
├── ui/                      # UI and visualization
├── testing/                 # Cross-layer and research tests
├── analytics/               # Metrics, graphs, growth and evolution datasets
└── docs/                    # Architecture, research and experiment docs
```

Architecture contract: [`docs/architecture/SPS_CA_ARCHITECTURE_V2.md`](docs/architecture/SPS_CA_ARCHITECTURE_V2.md).

## Capability evolution

```text
Task / Failure
      ↓
Experience
      ↓
Pattern
      ↓
Adaptation Proposal
      ↓
Capability Candidate
      ↓
Governance
      ↓
Validation
      ↓
Capability Registry
      ↓
Reuse / Measurement
```

Generated capabilities retain provenance, parent capabilities, triggering task/experience IDs, proposal IDs, model/provider metadata, validation evidence, versions and activation history. This supports future capability genealogy and growth graphs.

## UI and analytics vision

The future dashboard will expose project/session state and explainable system evolution, including capability growth, genealogy, task-to-capability relationships, versions, validation evidence, provider performance, rollback statistics and event traces. Analytics is derived from events and persisted metadata; the UI is not the source of truth.

## Model strategy

SPS-CA uses a provider-neutral model interface. The initial local provider is Ollama. Future adapters can support OpenAI, Anthropic and additional local/cloud providers without changing the SPS layers.

For the current 16 GB RAM / Intel HD 620 / i7 7th Gen office machine, start with `qwen2.5-coder:7b`. Qwen3-Coder is a separate model and can be used later on stronger hardware.

**Never commit API keys or model secrets.**

## Setup

Use [`SETUP.md`](SETUP.md) for the complete installation and verification procedure.

Use [`REQUIREMENTS.md`](REQUIREMENTS.md) for hardware, software, model, runtime-data and research requirements.

Quick start after cloning:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5-coder:7b
pytest -q
```

## Development rules

1. Each SPS layer keeps its own implementation and layer-local tests.
2. Cross-layer communication uses explicit interfaces/events.
3. User code and runtime data stay outside SPS source control.
4. Generated capabilities require provenance and versioning.
5. Evolution proposals pass Governance and Validation before activation.
6. Research scenarios and baselines remain reproducible and separate from runtime code.
7. Every implementation phase requires tests and verification.

## Research evaluation

The intended comparison is:

- **Baseline A:** naive LLM coding
- **Baseline B:** conventional tool-augmented coding agent
- **SPS-CA:** coding agent with experience, adaptation, capability evolution, governance and lineage

Primary evidence should include repeat-task performance, capability reuse, failure recovery, validation success, rollback behavior and measurable evolution over time.

## Status

The repository is the architecture foundation. The ten layers will be implemented incrementally, with separate layer code, tests, model adapters, runtime data boundaries, analytics and UI support.