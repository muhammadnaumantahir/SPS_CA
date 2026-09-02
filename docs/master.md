# SPS-CA — Self-Programming Code Assistant

## Introduction

SPS-CA is a research coding assistant built to demonstrate how a conventional AI coding assistant can be extended into a **Self-Programming Software (SPS)** system.

A conventional coding assistant mainly follows:

```text
User request → AI model → code/tools → tests → answer
```

SPS-CA adds an architectural system around the AI model so that the software can **remember experience, evaluate its own strategies, adapt its behavior, develop reusable capabilities, and evolve those capabilities under verification and governance**.

The goal is not to claim that AI code generation is new. The goal is to test whether an SPS architecture can make a coding assistant more systematic, traceable, reusable and capable of improvement over repeated tasks.

## What SPS-CA Is

SPS-CA has three distinct concepts:

```text
SPS-CA
├── Ten architectural layers
├── Brain (replaceable AI intelligence)
└── Capability system (executable SPS skills)
```

### The Brain

The Brain is the intelligence service used by SPS-CA. Ollama is the initial local provider, but the architecture is provider-neutral.

The Brain supports:

- prompt understanding
- reasoning
- planning
- code understanding
- code generation
- debugging
- strategy analysis
- capability selection
- failure analysis
- evolution reasoning

The Brain is **not a layer, not a capability, and not CAP-001**.

### Capabilities

Capabilities are executable SPS skills. They are independently implemented and discoverable through the capability registry.

Examples in the initial system include bug detection, syntax repair, test generation, optimization, error handling, refactoring, type annotation, documentation and natural-language code modification.

A capability may use the Brain, but the capability and the Brain remain separate architectural objects.

## My SPS Framework

The SPS framework is expressed through ten architectural layers. The names and responsibilities below are the canonical model used by the project.

| # | Layer | Core purpose | Optional sub-components |
|---|---|---|---|
| 1 | **Software DNA layer** | Absolute source of truth defining constraints and meta-rules that evolution must obey | Goals, Policies, Constraints, Learning Rules, Repair Rules, Safety Rules, Ethical Rules, Evolution Rules, Meta-Rules |
| 2 | **Governance layer** | Executive gatekeeper that authorizes proposed changes against Software DNA before deployment | Authorization, Evolution Approval, Compliance Checking, Risk Management |
| 3 | **Cognitive core** | Synthesizes goals and system state into tactical decisions, reasoning and plans | Goal Manager, Reasoning Engine, Planning Engine, Decision Engine, Explainability Engine |
| 4 | **Knowledge core** | Manages structured, evolving domain knowledge | Knowledge Base, Knowledge Acquisition Engine, Knowledge Validation, Knowledge Evolution |
| 5 | **Experience core** | Collects and stores feedback and runtime signals as historical memory | Memory, Feedback, Monitoring, Learning Engine |
| 6 | **Meta-learning core** | Evaluates and improves the system's own learning process | Learning Evaluation, Strategy Optimization, Learning Improvement |
| 7 | **Adaptation core** | Shifts behavior by context without modifying source code | Context Awareness, Personalization, Capability Activation, Strategy Selection |
| 8 | **Evolution core** | Engine of genuine structural self-growth | Self-Modification, Self-Regeneration, Capability Preservation, Capability Differentiation, Capability Creation |
| 9 | **Verification & Validation** | Screens new or mutated code in a sandbox before deployment | Testing, Simulation, Safety Validation, Performance Validation |
| 10 | **Execution layer** | Translates validated decisions into real, observable action | Action Executor, Services, APIs, User Interaction |

Sub-components are **optional building blocks**. An implementation may introduce them gradually, replace them or omit them while the parent layer keeps its responsibility.

## How SPS-CA Differs from Other Coding Assistants

SPS-CA is not intended to compete on raw code generation alone. The research distinction is architectural and behavioral.

| Dimension | Conventional AI coding assistant | SPS-CA |
|---|---|---|
| Prompt understanding | Model-driven | Brain inside Cognitive core + SPS context |
| Code generation | Core capability | Brain-assisted capability execution |
| Persistent experience | Usually conversation/project context | Experience core with structured task outcomes |
| Strategy improvement | Mostly implicit | Meta-learning core evaluates strategy performance |
| Context adaptation | Prompt/context rules | Adaptation core selects or composes strategies |
| Reusable skills | Scripts/plugins/instructions | Capability system with registry and lineage |
| Self-growth | Usually user-directed | Evolution core can develop new SPS capabilities |
| Governance | Tool permissions/constraints | Software DNA + Governance layer |
| Verification | Tests/tool execution | Dedicated Verification & Validation boundary |
| Explainability | Conversation output | Decision, capability, layer and trace evidence |
| Feedback loop | User conversation | Experience → Meta-learning → Adaptation → Evolution |

SPS-CA therefore asks a stronger question:

> Can a coding assistant improve its future task handling by learning from experience and developing reusable capabilities, while keeping self-change governed and verifiable?

## Requirements

### Runtime

- Python 3.11+
- Git
- Ollama or another supported AI model provider
- Modern multi-core CPU
- 16 GB RAM recommended for the initial local setup

### Initial Brain

The default local Brain uses Ollama. The current recommended model for the prototype is `qwen2.5-coder:7b`.

### Supported target languages

The prototype is designed for Python, Java, JavaScript, TypeScript, Go and C# and can be extended through the code-analysis subsystem.

### Research requirements

