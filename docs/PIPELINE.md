# SPS-CA Request and Feedback Pipeline

SPS-CA is a ten-layer self-programming coding assistant with a separate AI Brain and a separate capability system. The Brain is not a capability and there is no `CAP-001 Prompt Processing` stage.

## Conversational request flow

```text
User message + current working code + recent conversation
                           ↓
                Software DNA layer
                           ↓
                Governance preflight
                           ↓
                  Cognitive core
                           ↕
                     SPS-CA Brain
             (Ollama / other AI provider)
                           ↓
                  Knowledge core
                           ↓
                 Experience core
                           ↓
               Meta-learning core
                           ↓
                 Adaptation core
                           ↓
          Evolution core when self-growth is relevant
                           ↓
             Capability selection/composition
                           ↓
            Verification & Validation
                           ↓
             Governance final decision
                           ↓
                  Execution layer
                           ↓
                New working state
                           ↓
            Experience / trace feedback
```

The system can return to the Cognitive core, Brain, Knowledge, Experience, Meta-learning or Adaptation responsibilities when a failure or new user feedback requires another reasoning cycle.

## Brain boundary

The Brain is a replaceable intelligence service. Its responsibilities include prompt analysis, code understanding, reasoning, planning, code generation, debugging, failure analysis, strategy selection and support for evolution reasoning.

Ollama is the initial local provider. Other providers can be placed behind `models/` without becoming SPS capabilities.

The Brain does not execute code, approve its own changes or appear in the capability registry as a `CAP-NNN`.

## Capability boundary

Capabilities are executable SPS skills selected or composed by the Brain and the SPS layers.

The current Stage 0 seed portfolio contains:

| ID | Capability |
|---|---|
| CAP-001 | Simple Bug Detection |
| CAP-002 | Syntax Error Fix |
| CAP-003 | Unit Test Generation |
| CAP-004 | Loop Optimization |
| CAP-005 | Error Handling Pattern |
| CAP-006 | Unused Variable Removal |
| CAP-007 | Type Annotation Addition |
| CAP-008 | Documentation Generation |
| CAP-011 | Natural Language Code Modification |

A generated capability is added through the Evolution → Verification & Validation → Governance → Registry path, not by treating the Brain as a new capability.

## Multi-turn behavior

A conversation keeps both the recent user/assistant messages and the current working source.

```text
Turn 1: "Add input validation."
        ↓
SPS-CA changes working code
        ↓
Turn 2: "Also reject negative values."
        ↓
Brain sees previous turn + current working code
        ↓
new capability plan
        ↓
updated working code
        ↓
Turn 3: "Now add tests."
```

A follow-up does not start from the original source unless the user explicitly resets the working state.

## Self-programming feedback loop

Normal user-code changes are coding-assistant behavior. SPS self-programming is demonstrated when the SPS itself develops or changes reusable capabilities:

```text
Repeated limitation/failure
          ↓
Experience core
          ↓
Meta-learning core
          ↓
Adaptation core
          ↓
Brain-assisted Evolution core
          ↓
Capability candidate
          ↓
Verification & Validation
          ↓
Governance approval
          ↓
Capability Registry + lineage
          ↓
Later capability reuse
```

## Observability

A turn should leave enough information to reconstruct the decision:

- conversation context
- current source
- Brain provider/model
- Brain intent/reasoning
- selected capability sequence
- capability outcomes
- validation evidence
- governance decision
- execution result
- experience record
- evolution/lineage evidence when applicable

The executable implementation is shared by the web UI and CLI through `core/assistant_service.py` so the interfaces do not implement separate routing logic.
