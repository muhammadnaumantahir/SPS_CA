# SPS-CA Architecture v2

## 1. Purpose

SPS-CA is a research prototype for Self-Programming Software expressed as a coding assistant. Its purpose is not merely to generate code. It provides a governed, traceable and reversible architecture in which the system can accumulate experience, improve strategy selection, adapt, and eventually develop reusable capabilities.

The architecture has **exactly ten layers**. The **Brain is not a layer and is not a capability**. It is a replaceable AI/model service used primarily by the Cognitive core for reasoning, prompt analysis, planning, code generation, debugging and strategy analysis.

## 2. Canonical ten-layer model

| # | Public name | Core purpose | Optional sub-components |
|---|---|---|---|
| L1 | **Software DNA layer** | Acts as the absolute source of truth, defining constraints and meta-rules that all evolution must obey. | Goals, Policies, Constraints, Learning Rules, Repair Rules, Safety Rules, Ethical Rules, Evolution Rules, Meta-Rules |
| L2 | **Governance layer** | Executive gatekeeper that authorizes proposed changes against the Software DNA before deployment. | Authorization, Evolution Approval, Compliance Checking, Risk Management |
| L3 | **Cognitive core** | Synthesizes goals and system state into tactical decisions, reasoning, and plans. | Goal Manager, Reasoning Engine, Planning Engine, Decision Engine, Explainability Engine |
| L4 | **Knowledge core** | Manages structured, evolving domain knowledge. | Knowledge Base, Knowledge Acquisition Engine, Knowledge Validation, Knowledge Evolution |
| L5 | **Experience core** | Collects and stores feedback and runtime signals as historical memory. | Memory, Feedback, Monitoring, Learning Engine |
| L6 | **Meta-learning core** | Evaluates and improves the system's own learning process. | Learning Evaluation, Strategy Optimization, Learning Improvement |
| L7 | **Adaptation core** | Shifts behavior instantly by context, without modifying source code. | Context Awareness, Personalization, Capability Activation, Strategy Selection |
| L8 | **Evolution core** | The engine of genuine structural self-growth. | Self-Modification, Self-Regeneration, Capability Preservation, Capability Differentiation, Capability Creation |
| L9 | **Verification & Validation** | Screens new or mutated code in a sandbox before it reaches production. | Testing, Simulation, Safety Validation, Performance Validation |
| L10 | **Execution layer** | Translates validated decisions into real, observable action. | Action Executor, Services, APIs, User Interaction |

The canonical vocabulary is implemented in `layers/architecture.py` and exposed to the web dashboard/API.

### Sub-components are modular

The sub-components above are recommended architectural building blocks, not a requirement that every SPS-CA deployment implement all of them at once. A sub-component may be added, replaced, deferred, or omitted while the parent layer retains its core responsibility.

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

The Brain does **not** execute code, approve its own changes, bypass Verification & Validation, or become `CAP-001`.

## 4. Capability boundary

Capabilities are executable SPS skills. They are independent of the Brain and are registered/versioned separately.

Stage 0 contains the initial seeded capabilities. The exact portfolio may grow as SPS-CA evolves.

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

Generated SPS capabilities and SPS self-modifications must never bypass Verification & Validation or Governance. Runtime user projects, credentials and model secrets remain outside source control.
