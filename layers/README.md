# SPS-CA Layer Architecture

SPS-CA uses ten canonical layers. The names below are authoritative and must not drift. The implementation packages use the corresponding `*_core` names.

| # | Canonical layer | Implemented sub-components |
|---|---|---|
| 1 | **Software DNA Core** | DNA Policy Rules; Software DNA Model; Capability Contract Templates |
| 2 | **Governance Core** | Governance Gate; Risk Assessment; Compliance & Decision Audit |
| 3 | **Cognitive core** | Cognitive Reasoning; LLM Provider Interface; Project Analyzer; Cognitive Data Models |
| 4 | **Knowledge core** | Knowledge Core; Knowledge Snapshot; Knowledge Validation |
| 5 | **Experience core** | Experience Log; Long-Term Learning; Experience Data Models |
| 6 | **Meta-learning core** | Capability Evaluator; Meta-Learner; Strategy Policy; A/B Experimentation; Optimization Cycle Controller |
| 7 | **Adaptation core** | Adaptation Engine; Adaptation Records; Contextual Strategy Adjustment |
| 8 | **Evolution core** | Controlled Evolution Engine; Evolution Cycle; Capability Gap Planning; SPS Growth Decision; Evolution Evidence; Evolution Transaction; Evolution Execution Authority; Self-Programming; Capability Retirement |
| 9 | **Verification & Validation Core** | Validation Engine; Validation Data Models; Sandbox & Test Execution |
| 10 | **Execution Core** | Execution Engine; Execution Data Models; Action Execution |

## Flow

```text
USER prompt + code/file
        ↓
CanonicalSPSPipeline
        ↓
L1 Software DNA Core → L2 Governance Core
        ↓
L3 Cognitive core ← separate SPS-CA Brain
        ↓
L4 Knowledge core → L5 Experience core → L6 Meta-learning core
        ↓
L7 Adaptation core → L8 Evolution core
        ↓
L9 Verification & Validation Core → Governance revisit → DNA check
        ↓
L10 Execution Core
        ↓
result + modified code + trace/evidence
        ↓
Experience / future evolution
```

### Growth rule
`DISAGREEMENT ≠ CAPABILITY CREATION`. Disagreement is evidence. Layer 8's **SPS Growth Decision** evaluates reuse, adaptation, composition, improvement, creation, or deferral using accumulated evidence and governance constraints.

The Brain is a separate replaceable model service, not Layer 11 and not a capability. `layers/architecture.py` is the machine-readable source of truth consumed by UI and tests.
