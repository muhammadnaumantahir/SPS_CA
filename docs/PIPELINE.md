# SPS-CA Request Pipeline

Every user coding request follows a deterministic entry sequence. The first capability is always **CAP-001 Prompt Processing**.

```text
User Prompt
    |
    v
CAP-001 Prompt Processing
    |
    |  Ollama = reasoning brain
    |  returns ordered allowlisted capability IDs
    v
CAP-002 ... CAP-011 (selected by the brain)
    |
    v
Layer 6 Validation / sandbox
    |
    v
Layer 7 Governance
    |
    v
Layer 10 Execution
    |
    v
Result + trace
```

## Brain rule

The UI must not use keyword priority rules to override the model. CAP-001 is responsible for interpreting the request and choosing the downstream capability sequence. The selected IDs are validated against the active registry before execution.

The local Ollama adapter defaults to `qwen2.5-coder:7b` as documented in `REQUIREMENTS.md`.

## Capability numbering

| ID | Role |
|---|---|
| CAP-001 | Prompt Processing / Ollama brain |
| CAP-002 | Bug Detection |
| CAP-003 | Syntax Error Fix |
| CAP-004 | Unit Test Generation |
| CAP-005 | Loop Optimization |
| CAP-006 | Error Handling |
| CAP-007 | Unused Variable Removal |
| CAP-008 | Type Annotation |
| CAP-009 | Documentation Generation |
| CAP-010 | Generated Parse Error Handler |
| CAP-011 | Natural Language Code Modification |

The directory names of legacy seed implementations are retained for compatibility; their registry IDs define the pipeline order.
