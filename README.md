# SPS-CA — Self-Programming Code Assistant

**Version:** 0.7.0  
**Status:** Phase 7 — User Interface & Prompt-Based Interaction  
**Goal:** Research prototype for governed, traceable and reversible self-programming.

SPS-CA investigates whether an AI coding system can improve future performance by accumulating experience, adapting strategies, and safely developing reusable capabilities.

## Core research distinction

A conventional coding agent is approximately:

`Task → Model → Tools → Tests → Result`

SPS-CA adds persistent experience, meta-learning, adaptation, governed evolution, capability lineage and feedback:

`Task → Cognition → Context → Adaptation → Governance → Execution → Validation → Experience → Evolution → Reuse`

Self-modification must never bypass governance or validation.

## Current implementation status

Phases 0–6 established the ten-layer foundation, validation/governance/evolution pipeline, capability registry, execution boundary and executable seed capabilities. **Phase 7 adds the prompt-based user interface and session interaction layer.**

- **CLI:** `python ui/cli_interface.py`
- **Commands:** `load`, `show project`, `show registry`, `show experience`, `help`, `quit`.
- **Session history:** persisted locally as `ui/session_history.json` at runtime.
- **Request flow:** natural-language requests are routed through Cognitive Core, then through Validation and Governance before approved executable changes reach Layer 10.
- **Response:** reports capability, validation/governance status, test counts, coverage when available, and execution time.

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
├── ui/                      # Prompt UI and future presentation layers
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
Execution
      ↓
Reuse / Measurement
```

Generated capabilities retain provenance, triggering task/experience identifiers, versions, validation evidence and activation history. This supports future capability genealogy and growth graphs.

## Model strategy

SPS-CA uses a provider-neutral model interface. The initial local provider is Ollama.

**Never commit API keys or model secrets.**

## Setup

Use [`SETUP.md`](SETUP.md) for the complete installation and verification procedure.

Use [`REQUIREMENTS.md`](REQUIREMENTS.md) for hardware, software, model, runtime-data and research requirements.

Quick start after cloning:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5-coder:7b
pytest -q
python ui/cli_interface.py
```

## Phase 7 commands

```text
load projects/project_a_python
show project
show registry
show experience
help
quit
```

Natural-language coding requests can be entered directly after loading a target project.

## Development rules

1. Each SPS layer keeps its own implementation and layer-local tests.
2. Cross-layer communication uses explicit interfaces/events or injected service boundaries.
3. User code and runtime execution snapshots stay outside SPS source control.
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

**Phase 7 UI implementation is in place.** The source includes the interactive CLI, required commands, session history, capability selection, validation/governance routing, execution reporting and a GitHub Actions verification workflow. Remote workflow execution remains subject to the repository's GitHub Actions availability.
