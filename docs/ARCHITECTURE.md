# SPS-CA Architecture

## 1. Purpose

SPS-CA is a research implementation of Self-Programming Software expressed as a coding assistant. The architecture separates the ten SPS responsibilities from the replaceable AI Brain, executable capabilities, coding infrastructure, runtime experience and user interface.

The ten layers describe **architectural responsibilities**. The Brain is a separate intelligence service and capabilities are separate executable SPS skills.

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

Sub-components are **optional**. A deployment can implement them incrementally without changing the responsibility of the parent layer.

The public vocabulary is implemented by `layers/architecture.py` and exposed to the UI/API. A dedicated `layers/knowledge_core/` module now provides the initial implementation boundary for the Knowledge core.

## 3. Brain boundary

```text
                         SPS-CA
                           │
            ┌──────────────┴──────────────┐
            │                             │
      Ten SPS layers                    Brain
            │                    Ollama / other AI
            │                             │
            └──────────────┬──────────────┘
                           │
                    Capability system
                           │
                Seed + generated capabilities
```

The Brain supports prompt understanding, reasoning, planning, code understanding, code generation, debugging, failure analysis, strategy selection and evolution reasoning. It does not execute code, bypass governance/verification, or appear in the capability registry as a `CAP-NNN`.

## 4. Capability boundary

Capabilities are independent executable SPS skills. The current Stage 0 seed set is described in `docs/master.md` and discovered through `capabilities/seed_registry.py`.

A capability may call the Brain for reasoning or generation, but that does not turn the Brain into a capability.

The Capability Registry and Capability Lineage are supporting subsystems, not additional architectural layers.

## 5. Conversational request lifecycle

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
               Experience / trace feedback
```

A follow-up user message uses the current working source and recent conversational context. Failures may cause another reasoning cycle instead of ending the session.

## 6. Self-programming lifecycle

Self-programming is demonstrated when SPS-CA changes its own reusable capability system rather than merely modifying a user's project:

```text
Repeated limitation or failure
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
Reusable capability
```

## 7. Implementation boundaries

| Area | Responsibility |
|---|---|
| `layers/` | Ten SPS architectural responsibilities |
| `brain/` | Replaceable AI intelligence service |
| `models/` | Provider/model abstraction |
| `capabilities/` | Seed/generated executable SPS skills, registry and lineage |
| `core/` | Shared orchestration and session services |
| `coding/` | Repository and code intelligence |
| `validation/` | Verification infrastructure used by L9 |
| `governance/` | Governance infrastructure used by L2 |
| `execution/` | Controlled execution used by L10 |
| `projects/` | Controlled target projects for evaluation |
| `baselines/` | Comparison coding assistants |
| `evaluation/` | Executable scenario catalog and runners |
| `analytics/` | Evidence and evaluation analytics |
| `memory/` / `experience/` | Runtime memory and experience data |
| `ui/` | Conversational presentation/observability only |

## 8. Runtime conversation state

The web UI maintains a current working source and a bounded recent conversation. The backend receives both on every turn. The shared `core/assistant_service.py` then:

1. builds Knowledge context;
2. supplies recent Experience context;
3. asks the Brain for a capability plan;
4. executes the selected active capabilities;
5. returns the new working source and trace;
6. records the turn as Experience evidence.

The browser is not the system of record for SPS decisions.

## 9. Evaluation architecture

SPS-CA should be compared against a basic coding assistant and a tool-augmented coding assistant using the same target projects and matched scenario intents. Detailed scenarios and evidence requirements are in `docs/scenarios.md`.

Important measures include correctness, success rate, time, retries, validation failures, governance outcomes, capability selection/reuse/composition, experience continuity and capability evolution/lineage.