The system must be testable under controlled scenarios so that a basic coding assistant, a tool-augmented assistant and SPS-CA can be compared using the same tasks and projects.

## Core Features

### Conversational coding

The top page behaves as a coding-assistant chat. A user can provide source code and a request, receive a result, and then continue with feedback such as:

```text
User: Add input validation.
SPS-CA: [result]
User: Also reject negative values.
SPS-CA: [updated result based on current code + prior conversation]
```

Recent conversation and the current working source are carried into the next turn.

### Brain separation

The Brain is an interchangeable AI service. The provider implementation is isolated behind `models/` and the Brain boundary, so changing the model does not redefine SPS capabilities.

### Capability selection and composition

The Brain reasons over the active capability catalog and chooses an ordered set of executable SPS skills. It does not invent arbitrary capability IDs at runtime.

### Experience accumulation

Each completed or failed task can become an experience record containing the user request, language, capability used, outcome, timing and failure category.

### Meta-learning and adaptation

Experience becomes evidence for strategy evaluation. The system can later use that evidence to select better strategies or compose existing capabilities for the same kind of problem.

### Capability evolution

When repeated limitations justify structural improvement, the Evolution core can produce a capability candidate. Candidates must pass Verification & Validation and Governance before becoming reusable SPS capabilities.

### Governance and verification

Self-change is never allowed to bypass the governance or verification boundary. Validation evidence and governance decisions are part of the trace.

### Multi-language evaluation

The same SPS architecture can be exercised against controlled Python, Java and TypeScript projects.

## Architecture and Request Flow

A normal user request is conceptually processed as:

```text
User prompt + code
      ↓
Software DNA layer
      ↓
Governance layer — policy/context gate
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
Evolution core — only when self-growth is relevant
      ↓
Capability selection / composition
      ↓
Verification & Validation
      ↓
Governance — final authorization
      ↓
Execution layer
      ↓
Experience / trace feedback
```

The exact runtime may revisit a layer when a failure or feedback signal requires another reasoning cycle. The ten layers describe **responsibilities**, not a rigid single-pass program counter.

## User Project vs SPS Self-Programming

This distinction is central to the project.

### Coding-assistant behavior

SPS-CA changes a user's project:

```text
User project
   ↓
request
   ↓
capability execution
   ↓
validated change
```

### Self-programming behavior

SPS-CA changes its own reusable capability system:

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
Capability candidate
   ↓
Verification & Validation
   ↓
Governance
   ↓
Capability Registry + lineage
   ↓
Reusable SPS capability
```

Changing user code alone does not prove self-programming.

## Initial Capability Portfolio

Stage 0 starts with seeded capabilities. The current registry includes:

1. **CAP-001 — Simple Bug Detection**
2. **CAP-002 — Syntax Error Fix**
3. **CAP-003 — Unit Test Generation**
4. **CAP-004 — Loop Optimization**
5. **CAP-005 — Error Handling Pattern**
6. **CAP-006 — Unused Variable Removal**
7. **CAP-007 — Type Annotation Addition**
8. **CAP-008 — Documentation Generation**
9. **CAP-011 — Natural Language Code Modification**

Generated capabilities are kept conceptually separate from the seed set and are activated only after the evolution path produces sufficient evidence.

## Evaluation Strategy

SPS-CA should be evaluated against the same coding scenarios in progressively stronger conditions:

```text
Baseline A
Naive AI coding assistant

Baseline B
Tool-augmented coding assistant

SPS-CA Stage 0
Ten-layer SPS architecture + seeded capabilities

SPS-CA improved state
Experience + strategy learning + adaptation + generated/reused capabilities
```

The goal is to determine whether the added SPS mechanisms improve repeated-task behavior rather than merely demonstrating that a model can generate code.

Key evidence should include:

- correctness
- success/failure rate
- time
- retries
- validation failures
- governance decisions
- capability selection
- capability reuse
- capability composition
- generated capability count
- capability lineage
- recovery/rollback behavior
- performance over repeated scenarios

The full scenario definitions and experimental procedure live separately in `docs/scenarios.md`.

## Project Structure

```text
SPS_CA/
├── brain/                 # separate SPS-CA intelligence service
├── layers/                # ten-layer architectural implementation
├── capabilities/          # seeded/generated executable SPS skills
├── core/                  # shared orchestration and state services
├── models/                # model/provider abstraction
├── coding/                # repository and code intelligence
├── validation/            # verification support
├── governance/            # governance support
├── execution/             # controlled execution support
├── projects/              # controlled evaluation projects
├── baselines/             # comparison assistants
├── evaluation/            # executable evaluation code
├── analytics/             # evidence and analytics support
├── memory/                # runtime memory support
├── ui/                    # conversational web UI + CLI
└── docs/                  # project documentation
```

Runtime conversations, experiences, traces, model caches and user projects should remain outside source control whenever practical.

## Documentation Map

- `docs/master.md` — what SPS-CA is and how the whole system fits together
- `docs/ARCHITECTURE.md` — canonical ten-layer architecture and boundaries
- `docs/scenarios.md` — detailed experimental scenario specification
- `docs/PIPELINE.md` — request and feedback lifecycle
- `SETUP.md` — local/Colab setup
- `REQUIREMENTS.md` — environment and software requirements

## Research Position

SPS-CA is a research prototype. Its purpose is to make the SPS architecture testable and observable: a coding assistant with a separate Brain, explicit layers, reusable capabilities, persistent experience and a controlled route to self-improvement.
