# SPS-CA Layers

The public SPS-CA architecture has **ten layers**. These names are canonical for the UI, documentation, experiments, and trace output. **Layer names must never be renamed; new behavior is added as a sub-component.**

| # | Layer Name | Purpose / Core Capability | Sub-Components |
|---|---|---|---|
| 1 | **Software DNA Core** | Acts as the absolute source of truth, defining constraints and meta-rules that all evolution must obey | Goals, Policies, Constraints, Learning Rules, Repair Rules, Safety Rules, Ethical Rules, Evolution Rules, Meta-Rules |
| 2 | **Governance Core** | Executive gatekeeper that authorizes proposed changes against the Software DNA before deployment | Authorization, Evolution Approval, Compliance Checking, Risk Management |
| 3 | **Cognitive core** | Synthesizes goals and system state into tactical decisions, reasoning, and plans | Goal Manager, Reasoning Engine, Planning Engine, Decision Engine, Explainability Engine |
| 4 | **Knowledge core** | Manages structured, evolving domain knowledge | Knowledge Base, Knowledge Acquisition Engine, Knowledge Validation, Knowledge Evolution |
| 5 | **Experience core** | Collects and stores feedback and runtime signals as historical memory | Memory, Feedback, Monitoring, Learning Engine |
| 6 | **Meta-learning core** | Evaluates and improves the system's own learning process | Learning Evaluation, Strategy Optimization, Learning Improvement |
| 7 | **Adaptation core** | Shifts behavior instantly by context, without modifying source code | Context Awareness, Personalization, Capability Activation, Strategy Selection |
| 8 | **Evolution core** | The engine of genuine structural self-growth | Self-Modification, Self-Regeneration, Capability Preservation, Capability Differentiation, Capability Creation, **SPS Growth Decision** |
| 9 | **Verification & Validation Core** | Screens new or mutated code in a sandbox before it reaches production | Testing, Simulation, Safety Validation, Performance Validation |
| 10 | **Execution Core** | Translates validated decisions into real, observable action | Action Executor, Services, APIs, User Interaction |

## SPS Growth Decision

`SPS Growth Decision` is a **sub-component of Evolution core**, not a new layer. Layer 8 decides whether the system should reuse, adapt, compose, improve, create, or defer based on evidence and reasoning.

**Disagreement is evidence, not an automatic capability-creation command.**

## Sub-components are modular

The table defines the canonical architecture. A sub-component may be added, replaced, deferred, or omitted while the parent layer retains ownership of its responsibility. The ten layer names themselves remain stable.

## Brain boundary

The **Brain is separate from these ten layers**. It is a replaceable AI intelligence service, initially backed by Ollama through `models/`. It supports the Cognitive core with prompt understanding, reasoning, planning, code generation and debugging. It may also support Meta-learning core, Adaptation core and Evolution core reasoning.

The Brain is **not** `CAP-001`, is not assigned a `CAP-NNN` identifier, and is not counted as layer 11.

## Capability boundary

Capabilities are executable SPS skills under `capabilities/`. They are selected/composed by the SPS process and may be seeded or generated. Capability Registry and Capability Lineage are supporting subsystems, not additional architectural layers.

`layers/architecture.py` is the canonical machine-readable architecture manifest used by the dashboard/API.
