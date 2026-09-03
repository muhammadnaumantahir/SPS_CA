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

1. Software DNA
2. Governance
3. Cognitive
4. Knowledge
5. Experience
6. Meta-Learning
7. Adaptation
8. Evolution
9. Verification & Validation
10. Execution

See `docs/ARCHITECTURE.md` for responsibilities and runtime boundaries.

## Canonical Stage-0 capabilities

Stage 0 now has exactly ten focused capabilities:

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

The request flow is:

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

For example, `write Python code to add, subtract, multiply and divide numbers` is classified as `code_generation` and routes to CAP-001. CAP-007 is excluded.

## Evolution

CAP-001 through CAP-010 are reserved for the initial baseline. Layer 8 generated capabilities start at CAP-011. Existing generated history is preserved by migration rather than reusing canonical IDs.

## Research goal

The research question is whether a coding assistant can improve repeated-task behavior through structured experience, strategy evaluation, adaptation and reusable capability evolution while remaining governed and verifiable.
