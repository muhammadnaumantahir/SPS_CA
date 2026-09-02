# SPS-CA Architecture v2

## 1. Purpose

SPS-CA is a research prototype for Self-Programming Software expressed as a coding assistant. Its purpose is not merely to generate code. It provides a governed, traceable and reversible architecture in which the system can accumulate experience, improve strategy selection, adapt, and eventually develop reusable capabilities.

The architecture has **exactly ten layers**. The **Brain is not a layer and is not a capability**. It is a replaceable AI/model service used primarily by the Cognitive core for reasoning, prompt analysis, planning, code generation, debugging and strategy analysis.

## 2. Canonical ten-layer model

| Layer | Public name | Responsibility |
|---|---|---|
| L1 | **Software DNA layer** | Identity, invariants, constraints and seed-system rules |
| L2 | **Governance layer** | Policy, risk, approval/rejection and audit decisions |
| L3 | **Cognitive core** | Prompt understanding, reasoning, planning and code context |
| L4 | **Knowledge core** | Structured knowledge about code, capabilities, patterns and system state |
| L5 | **Experience core** | Persistent outcomes, failures, successes, traces and lessons |
| L6 | **Meta-learning core** | Learns which strategies/capabilities work under which conditions |
| L7 | **Adaptation core** | Adjusts strategy and capability composition to current context |
| L8 | **Evolution core** | Designs, generates and improves SPS capabilities |
| L9 | **Verification & Validation** | Syntax, tests, regression, sandbox and evidence checks |
| L10 | **Execution layer** | Controlled application of approved changes and tool operations |

The canonical vocabulary is implemented in `layers/architecture.py`. Existing Python package paths are kept stable where necessary for compatibility; package names are implementation details and must not redefine the research-layer names.

## 3. Brain boundary

```text
                       SPS-CA
                          │
             ┌────────────┴────────────┐
             │                         │
       Ten architectural layers       Brain
             │                         │
             │                 Ollama / other AI
             │                         │
             └──────────────┬──────────┘
                            │
                     Capability system
                            │
                 Seed + generated capabilities
```

The Brain is provider-neutral. Ollama is the initial local provider, but another model can be introduced through `models/` without becoming a new SPS capability or layer.

The Brain can:
- analyze a user prompt;
- reason about code and context;
- produce a task/strategy plan;
- select and order capabilities from the registry;
- generate or repair code when a capability delegates generation to it;
- analyze failures and propose recovery strategies;
- support Evolution when repeated limitations justify a new capability.

The Brain does **not** execute code, approve its own changes, bypass Validation, or become `CAP-001`.

## 4. Capability boundary

Capabilities are executable SPS skills. They are independent of the Brain and are registered/versioned separately.

Stage 0 contains the initial seeded capabilities, for example:

- CAP-001 — Simple Bug Detection
- CAP-002 — Syntax Error Fix
- CAP-003 — Unit Test Generation
- CAP-004 — Loop Optimization
- CAP-005 — Error Handling Pattern
- CAP-006 — Unused Variable Removal
- CAP-007 — Type Annotation Addition
- CAP-008 — Documentation Generation
- CAP-010 — generated Parse Error Handler (existing evolution artifact)
- CAP-011 — Natural Language Code Modification

The exact portfolio may grow as SPS-CA evolves. The Brain chooses from active capabilities; it does not replace the capability registry.

`capabilities/` and its registry/lineage services are supporting infrastructure, not an eleventh architectural layer.

## 5. Request lifecycle

For a normal coding request:

```text
User prompt + source
        ↓
L1 Software DNA layer
        ↓
L2 Governance layer (preflight constraints)
        ↓
L3 Cognitive core
        ↓
Brain reasoning / planning
        ↓
L4 Knowledge core
        ↓
L5 Experience core
        ↓
L6 Meta-learning core
        ↓
L7 Adaptation core
        ↓
L8 Evolution core (when evolution is relevant)
        ↓
Capability selection/composition
        ↓
L9 Verification & Validation
        ↓
L2 Governance final decision
        ↓
L10 Execution layer
        ↓
L5 Experience + trace
        ↓
L6 Meta-learning / L8 Evolution feedback
```

The numbered layers are architectural responsibilities. A layer may participate at more than one point in a controlled lifecycle; for example, Governance provides both preflight policy context and a final approval decision.

## 6. Self-programming lifecycle

Only self-change should be treated as SPS evolution:

```text
Repeated task/failure pattern
        ↓
Experience core
        ↓
Meta-learning core
        ↓
Adaptation core
        ↓
Brain-assisted Evolution core
        ↓
New capability candidate
        ↓
Verification & Validation
        ↓
Governance approval
        ↓
Capability Registry + Lineage
        ↓
Reusable capability
```

A user-project modification is **not automatically self-programming**. The research distinction is between changing the target project and changing SPS-CA's own reusable capability set.

## 7. Evaluation strategy

SPS-CA must be evaluated progressively:

1. **Baseline A — Naive coding assistant:** same Brain/model, direct request + code.
2. **Baseline B — Tool-augmented coding assistant:** same Brain/model plus deterministic analysis/testing tools, but no SPS learning/evolution.
3. **SPS-CA Stage 0:** ten-layer architecture with fixed seed capabilities.
4. **SPS-CA later stage:** experience-informed adaptation and generated/reused capabilities.

The same coding scenarios should be exercised across controlled projects/languages. Metrics should include correctness, success rate, time, validation failures, retries, capability selection, reuse, composition, generated capabilities, lineage, rollback and governance decisions.

The central research question becomes measurable:

> Does adding the SPS architecture allow the coding assistant to improve future task handling and develop/reuse capabilities compared with the same-model coding baselines?

## 8. Implementation boundaries

- `layers/` — ten architectural responsibilities.
- `brain/` — replaceable AI intelligence service; never a capability.
- `models/` — provider/model abstraction.
- `capabilities/` — seed/generated executable skills, registry and lineage.
- `coding/` — repository and code intelligence.
- `validation/` — verification infrastructure used by L9.
- `governance/` — policy infrastructure used by L2.
- `execution/` — controlled runtime infrastructure used by L10.
- `memory/`, `data/`, `analytics/` — supporting runtime/evidence services.
- `ui/` — presentation and observability; never the system of record.

## 9. Safety boundary

Generated SPS capabilities and SPS self-modifications must never bypass Validation or Governance. Runtime user projects, credentials and model secrets remain outside source control.
