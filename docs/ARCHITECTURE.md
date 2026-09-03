# SPS-CA Architecture

SPS-CA separates ten SPS responsibilities from the replaceable AI Brain and the executable capability system.

## Ten-layer model

| # | Layer | Purpose |
|---|---|---|
| L1 | Software DNA | Constraints and meta-rules |
| L2 | Governance | Authorizes changes |
| L3 | Cognitive | Reasoning, planning, decisions |
| L4 | Knowledge | Structured evolving knowledge |
| L5 | Experience | Feedback and historical runtime signals |
| L6 | Meta-Learning | Evaluates learning strategies |
| L7 | Adaptation | Context-dependent behavior selection |
| L8 | Evolution | Structural self-growth and capability creation |
| L9 | Verification & Validation | Tests and safety checks in a boundary |
| L10 | Execution | Controlled real-world action |

## Brain boundary

The Brain is a replaceable AI service, currently backed by Ollama. It performs prompt understanding, language inference, intent classification, planning and reasoning. It is not a `CAP-NNN` and does not execute code.

## Capability boundary

The Stage-0 capability portfolio is exactly the ten capabilities in `docs/capabilities/CANONICAL_CAPABILITIES.md`. Capabilities are executable skills; the Brain selects them but remains separate from them.

Generated capabilities are extensions of the baseline. IDs CAP-001..CAP-010 are never allocated by Evolution.

## Request flow

```text
User prompt + working code
          ↓
Software DNA / Governance context
          ↓
Cognitive Layer + Brain
          ↓
Language inference + intent classification
          ↓
Intent-eligible capability selection
          ↓
Knowledge / Experience / Meta-Learning / Adaptation context
          ↓
Capability execution
          ↓
Verification & Validation
          ↓
Governance / Execution
          ↓
Experience trace
```

For a plain code-creation request, Test Generation is excluded before the model selects capabilities. A user disagreement becomes evidence for the Experience and Evolution path; it is not an automatic capability-creation command.

## Repository boundaries

- `brain/` — replaceable intelligence and planning
- `capabilities/` — canonical and generated executable skills
- `layers/` — SPS architectural responsibilities
- `core/` — orchestration and conversation services
- `validation/`, `governance/`, `execution/` — controlled infrastructure
- `ui/` — presentation and observability
- `docs/` — research and implementation documentation
