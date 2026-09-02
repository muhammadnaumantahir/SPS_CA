# SPS-CA Request Pipeline

Every user coding request follows a deterministic lifecycle through the 10-layer architecture. The Brain (separate from the layers) provides the intelligence for reasoning, planning, and capability selection.

```text
User Prompt + Source Code
        │
        ▼
L1  Software DNA layer
        │  load constraints, policies, safety rules
        ▼
L2  Governance layer (preflight)
        │  check DNA preconditions, risk assessment
        ▼
L3  Cognitive core
        │  ← Brain (Ollama / other AI model)
        │  reasoning, intent understanding, planning
        │  select ordered capability sequence
        ▼
L4  Knowledge core
        │  structured domain knowledge context
        ▼
L5  Experience core
        │  historical memory, failure patterns
        ▼
L6  Meta-learning core
        │  strategy evaluation, learning improvement
        ▼
L7  Adaptation core
        │  context awareness, capability activation
        ▼
L8  Evolution core (when evolution is triggered)
        │  generate new capability candidate
        ▼
Capability selection / composition
        │  CAP-001 ... CAP-011 (seeded + generated)
        ▼
L9  Verification & Validation
        │  sandboxed testing, regression detection
        ▼
L2  Governance (final decision)
        │  approve / reject with rationale
        ▼
L10 Execution layer
        │  apply changes, monitor, rollback if needed
        ▼
Result + trace
        │  update L5 Experience, L6 Meta-learning
        ▼
Experience + learning feedback loop
```

## Brain boundary

The Brain is a **separate AI intelligence service**, not a layer and not a capability.

```text
              SPS-CA
                 │
    ┌────────────┴────────────┐
    │                         │
  Ten architectural layers    Brain
    │                         │
    │                 Ollama / other AI
    │                         │
    └──────────────┬──────────┘
                   │
             Capability system
                   │
        Seed + generated capabilities
```

The UI must not use keyword priority rules to override the Brain. The Brain interprets the request, reasons about context, and selects the downstream capability sequence. Selected capability IDs are validated against the active registry before execution.

The Brain can be swapped (Ollama → Qwen → Llama → DeepSeek → cloud API) through `models/` without changing the SPS architecture or capabilities.

## Capability numbering (Stage 0 seed portfolio)

| ID | Role |
|---|---|
| CAP-001 | Simple Bug Detection |
| CAP-002 | Syntax Error Fix |
| CAP-003 | Unit Test Generation |
| CAP-004 | Loop Optimization |
| CAP-005 | Error Handling Pattern |
| CAP-006 | Unused Variable Removal |
| CAP-007 | Type Annotation Addition |
| CAP-008 | Documentation Generation |
| CAP-009 | Natural Language Code Modification |
| CAP-010+ | Generated capabilities (from evolution) |

The local Brain adapter defaults to `qwen2.5-coder:7b` as documented in `REQUIREMENTS.md`.
