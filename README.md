# SPS-CA — Self-Programming Code Assistant

SPS-CA is a self-programming coding assistant built around a ten-layer Self-Programming Software (SPS) architecture. The Brain is replaceable and separate from executable capabilities.

## Brain and SPS components

The **Brain is not an SPS layer and is not a capability**. It is a replaceable intelligence service used by the Cognitive core for request understanding, intent classification, reasoning and planning support.

The ten canonical layer names are fixed. New functionality is added as sub-components; layer names are never renamed.

## Canonical SPS architecture

| # | Layer Name | Purpose / Core Capability | Sub-Components |
|---|---|---|---|
| 1 | **Software DNA Core** | Absolute source of truth for constraints and meta-rules | Goals, Policies, Constraints, Learning Rules, Repair Rules, Safety Rules, Ethical Rules, Evolution Rules, Meta-Rules |
| 2 | **Governance Core** | Authorizes proposed changes against Software DNA | Authorization, Evolution Approval, Compliance Checking, Risk Management |
| 3 | **Cognitive core** | Synthesizes goals/system state into reasoning and plans | Goal Manager, Reasoning Engine, Planning Engine, Decision Engine, Explainability Engine |
| 4 | **Knowledge core** | Manages structured, evolving domain knowledge | Knowledge Base, Knowledge Acquisition Engine, Knowledge Validation, Knowledge Evolution |
| 5 | **Experience core** | Stores feedback and runtime signals as historical memory | Memory, Feedback, Monitoring, Learning Engine |
| 6 | **Meta-learning core** | Evaluates and improves the system's learning process | Learning Evaluation, Strategy Optimization, Learning Improvement |
| 7 | **Adaptation core** | Shifts behavior by context without source-code modification | Context Awareness, Personalization, Capability Activation, Strategy Selection |
| 8 | **Evolution core** | Engine of genuine structural self-growth | Self-Modification, Self-Regeneration, Capability Preservation, Capability Differentiation, Capability Creation, **SPS Growth Decision** |
| 9 | **Verification & Validation Core** | Screens new/mutated code before production | Testing, Simulation, Safety Validation, Performance Validation |
| 10 | **Execution Core** | Translates validated decisions into observable action | Action Executor, Services, APIs, User Interaction |

`SPS Growth Decision` is a sub-component of **Evolution core**, not layer 11.

## Capabilities

The system starts with ten intent-specific canonical capabilities:

1. CAP-001 — Code Generation
2. CAP-002 — Code Modification
3. CAP-003 — Code Explanation & Analysis
4. CAP-004 — Bug Detection & Diagnosis
5. CAP-005 — Bug Fixing
6. CAP-006 — Refactoring & Optimization
7. CAP-007 — Test Generation
8. CAP-008 — Documentation Generation
9. CAP-009 — Code Validation & Review
10. CAP-010 — Project/File Operations

Generated capabilities use CAP-011 and above and retain provenance and lineage.

## Canonical user execution flow

The browser UI and model-backed scenario runner share one entry point: `CanonicalSPSPipeline`.

```text
                         USER
                          │
                 Prompt + Code/File
                          │
                          ▼
              CanonicalSPSPipeline
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
        ▼                                   ▼
   SPS Architecture                    Brain boundary
        │                                   │
        ├─ L1 Software DNA Core             │
        ├─ L2 Governance Core               │
        ├─ L3 Cognitive core ◄────── Brain  │
        ├─ L4 Knowledge core                │
        ├─ L5 Experience core               │
        ├─ L6 Meta-learning core            │
        ├─ L7 Adaptation core               │
        ├─ L8 Evolution core ─► Capability  │
        │                    reuse/create   │
        ├─ L9 Verification & Validation Core│
        └─ L10 Execution Core               │
                          │
                          ▼
              Result + Modified Code
                          │
                          ▼
             Experience / Trace / Evidence
                          │
                          ▼
                  Future Evolution
```

## SPS Growth Decision — Layer 8 is a decision-maker

Layer 8 is **not** a disagreement counter. `SPS Growth Decision` evaluates evidence and chooses the least-structural action justified by the current state:

- `reuse` — existing capability is sufficient.
- `adapt` — contextual/runtime adaptation is sufficient.
- `compose` — an established combination should become reusable.
- `improve` — strengthen an existing capability instead of duplicating it.
- `create` — a genuine capability gap or persistent unmet pattern justifies structural growth.
- `defer` — evidence is insufficient or growth should wait.

### Critical SPS invariant

> **DISAGREEMENT ≠ CAPABILITY CREATION**

A disagreement is experience evidence. It is analyzed together with capability matching, recurrence, adaptation, composition and improvement evidence. Only a reasoned Layer-8 `create` decision can initiate capability generation.

```text
Disagreement / Gap / Performance Signal
                  │
                  ▼
          Experience Evidence
                  │
                  ▼
       Meta-Learning Analysis
                  │
                  ▼
         Brain + Cognitive Reasoning
                  │
                  ▼
          SPS Growth Decision
                  │
      ┌───────────┼────────────┐
      ▼           ▼            ▼
    Reuse       Adapt        Evolve
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
                 Improve    Compose     Create
                                           │
                                           ▼
                                  Govern → Generate
                                  → Test → Register
```

Examples of growth evidence include a previously unknown task with no suitable capability, repeated unmet patterns, recurring failure despite adaptation, repeated capability compositions that deserve a reusable skill, or a capability requiring structural improvement. A single disagreement is not sufficient by itself.

## Feedback and capability growth

`agree` strengthens evidence for reuse. `disagree` is recorded as evidence and analyzed by `SPS Growth Decision`; it does not directly create a capability.

## Self-programming

SPS-CA can use observed failures and capability gaps as evidence for controlled self-programming. Candidate changes pass through Software DNA, Governance, Verification & Validation and controlled Execution with rollback safeguards.

## Web application

The browser UI is chat-first. Users can provide prompts and code/files, see the Brain boundary, selected/generated capability, validation/governance/DNA/execution state, and the canonical ten-layer trace. Growth and Evolution views expose capability lineage and persisted why/what/when/how evidence.

## Evaluation

1. `testing/test_sps_scenarios.py` — deterministic 500-case routing/language contract.
2. `evaluation/scenario_runner.py --live-evolve` — model-backed execution through the canonical SPS pipeline, feedback recording and Layer-8 evolution evidence.

## Documentation

- `docs/ARCHITECTURE.md` — canonical architecture and SPS Growth Decision
- `docs/PIPELINE.md` — request, feedback, learning and self-programming flow
- `docs/capabilities/CANONICAL_CAPABILITIES.md` — capability contracts
- `docs/master.md` — research overview and SPS model
- `docs/scenarios.md` — evaluation scenarios
- `docs/SELF_PROGRAMMING.md` — controlled self-programming design
- `docs/WEB_UI_GUIDE.md` — browser workspace guide
- `SETUP.md` — local and Colab setup
- `REQUIREMENTS.md` — environment requirements

`layers/architecture.py` is the authoritative machine-readable layer vocabulary.
