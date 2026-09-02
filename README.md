# SPS-CA — Self-Programming Code Assistant

**Goal:** Research a governed, traceable and reversible Self-Programming Software (SPS) framework expressed as a coding assistant.

SPS-CA is designed around **10 architectural layers** plus a separate, replaceable **AI Brain**. The Brain is not a layer and is not a capability. Ollama is the default local Brain provider; future model providers can be swapped through `models/` without changing SPS capabilities.

## The SPS-CA model

```text
User request + code
       ↓
L1  Software DNA layer
       ↓
L2  Governance layer
       ↓
L3  Cognitive core  ←── Brain (Ollama / other AI model)
       ↓
L4  Knowledge core
       ↓
L5  Experience core
       ↓
L6  Meta-learning core
       ↓
L7  Adaptation core
       ↓
L8  Evolution core
       ↓
Capabilities (seeded + generated)
       ↓
L9  Verification & Validation
       ↓
L10 Execution layer
       ↓
Experience / learning / evolution feedback
```

A layer is an architectural responsibility. A capability is an executable skill. The Brain is the intelligence service that reasons over context and helps the layers select, compose, generate or improve capabilities.

## Canonical ten layers

| Layer | Name |
|---|---|
| 1 | **Software DNA layer** |
| 2 | **Governance layer** |
| 3 | **Cognitive core** |
| 4 | **Knowledge core** |
| 5 | **Experience core** |
| 6 | **Meta-learning core** |
| 7 | **Adaptation core** |
| 8 | **Evolution core** |
| 9 | **Verification & Validation** |
| 10 | **Execution layer** |

## Brain

`brain/` contains the provider-neutral SPS-CA Brain. It currently delegates to the existing `models/` provider abstraction and defaults to Ollama. The Brain is responsible for reasoning, prompt analysis, planning, code understanding, debugging and strategy analysis. It can select capabilities from the registry, but it is never itself registered as a `CAP-NNN`.

## Capabilities

`capabilities/` contains executable SPS skills with metadata, tests, versioning and lineage. Stage 0 starts with seeded coding capabilities such as bug detection, syntax repair, test generation, optimization, error handling, refactoring, type annotation, documentation and explicit code modification. Evolution may add generated capabilities after validation and governance.

The Capability Registry is a supporting subsystem, not an eleventh architectural layer.

## Evaluation

The research implementation keeps three progressively stronger conditions:

- **Baseline A:** same-model naive coding assistant.
- **Baseline B:** same-model tool-augmented coding assistant without SPS learning/evolution.
- **SPS-CA Stage 0+:** ten-layer framework with fixed capabilities, then experience-informed adaptation and generated/reused capabilities.

The repository contains controlled projects and a 25-scenario evaluation harness. The important evidence is not simply that an LLM can write code, but whether SPS-CA can improve strategy selection, reuse experience, safely evolve capabilities and demonstrate measurable gains under repeated scenarios.

## Repository structure

```text
SPS_CA/
├── brain/                   # Separate AI Brain service
├── layers/                  # Canonical ten-layer architecture
├── core/                    # Cross-layer orchestration/state/events
├── models/                  # Provider/model abstraction (Ollama default)
├── capabilities/            # Seed/generated skills + registry + lineage
├── coding/                  # Repository/code intelligence
├── validation/              # Verification infrastructure
├── governance/              # Governance infrastructure
├── execution/               # Controlled execution infrastructure
├── memory/                  # Runtime experience/memory/traces
├── projects/                # Controlled benchmark projects
├── baselines/               # Comparison agents
├── evaluation/              # Scenarios, runner and metrics
├── analytics/               # Evidence and growth analytics
├── ui/                      # CLI + advanced web dashboard
└── docs/                    # Research and architecture documentation
```

## Run the CLI

```bash
python ui/cli_interface.py
```

## Run the advanced dashboard

```bash
python ui/web_app.py
```

Then open `http://127.0.0.1:8080`.

The dashboard exposes the Brain boundary, live ten-layer status, capability decisions, reasoning summary, modified source, diff and trace. Browser execution is a preview boundary; project mutation remains controlled by the Execution layer.

## Setup and experiments

See `SETUP.md`, `REQUIREMENTS.md`, `docs/ARCHITECTURE.md` and `docs/MASTER_DOCUMENT.md` for installation, research design and the evaluation protocol.

## Development rules

1. Keep the ten public layer names stable.
2. Never model the Brain as a capability or an eleventh layer.
3. Keep model providers behind `models/` and the Brain interface.
4. Keep capabilities independently versioned, tested and traceable.
5. Evolution proposals must pass Verification & Validation and Governance before activation.
6. Keep user/runtime data and secrets out of source control.
7. Preserve baseline/SPS experimental separation so results remain reproducible.
