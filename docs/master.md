# SPS-CA — Self-Programming Code Assistant

SPS-CA is a research coding assistant intended to demonstrate how a conventional AI coding assistant can be extended with persistent experience, adaptation, reusable capabilities and governed self-growth.

## Three distinct parts

```text
SPS-CA
├── Ten architectural layers
├── Brain — replaceable AI intelligence
└── Capability system — executable SPS skills
```

The Brain is not a layer and not a capability. It performs language inference, intent classification, reasoning and planning through the provider abstraction.

## Ten-layer SPS architecture

1. Software DNA Core
2. Governance Core
3. Cognitive core
4. Knowledge core
5. Experience core
6. Meta-learning core
7. Adaptation core
8. Evolution core
9. Verification & Validation Core
10. Execution Core

See `docs/ARCHITECTURE.md` for responsibilities, implemented sub-components and runtime boundaries.

## Canonical Stage-0 capabilities

Stage 0 has exactly ten focused capabilities:

| ID | Capability | Primary intent |
|---|---|---|
| CAP-001 | Code Generation | code_generation |
| CAP-002 | Code Modification | code_modification |
| CAP-003 | Code Explanation & Analysis | analysis |
| CAP-004 | Bug Detection & Diagnosis | bug_diagnosis |
| CAP-005 | Bug Fixing | bug_fixing |
| CAP-006 | Refactoring & Optimization | refactoring |
| CAP-007 | Test Generation | test_generation |
| CAP-008 | Documentation Generation | documentation |
| CAP-009 | Code Validation & Review | validation |
| CAP-010 | Project/File Operations | project_operations |

The portfolio is deliberately specific. A code-generation request is not a testing request. A request to find a bug is not a request to fix it. This separation makes Brain decisions testable and explainable.

## Intent-safe planning

```text
Prompt + working source
        ↓
Brain language inference
        ↓
Brain intent classification
        ↓
Eligible capability filter
        ↓
LLM plan over eligible capabilities
        ↓
Post-plan eligibility validation
        ↓
Capability execution
        ↓
Verification / Governance / Execution
```

## Evolution and SPS Growth Decision

CAP-001 through CAP-010 are reserved for the initial baseline. Layer 8 generated capabilities start at CAP-011. Growth is evidence-driven: `DISAGREEMENT ≠ CAPABILITY CREATION`. The Evolution core's SPS Growth Decision can choose reuse, adapt, compose, improve, create, or defer after evaluating capability evidence, recurrence, context and governance constraints.

## Research goal

The research question is whether a coding assistant can improve repeated-task behavior through structured experience, strategy evaluation, adaptation and reusable capability evolution while remaining governed and verifiable.
