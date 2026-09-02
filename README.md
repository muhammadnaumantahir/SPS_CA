# SPS-CA — Self-Programming Code Assistant

SPS-CA is a research coding assistant for studying **Self-Programming Software (SPS)**. It combines a conventional AI coding workflow with a ten-layer SPS architecture, a separate replaceable AI Brain, reusable executable capabilities, persistent experience and a controlled route to capability evolution.

## The model

```text
User message + code + conversation
                 ↓
        SPS-CA ten-layer architecture
                 ↕
       Brain (Ollama / other AI)
                 ↓
       Capability system
                 ↓
 Verification & Validation → Governance → Execution
                 ↓
       Experience / feedback
                 ↺ learning / adaptation / evolution
```

**Brain ≠ capability.** The Brain is an intelligence service. Capabilities are executable SPS skills. Neither is an additional architectural layer.

## Ten architectural layers

1. **Software DNA Layer**
2. **Governance Layer**
3. **Cognitive Layer**
4. **Knowledge Layer**
5. **Experience Layer**
6. **Meta-Learning Layer**
7. **Adaptation Layer**
8. **Evolution Layer**
9. **Verification & Validation Layer**
10. **Execution Layer**

Each layer has a defined responsibility and optional sub-components. The canonical machine-readable definition is in `layers/architecture.py`.

## Conversational coding assistant

The top page is designed as a normal coding-assistant chat rather than a one-shot form. The user can provide code and a request, receive a result, and continue with feedback in the same session.

```text
User: Add input validation.
SPS-CA: [result]
User: Also reject negative values.
SPS-CA: [uses current code + recent conversation]
User: Now add tests.
SPS-CA: [new capability plan]
```

The current working source and recent conversation are passed to the Brain on each turn. Experience records can also be supplied as reasoning context.

## Stage 0 capabilities

Stage 0 starts with seeded SPS skills, including:

- CAP-001 — Simple Bug Detection
- CAP-002 — Syntax Error Fix
- CAP-003 — Unit Test Generation
- CAP-004 — Loop Optimization
- CAP-005 — Error Handling Pattern
- CAP-006 — Unused Variable Removal
- CAP-007 — Type Annotation Addition
- CAP-008 — Documentation Generation
- CAP-011 — Natural Language Code Modification

Later SPS states can create or improve reusable capabilities through the Evolution → Verification & Validation → Governance → Registry path.

## Research distinction

A normal coding-assistant change to a user's project is not, by itself, self-programming.

The SPS research behavior is:

```text
Repeated limitation/failure
        ↓
Experience
        ↓
Meta-learning
        ↓
Adaptation
        ↓
Evolution reasoning
        ↓
New capability candidate
        ↓
Verification & Validation Layer
        ↓
Governance
        ↓
Capability Registry + lineage
        ↓
Reusable capability
```

The project therefore evaluates both **basic coding-assistant behavior** and **SPS behavior**.

## Evaluation

Controlled Python, Java and TypeScript projects are used to compare:

- Baseline A — naive/model-only coding assistant
- Baseline B — tool-augmented coding assistant without SPS learning/evolution
- SPS-CA Stage 0 — fixed capabilities and ten-layer architecture
- later SPS state — experience-informed adaptation and evolved/reused capabilities

The detailed test plan is in `docs/scenarios.md` and executable scenario definitions are in `evaluation/scenarios.py`.

## Run locally

Install dependencies and Ollama as described in `SETUP.md`.

### Web UI

```bash
python ui/web_app.py
```

Open `http://127.0.0.1:8080`.

### CLI

```bash
python ui/cli_interface.py
```

## Project structure

```text
SPS_CA/
├── brain/                 # separate AI intelligence service
├── layers/                # ten SPS architectural responsibilities
├── capabilities/          # executable SPS skills
├── core/                  # shared orchestration
├── models/                # provider/model abstraction
├── coding/                # code/repository intelligence
├── validation/            # validation infrastructure
├── governance/            # governance infrastructure
├── execution/             # execution infrastructure
├── projects/              # controlled evaluation projects
├── baselines/             # comparison assistants
├── evaluation/            # scenario runner and metrics
├── analytics/             # evidence/analytics support
├── memory/                # runtime memory support
├── ui/                    # conversational web UI + CLI
└── docs/                  # architecture, master overview and scenarios
```

## Documentation

- `docs/master.md` — what SPS-CA is, its framework, features and architecture
- `docs/ARCHITECTURE.md` — canonical ten-layer definitions and boundaries
- `docs/scenarios.md` — what will be tested and what evidence is required
- `docs/PIPELINE.md` — request, feedback and self-programming lifecycle
- `SETUP.md` — installation and local setup
- `REQUIREMENTS.md` — system/software requirements

## Security

Never commit API keys, personal access tokens, passwords or other secrets. Runtime projects, conversations, model caches and generated data should remain outside Git whenever practical.
