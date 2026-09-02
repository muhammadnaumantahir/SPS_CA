# SPS-CA Request Pipeline

SPS-CA uses ten architectural layers. The Brain is a separate AI intelligence service, used primarily by the Cognitive Layer, and is neither a layer nor a capability.

```text
User message + current code + conversation
                    ↓
L1 Software DNA Layer
                    ↓
L2 Governance Layer (preflight policy/risk)
                    ↓
L3 Cognitive Layer ↔ SPS-CA Brain
                    ↓
L4 Knowledge Layer
                    ↓
L5 Experience Layer
                    ↓
L6 Meta-Learning Layer
                    ↓
L7 Adaptation Layer
                    ↓
L8 Evolution Layer (when SPS self-growth is relevant)
                    ↓
Capability system: select / compose reusable SPS skills
                    ↓
L9 Verification & Validation Layer
                    ↓
L2 Governance Layer (final authorization)
                    ↓
L10 Execution Layer
                    ↓
Result + trace → Experience → learning/adaptation/evolution
```

## Brain boundary

The Brain provides prompt analysis, reasoning, planning, code generation, debugging, strategy analysis, failure analysis and capability-selection reasoning. Ollama is the initial provider through the provider-neutral `models/` interface. The Brain does not execute code or approve its own changes.

## Capabilities

Capabilities are independent executable SPS skills. Current Stage 0 seeded capabilities include:

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

Generated capabilities are created by the Evolution path and recorded separately with lineage evidence.

## Conversational coding

The top page is a multi-turn coding assistant. Every turn carries the current working source and recent conversation to the Brain, so feedback can refer to earlier work.

```text
Turn 1: Add input validation.
Turn 2: Also reject negative values.
Turn 3: Now add tests for those cases.
Turn 4: Allow zero again; keep the other validation.
```

## SPS self-programming

A user-project change is normal coding-assistant behavior. Self-programming is demonstrated when SPS-CA improves its own reusable capability system:

```text
Repeated limitation/failure
        ↓
Experience Layer
        ↓
Meta-Learning Layer
        ↓
Adaptation Layer
        ↓
Brain-assisted Evolution Layer
        ↓
New capability candidate
        ↓
L9 Verification & Validation Layer
        ↓
L2 Governance
        ↓
Capability Registry + Lineage
        ↓
Reusable capability
```

## Trace requirements

The runtime trace should retain the request/turn, source context, Brain plan, layer participation, selected capabilities, capability outcomes, verification evidence, governance decision, execution/rollback outcome, experience record and evolution lineage when applicable.

Detailed experimental scenarios are maintained separately in `docs/scenarios.md`.
