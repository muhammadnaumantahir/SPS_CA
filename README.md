# SPS-CA — Self-Programming Code Assistant

**Version:** 0.2.0  
**Status:** Phase 0 — Architecture Foundation  
**Goal:** Research prototype for governed, traceable and reversible self-programming.

SPS-CA is an experimental coding-agent architecture designed to investigate whether an AI coding system can improve its future performance by accumulating experience, adapting strategies, and safely developing reusable capabilities.

## Core research distinction

A conventional coding agent is approximately:

`Task → Model → Tools → Tests → Result`

SPS-CA adds persistent experience, meta-learning, adaptation, governed evolution, capability lineage and feedback:

`Task → Cognition → Experience/Knowledge → Adaptation → Governance → Execution → Validation → Experience → Evolution → Reuse`

Self-modification is never allowed to bypass governance and validation.

## Architecture

The ten SPS layers are first-class packages under `layers/`. Cross-layer orchestration is under `core/`. Supporting subsystems are intentionally separated.

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
│   ├── base/
│   ├── ollama/
│   ├── qwen/
│   ├── openai/              # Future API provider
│   ├── anthropic/            # Future API provider
│   └── registry/
├── coding/                  # Repository intelligence and code manipulation
├── capabilities/             # Built-in/generated capabilities + lineage
├── execution/                # Controlled execution infrastructure
├── governance/               # Policy/risk/approval infrastructure
├── validation/               # Verification infrastructure
├── memory/                   # Runtime conversations/experiences/memories/traces
├── projects/                 # User target projects; never mix with SPS source
├── data/                     # Runtime DB/users/sessions/exports
├── ui/                       # Frontend/backend/visualization
├── testing/                  # Cross-layer, integration, system and research tests
├── analytics/                # Metrics, graphs, growth and evolution datasets
└── docs/                     # Architecture, research and experiment docs
```

See [`docs/architecture/SPS_CA_ARCHITECTURE_V2.md`](docs/architecture/SPS_CA_ARCHITECTURE_V2.md) for the architectural contract.

## Capability evolution and lineage

A generated capability is a research artifact with provenance, not just a Python file. The intended lifecycle is:

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

Each capability will retain parent capability IDs, triggering task/experience IDs, proposal IDs, model/provider metadata, validation evidence, versions and activation history. This data will power future genealogy and capability-growth graphs.

## UI and analytics vision

The future dashboard will expose project/session state plus explainable system evolution:

- capability count and growth over time
- capability genealogy/lineage graph
- task → failure → experience → adaptation → capability relationships
- capability versions and validation evidence
- model/provider performance
- execution success/failure and rollback statistics
- evolution history and event traces

Analytics derives datasets from events and persisted metadata; the UI is not the source of truth.

## Model strategy

SPS-CA is model-provider independent. The application calls a common model interface and the provider adapter handles Ollama or a future cloud/local provider.

For the current 16 GB office machine, start with a smaller local coding model such as `qwen2.5-coder:7b` through Ollama. A stronger machine can later use Qwen3-Coder without changing the SPS layers.

Do not commit API keys or model secrets.

## Runtime data isolation

Target user projects, chats, sessions, experiences, memories and traces are runtime data and are intentionally separated from the SPS-CA source tree. Runtime data should be stored outside Git and through a configurable data root.

## Setup

Requirements:

- Python 3.11+
- Git
- Ollama for local models
- 16 GB RAM minimum for the initial prototype; model choice depends on available hardware

```bash
git clone https://github.com/muhammadnaumantahir/SPS_CA.git
cd SPS_CA
python -m venv venv

# Windows
venv\\Scripts\\activate

# Linux/macOS
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

For the current office machine:

```bash
ollama pull qwen2.5-coder:7b
ollama run qwen2.5-coder:7b
```

## Development rules

1. Each SPS layer keeps its own implementation and layer-local tests.
2. Cross-layer communication uses explicit interfaces/events.
3. User code and runtime data never become part of SPS source control.
4. Generated capabilities require provenance and versioning.
5. Evolution proposals pass Governance and Validation before activation.
6. Research scenarios and baselines remain reproducible and separate from production runtime code.
7. Every phase must have tests and verification before being marked complete.

## Research evaluation

The intended comparison is:

- **Baseline A:** naive LLM coding
- **Baseline B:** conventional tool-augmented coding agent
- **SPS-CA:** coding agent with experience, adaptation, capability evolution, governance and lineage

Primary research evidence should include repeat-task performance, capability reuse, failure recovery, validation success, rollback behavior and measurable evolution over time.

## Status

Phase 0 is the architecture foundation. The repository currently contains the architectural skeleton and contracts; the ten layer implementations will be built incrementally in later phases.
