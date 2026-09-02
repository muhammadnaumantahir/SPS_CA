# SPS-CA: Self-Programming Code Assistant

**Student:** Muhammad Nauman Tahir (MS240400054)
**Institution:** Virtual University of Pakistan
**Supervisor:** Dr. Muhammad Salman Bashir
**Repository:** [github.com/muhammadnaumantahir/SPS_CA](https://github.com/muhammadnaumantahir/SPS_CA)
**Budget:** $0 — fully local, open-source stack

---

## 1. What SPS-CA Is

SPS-CA (Self-Programming Code Assistant) is a research prototype demonstrating a **governed, traceable, reversible self-programming framework** expressed as a coding assistant.

Unlike standard AI coding assistants that simply generate or modify code on demand, SPS-CA is designed around a **10-layer self-programming architecture** with a separate, replaceable **AI Brain**. The system can:

- Receive user requests in natural language with code context
- Analyze and modify target code in any language (Python, Java, TypeScript, Go, C#)
- Govern every change through DNA constraints and evidence-based decision gates
- Trace every decision back to its trigger, rationale, and outcome
- Reverse failed changes automatically through sandbox testing and rollback
- Learn from accumulated experience to improve future strategy selection
- **Create new executable capabilities** when repeated failure patterns emerge
- Compose and reuse capabilities across different projects and languages

The core research claim:

> **A reference framework (SPS) exists that defines characteristics, design principles, and layered architecture necessary for software to safely, tracefully, and reversibly modify its own logic.**

SPS-CA proves this by implementing all 10 layers in working Python code, demonstrating governed self-modification, and measuring improvement through structured evaluation.

---

## 2. The SPS Framework

SPS-CA implements a **10-layer Self-Programming Software framework** where each layer has a clearly separated responsibility. The layers form a pipeline through which every request flows:

```
User Prompt + Source Code
        │
        ▼
L1  Software DNA layer          ← constraints, policies, safety rules
        │
L2  Governance layer            ← decision gates, risk assessment
        │
L3  Cognitive core              ← reasoning, planning  ← Brain (Ollama / AI model)
        │
L4  Knowledge core              ← structured domain knowledge
        │
L5  Experience core             ← historical memory, feedback
        │
L6  Meta-learning core          ← strategy improvement, learning
        │
L7  Adaptation core             ← context-aware behavior adjustment
        │
L8  Evolution core              ← capability generation (SELF-PROGRAMMING)
        │
Capability selection / composition
        │
L9  Verification & Validation   ← sandboxed testing, regression detection
        │
L2  Governance (final)          ← approve / reject with rationale
        │
L10 Execution layer             ← apply changes, monitor, rollback
        │
Experience + learning feedback loop
```

### Layer Responsibilities

| Layer | Name | Purpose |
|-------|------|---------|
| L1 | **Software DNA** | Immutable constraints, policies, safety rules, meta-rules that all evolution must obey |
| L2 | **Governance** | Executive gatekeeper — authorizes proposed changes against Software DNA before deployment |
| L3 | **Cognitive Core** | Synthesizes goals and system state into tactical decisions, reasoning, and plans; primary interface with the Brain |
| L4 | **Knowledge Core** | Manages structured, evolving domain knowledge |
| L5 | **Experience Core** | Collects and stores feedback and runtime signals as historical memory |
| L6 | **Meta-Learning Core** | Evaluates and improves the system's own learning process |
| L7 | **Adaptation Core** | Shifts behavior instantly by context, without modifying source code |
| L8 | **Evolution Core** | The engine of genuine structural self-growth — creates new capabilities |
| L9 | **Verification & Validation** | Screens new or mutated code in a sandbox before it reaches production |
| L10 | **Execution Layer** | Translates validated decisions into real, observable action |

Each layer is implemented as its own Python package under `layers/` with its own tests and models.

### The Brain

The Brain is a **separate AI intelligence service** — not a layer and not a capability:

```
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
```

The Brain provides reasoning, prompt analysis, planning, code generation, debugging, and strategy analysis. It is used primarily by the Cognitive Core (L3) but can be called by other layers.

The Brain is **provider-neutral**. Ollama with `qwen2.5-coder:7b` is the initial implementation, but the Brain can be swapped to Qwen, Llama, DeepSeek, or a cloud API through `models/` without changing the SPS architecture or capabilities.

### Capabilities

Capabilities are **executable SPS skills** — independent of the Brain and registered/versioned separately:

```
SPS-CA
    │
    ├── 10 Layers (architecture)
    ├── Brain (intelligence service)
    │
    └── Capability System
            │
            ├── Seed capabilities (CAP-001 through CAP-009)
            └── Generated capabilities (CAP-010+)
```

The Capability Registry and Capability Lineage are supporting subsystems, not additional architectural layers.

---

## 3. How SPS-CA Differs from Other Coding Assistants

SPS-CA is not competing on raw coding ability. Copilot, Cursor, Claude Code, Codex, Devin, Windsurf, Aider, and Codebuff all run frontier cloud models and are production-hardened. SPS-CA runs a small local 7B model.

The contribution of SPS-CA is the **governed self-programming layer underneath the agent loop**.

### Comparison Table

| Dimension | **SPS-CA** | GitHub Copilot | Cursor | Claude Code | Devin | Aider |
|---|---|---|---|---|---|---|
| **Persistent cross-session experience log** | ✅ Layer 5 — structured, queryable | ❌ | ⚠️ Project rules | ⚠️ Session memory | ⚠️ Task history | ❌ |
| **Meta-learning (strategy improves over time)** | ✅ Layer 6, explicitly measured | ❌ | ❌ | ❌ | ⚠️ Implicit | ❌ |
| **Self-generated, versioned, reusable capabilities** | ✅ Layer 8/9 — executable module + tests + metadata | ❌ | ❌ | ⚠️ If instructed | ⚠️ Internal playbooks | ❌ |
| **Formal governance (DNA rules, approve/reject)** | ✅ Layer 1 + L2 — hard/soft constraints, logged decisions | ❌ | ❌ | ⚠️ Permission prompts | ⚠️ Guardrails | ❌ |
| **Auditable decision trail** | ✅ Full JSON audit trail | ❌ | ❌ | ⚠️ Conversation log | ⚠️ Task log | ⚠️ Git commits |
| **Sandbox validation + rollback** | ✅ L9 + L10 — sandboxed test, auto-rollback | ❌ | ❌ | ⚠️ Runs tests if asked | ⚠️ Isolated VM | ⚠️ Git-based |
| **Capability lineage / provenance** | ✅ Parent capability, trigger tasks, model, validation evidence | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Cross-project, cross-language reuse** | ✅ Explicit evaluation metric | N/A | N/A | N/A | N/A | N/A |
| **Cost** | **$0** (local LLM, open-source) | Paid | Paid | Pay-per-use | Paid | Pay-per-use |
| **Reproducibility for research** | ✅ Fixed seeds, same-LLM baselines, full Git history | ❌ | ❌ | ⚠️ Partial | ❌ | ✅ Open tool |

### Key Distinction: User-Project Change vs. SPS Self-Change

This distinction is central to the thesis:

**Type A — User-Project Changes (Visible Output):**
- SPS-CA fixes bugs, adds features, generates tests in user code
- This is coding-assistant functionality
- All three baselines can do this

**Type B — SPS Self-Changes (Research Subject):**
- SPS-CA creates new capabilities in `capabilities/generated/`
- New Python module with `capability.py`, `tests.py`, `metadata.json`
- Registered, versioned, governance-approved, validated in sandbox
- **This is self-programming behavior**
- Only SPS-CA can do this — this is what the thesis measures

---

## 4. Requirements

### System Requirements

- **Python:** 3.11+
- **RAM:** 16 GB recommended
- **CPU:** Modern multi-core (Intel i7 7th Gen or equivalent)
- **Disk:** 30 GB free for initial setup
- **OS:** Windows, Linux, or macOS

### AI Brain

- **Provider:** Ollama (local, free)
- **Model:** `qwen2.5-coder:7b`
- **GPU:** Optional — runs on CPU/system memory
- **Cost:** $0

### Key Dependencies

- `tree-sitter` — language-agnostic code parsing
- `pydantic` — data validation and models
- `pytest` — testing framework
- `requests` / `httpx` — HTTP for Brain communication
- `sqlalchemy` — persistence
- `rich` — terminal UX

Full dependency list: `requirements.txt`

### Research Requirements

The prototype supports reproducible comparison between:

1. **Baseline A** — Naive LLM coding assistant (same model, no tools)
2. **Baseline B** — Tool-augmented coding agent (same model + analysis/testing tools, no SPS layers)
3. **SPS-CA** — Full 10-layer self-programming framework

All three use the **same local LLM** to isolate framework effects from model quality differences.

---

## 5. Features

### Core SPS-CA Features

1. **10-Layer Governed Architecture** — Every request flows through all layers with clear responsibilities
2. **Separate AI Brain** — Provider-neutral intelligence service, not a layer or capability
3. **Experience Accumulation** — Persistent cross-session experience log with structured failure/success tracking
4. **Meta-Learning** — Strategy selection improves over time; measured improvement target >15%
5. **Capability Adaptation** — Reuse existing capabilities with parameter adjustment for new contexts
6. **Structural Self-Modification** — Generate new, versioned, tested Python capability modules from repeated failure patterns
7. **Capability Composition** — Combine multiple capabilities to solve complex multi-step tasks
8. **Cross-Project Reuse** — Capabilities work across Python, Java, TypeScript, Go, C# projects
9. **Governance Enforcement** — DNA constraints checked on every change; violations rejected with reasoning
10. **Sandbox Validation** — All changes validated in isolated environment before deployment
11. **Automatic Rollback** — Failed changes are rolled back automatically; target >95% rollback success
12. **Complete Traceability** — Every decision logged with rationale, timestamp, outcome; audit trail is supervisor-reviewable
13. **Language-Agnostic Analysis** — Python core, any-language user projects via tree-sitter
14. **Zero Cost** — $0 development budget using local open-source stack

### What SPS-CA Does NOT Claim

- "AI writing code is new" — code generation is well-established
- "This is production-ready software" — it is a research prototype
- "The system learns in real-world software contexts" — evaluation is limited to controlled projects
- "This is the only way to build SPS" — it is one reference implementation

---

## 6. Architecture

### Repository Structure

```
SPS_CA/
├── brain/                    # Separate AI Brain service
├── layers/                   # Canonical 10-layer architecture
│   ├── layer_01_software_dna/
│   ├── layer_02_governance/
│   ├── layer_03_cognitive_core/
│   ├── layer_04_knowledge_core/
│   ├── layer_05_experience_core/
│   ├── layer_06_meta_learning/
│   ├── layer_07_adaptation/
│   ├── layer_08_evolution/
│   ├── layer_09_verification/
│   ├── layer_10_execution/
│   └── architecture.py       # Canonical architecture manifest
├── core/                     # Cross-layer orchestration
├── models/                   # Provider/model abstraction
├── capabilities/             # Seed + generated skills
│   ├── seeds/                # Built-in capabilities
│   ├── generated/            # Evolution-generated capabilities
│   ├── lineage/              # Capability provenance records
│   └── registry.json         # Central capability index
├── coding/                   # Repository/code intelligence
├── governance/               # DNA rules + decision audit trail
├── experience/               # Runtime experience logs
├── sandbox/                  # Isolated execution support
├── execution/                # Controlled execution infrastructure
├── evaluation/               # Scenarios, runner, metrics
├── baselines/                # Baseline A and B comparison agents
├── projects/                 # Controlled benchmark projects
├── testing/                  # Cross-layer integration tests
├── ui/                       # CLI and web dashboard
├── docs/                     # Documentation
├── scripts/                  # Setup and demo scripts
└── analytics/                # Evidence and growth analytics
```

### Zero-Cost Stack

| Component | Tool | Cost |
|-----------|------|------|
| LLM | Ollama + `qwen2.5-coder:7b` | $0 |
| Code Parsing | tree-sitter | $0 |
| Testing | pytest | $0 |
| Database | SQLite | $0 |
| Version Control | Git + GitHub Free | $0 |
| Containerization | Docker Desktop Free | $0 |
| Compute | Local machine | $0 |

---

## 7. Initial Capabilities (Stage 0)

SPS-CA starts with a fixed set of seed capabilities. These are the skills available to the system before any evolution occurs.

### Seed Capability Portfolio

| ID | Name | Type | Domain | Target Languages |
|----|------|------|--------|-----------------|
| CAP-001 | Simple Bug Detection | Analysis | Code Quality | Python, Java, JS/TS, Go, C# |
| CAP-002 | Syntax Error Fix | Fix | Correctness | Python, Java, JS/TS, Go, C# |
| CAP-003 | Unit Test Generation | Generation | Quality Assurance | Python, Java, JS/TS, Go, C# |
| CAP-004 | Loop Optimization | Optimization | Performance | Python, Java, JS/TS, Go, C# |
| CAP-005 | Error Handling Pattern | Analysis | Robustness | Python, Java, JS/TS, Go, C# |
| CAP-006 | Unused Variable Removal | Refactoring | Maintainability | Python, Java, JS/TS, Go, C# |
| CAP-007 | Type Annotation Addition | Transformation | Readability | Python, Java, JS/TS, Go, C# |
| CAP-008 | Documentation Generation | Generation | Knowledge | Python, Java, JS/TS, Go, C# |
| CAP-009 | Natural Language Code Modification | Modification | Feature/Repair | Python, Java, JS/TS, Go, C# |

### Capability Structure

Every capability (seed or generated) follows the same structure:

```
capabilities/seeds/cap_NNN_name/
├── capability.py      # Entry point: run(context) → CapabilityResult
├── tests.py           # Comprehensive test suite
├── metadata.json      # Version, entry point, languages, tags
└── README.md          # Documentation
```

The `CapabilityContext` and `CapabilityResult` interfaces in `capabilities/base.py` ensure every capability can be selected, executed, and validated uniformly.

### Capability Lifecycle: From Stage 0 to Self-Programming

```
Stage 0: Fixed seed capabilities (CAP-001 through CAP-009)
    │
    ├── User requests processed
    ├── Experience accumulated
    ├── Failures recorded
    │
    ▼
Repeated failure pattern detected (3+ occurrences)
    │
    ▼
Meta-learning recommends evolution
    │
    ▼
Governance approves evolution
    │
    ▼
Evolution generates new capability (e.g., CAP-010)
    │
    ▼
Capability validated in sandbox
    │
    ▼
Capability registered in registry
    │
    ▼
Stage 1: Expanded capability set, improved strategy selection
    │
    ▼
... cycle continues ...
```

---

## 8. Evaluation

The research uses a **25-scenario evaluation harness** (20 mandatory + 5 extended) across three baselines and three controlled projects.

| Level | Scenarios | What is Tested |
|-------|-----------|---------------|
| **Level 1: Basic Coding** | S1–S4 | Standard coding tasks (syntax fix, feature add, test gen, refactor) |
| **Level 2: SPS Behavior** | S5–S15 | Experience, meta-learning, adaptation, capability generation, cross-project reuse |
| **Level 3: Governance & Safety** | S16–S25 | DNA enforcement, risk assessment, sandbox validation, rollback, lineage |

**Target projects** implement the same business logic in three languages:
- Project A: Python/FastAPI
- Project B: Java/Spring Boot
- Project C: TypeScript/Express.js

**Total executions:** ~85–100 across all baselines, projects, and scenarios.

**Detailed scenario specifications:** See `docs/SCENARIOS.md`

### Success Metrics

| Metric | Target | Comparison |
|--------|--------|-----------|
| Task Success Rate | >65% | Baseline A: ~40%, Baseline B: ~55% |
| Meta-Learning Improvement | >15% | SPS-CA only |
| Cross-Language Reuse | >60% | SPS-CA only |
| Regression Rate | <2% | Baseline A: ~8%, Baseline B: ~4% |
| Test Coverage (Generated Code) | >80% | SPS-CA only |
| Rollback Success | >95% | SPS-CA only |
| Governance Accuracy | 100% | SPS-CA only |

---

## Companion Documents

| Document | Purpose |
|----------|---------|
| `README.md` | Quick overview and getting started |
| `docs/ARCHITECTURE.md` | Canonical layer/module reference |
| `docs/PIPELINE.md` | Request lifecycle through the 10 layers |
| `docs/SCENARIOS.md` | Detailed experimental scenario specifications |
| `SETUP.md` | Installation and verification procedure |
| `REQUIREMENTS.md` | Hardware, software, model, and research requirements |

---

**Prepared by:** Muhammad Nauman Tahir

*For questions, refer to `docs/ARCHITECTURE.md`, `README.md`, or contact the thesis supervisor.*
