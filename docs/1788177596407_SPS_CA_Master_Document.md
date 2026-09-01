# SPS-CA: Self-Programming Software Prototype
## Complete Master Development & Evaluation Plan
### Zero-Cost, Functional-Equivalence Edition

**Version:** 4.1 (Phase 0 Implemented — Structure Realigned to Actual Codebase, Competitive Analysis Added)  
**Date:** August 2026  
**Student:** Muhammad Nauman Tahir (MS240400054)  
**Institution:** Virtual University of Pakistan  
**Supervisor:** Dr. Muhammad Salman Bashir  
**Timeline:** 32-36 weeks (development + evaluation) + 8-10 weeks thesis writing  
**Development Phases:** 0-10 (11 total phases, consolidated)  
**Budget:** $0 — see Section 9 (Zero-Cost LLM & Compute Architecture) and Appendix A  
**Repository:** [github.com/muhammadnaumantahir/SPS_CA](https://github.com/muhammadnaumantahir/SPS_CA) — **v0.3.0, Phase 0 (Architecture Foundation) complete**

> **Change log (v4.0 → v4.1):**
> - **Phase 0 marked complete** and re-documented against the actual repository (45 commits, tag `v0.3.0`) instead of the originally planned layout.
> - **Directory structure realigned**: the flat `core/layer_N_*.py` design in v4.0 was superseded during implementation by a modular `layers/layer_0N_name/` package-per-layer design, with `core/` reserved for orchestration, state, and event contracts only. Section 6, Section 7 intro, Phase 0, and Appendix C are updated to match.
> - **New subsystems introduced during Phase 0** that were not in the original v4.0 blueprint: `models/` (provider-neutral LLM abstraction), `coding/` (repository intelligence & code manipulation), `execution/`, `governance/`, and `validation/` as standalone infrastructure packages (separate from their same-named layers), `memory/` and `data/` (runtime data, kept out of Git), `analytics/` (capability growth/genealogy datasets), and `testing/` (cross-layer/integration tests, replacing the flat `tests/` folder).
> - **LLM substitution**: local model changed from Llama 2 70B / Mixtral 8x7B (v4.0 placeholder) to **`qwen2.5-coder:7b`** via Ollama, matching the actual development machine (16GB RAM, Intel HD 620, i7 7th Gen). Section 9 and Appendix A updated accordingly. `qwen2.5-coder:7b` in `REQUIREMENTS.md`.
> - **New Section 4 — Competitive Analysis & Differentiation**: added a comparison table positioning SPS-CA against existing AI coding tools (GitHub Copilot, Cursor, Claude Code, OpenAI Codex, Devin, Windsurf, Aider, Codebuff) on the dimensions that matter to the thesis claim (persistent experience, governed self-evolution, capability lineage, rollback, reproducibility, cost).
> - **New project-level docs referenced**: `REQUIREMENTS.md`, `SETUP.md`, `SETUP_AND_PUSH.sh`, and `docs/architecture/SPS_CA_ARCHITECTURE_V2.md` now exist in the repo and are cited as the authoritative low-level companions to this master document.

> **Change log (v3.0 → v4.0):** 
> - **Core language strategy**: Python-first SPS orchestration engine, but can analyze and modify user code in ANY language (Java, JavaScript, TypeScript, Python, Go, C#, etc.)
> - **Experimental scenarios**: Expanded from 13 to 25 (20 mandatory + 5 extended), organized in 3 levels (basic coding, SPS behavior, governance & evolution safety)
> - **User interaction model**: Simplified prompt-based UI (like ChatGPT); users share code/prompts, SPS modifies user code or generates new capabilities
> - **Self-programming clarity**: Distinct between user-project changes (visible output) and SPS self-changes (research subject—new capabilities committed to GitHub)
> - **Capability definition**: Formalized as versioned executable Python module with fixed entry point, tests, and metadata (not just prompt changes)
> - **Baseline comparison**: Three baselines (Naive LLM, Coding Agent + Tool Registry, SPS-CA) with same local LLM to isolate framework effects
> - **Documentation focus**: Phase-by-phase implementation instructions are now the central purpose, not secondary to architecture

---

## TABLE OF CONTENTS

### PART I: FOUNDATION & CONTEXT
1. Executive Summary
2. Vision & Objectives
3. Framework-to-Implementation Mapping
4. Competitive Analysis & Differentiation (incl. SPS-CA vs. Copilot/Cursor/Claude Code/Codex/Devin/Windsurf/Aider/Codebuff)
5. Research Boundaries & Constraints

### PART II: ARCHITECTURE & DESIGN
6. Complete System Architecture
7. Ten-Layer Implementation Blueprint
8. Language-Agnostic Analysis Strategy (Python orchestration, target-language-neutral code analysis)
9. Zero-Cost LLM & Compute Architecture

### PART III: TARGET ENVIRONMENTS & CHANGE TAXONOMY
10. Project Portfolio — Functional Equivalence Group (3 Projects)
11. Change Type Taxonomy (7 Types)
12. Initial Capability Portfolio (8-10 Built-in Capabilities)

### PART IV: SELF-PROGRAMMING MECHANISM
13. Self-Programming Mechanism Overview (Software DNA, Governance, Evolution)

### PART V: DEVELOPMENT ROADMAP
14. **Phases 0-10: Complete Specifications (INSTRUCTION MANUAL FORMAT — PRIMARY REFERENCE)**
15. Phase Overview Table & Dependencies

### PART VI: USER INTERACTION & WORKFLOW
16. User Interface & Interaction Model (Prompt-Based)
17. User Project vs SPS Self-Change Architecture

### PART VII: EXPERIMENTAL DESIGN
18. Baseline Agents (A, B, SPS-CA)
19. **25 Experimental Scenarios (20 Mandatory + 5 Extended)**
20. Project Execution Matrix & Scenario Distribution

### PART VIII: EVALUATION & EVIDENCE
21. Metrics & Measurement Framework
22. Evaluation Protocol
23. Expected Thesis Artifacts
24. Threats to Validity
25. Risk Mitigation Strategies

### PART IX: APPENDICES
A. Zero-Cost Technology Stack
B. Installation Instructions
C. File Manifest
D. Success Metrics Summary
E. Evaluation Forms & Checklists

---

## PART I: FOUNDATION & CONTEXT

---

## 1. EXECUTIVE SUMMARY

### 1.1 What This Document Is

This is the **definitive, executable development blueprint** for SPS-CA (Self-Programming Code Assistant), a research prototype demonstrating a reference framework for Self-Programming Software (SPS).

**Critical distinction:** This document is NOT a description of what you'll build. It is a **step-by-step instruction manual** (see Part V, Phases 0-10) that can be given to an AI coding agent, phase by phase, to construct the entire system from scratch.

**New in v4.0:** Phase specifications are now the primary document focus. Architecture documentation is secondary.

### 1.2 What SPS-CA Proves

Your thesis claims:

> **"A reference framework (SPS) exists that defines characteristics, design principles, and layered architecture necessary for software to safely, tracefully, and reversibly modify its own logic."**

SPS-CA proves this claim by:

1. **Implementing all 10 layers** in working Python code (orchestration engine)
2. **Analyzing and modifying user code** in any target language (Java, JavaScript, Python, Go, C#, TypeScript, etc.)
3. **Demonstrating governance enforcement** (DNA violations rejected, decisioning is auditable)
4. **Showing evolution traceability** (complete audit trail of every self-modification with decision rationale)
5. **Validating safety mechanisms** (sandbox, regression testing, rollback)
6. **Creating executable capabilities** (not prompt changes — actual versioned Python modules with tests and metadata)
7. **Demonstrating capability composition** (combining multiple generated capabilities)
8. **Showing cross-project reuse** (capabilities work across different user projects and domains)
9. **Measuring meta-learning effectiveness** (system improves strategy selection over time)

### 1.3 What SPS-CA Does NOT Claim

❌ "AI writing code is new"  
❌ "Code generation is novel"  
❌ "Self-modifying systems haven't existed before"  
❌ "This is production-ready software"  
❌ "This is the only way to build SPS"  
❌ "The system learns in real-world software contexts"

### 1.4 Key Facts About This Prototype

| Attribute | Value |
|-----------|-------|
| **SPS Core Language** | Python 3.11+ (orchestration, self-modification, governance) |
| **Target User Languages** | Python, Java, JavaScript/TypeScript, Go, C# (extensible via tree-sitter) |
| **Target Projects** | 3 controlled projects in Functional Equivalence Group (same logic, different languages) |
| **Initial Capabilities** | 8-10 built-in |
| **Generated Capabilities** | Expected: 3-6 during evaluation |
| **Experimental Scenarios** | 25 total (20 mandatory + 5 extended) |
| **  Level 1 (Basic Coding)** | 4 scenarios |
| **  Level 2 (SPS Behavior)** | 11 scenarios |
| **  Level 3 (Governance & Safety)** | 10 scenarios |
| **Total Executions** | ~75-90 (across 3 baselines × 3 projects × scenario mix) |
| **Total Development Time** | ~18-20 weeks (phases 0-10) |
| **Total Evaluation Time** | ~4 weeks (folded into Phase 10 + buffer) |
| **Documentation Pages** | This master doc: 80+ |
| **Expected Code Lines** | ~5,500-7,500 (SPS core + tests) |
| **Git Commits** | ~90-120 (tracked by phase) |
| **Development Budget** | **$0** — local open-weight LLM (Ollama), SQLite, tree-sitter, Docker, GitHub free tier |

### 1.5 How to Read This Document

**For Project Managers/Supervisors (skip to here if time-constrained):**
- Read: Executive Summary, Vision (Section 2), Key Facts (Section 1.4), Project Portfolio (Section 10), Baselines (Section 18), Phase Summary (Section 15)
- Time: 2-3 hours
- Output: Understand scope, timeline, deliverables

**For AI Coding Agents (automation — PRIMARY USE CASE):**
- Read: **Section 14 (Phases 0-10)** in order
- Use: AI Agent Prompt templates provided in each phase specification
- Follow: Phase-by-phase, 1-3 weeks per phase, checkpoint after each phase (Appendix E, Form 1)
- Time: 18-20 weeks
- Output: Complete SPS-CA system, ready for evaluation

**For Researchers (thesis development):**
- Read: Entire document, focusing on Part IV (self-programming mechanism), Part VII (experimental design), Part VIII (evaluation)
- Cross-reference: Phase specs for implementation details
- Time: 4-6 hours initial read, then iterative reference during phases
- Output: Thesis structure, evidence collection strategy, evaluation approach

---

## 2. VISION & OBJECTIVES

### 2.1 Long-Term Vision

Build a **self-programming software ecosystem** that:

- **Receives user requests** in natural language with optional code context
- **Analyzes target code** independent of language, using language-agnostic parsing (tree-sitter)
- **Modifies user code** safely and tracefully in the target project
- **Creates new capabilities** (executable Python modules) when patterns emerge from repeated failures
- **Governs all changes** through DNA constraints and evidence-based decision gates
- **Traces every decision** back to trigger, rationale, and outcome
- **Reverses failed changes** automatically through sandbox testing and regression detection
- **Learns from experience** to improve strategy selection and capability composition
- **Reuses capabilities** across different user projects
- **Remains controllable** through human-in-the-loop escalation when risk is high

### 2.2 Key Architectural Distinction: User Project vs SPS Self-Change

**This is central to your thesis and differentiates SPS-CA from standard coding assistants.**

```
         SPS-CA INTERNAL SYSTEM (Python-based, self-modifying)
    ┌───────────────────────────────────────────────────────────┐
    │ Software DNA                                              │
    │ Governance & Decision Gates                               │
    │ Cognitive Core (Planning, Analysis, Meta-Learning)        │
    │ Knowledge Base & Experience Log                           │
    │ Meta-Learning (Strategy Improvement)                      │
    │ Adaptation & Capability Selection                         │
    │ Evolution Engine (Capability Generation)                  │
    │ Validation & V&V (Sandbox, Testing, Rollback)            │
    │ Execution & Tracing                                       │
    │ Capability Registry (Versioned Python Modules)            │
    └────────────────┬─────────────────────────────────────────┘
                     │
              operates on (analyzes, modifies)
                     ▼
              USER TARGET PROJECT
    ┌───────────────────────────────────────────────────────────┐
    │ Source Code (Python, Java, JavaScript, Go, C#, etc.)     │
    │ Tests (pytest, JUnit, Jest, etc.)                        │
    │ Configuration (config files, env vars)                    │
    │ Dependencies (requirements.txt, package.json, etc.)       │
    └───────────────────────────────────────────────────────────┘
```

**User-Project Changes (Visible Output):**
- SPS-CA fixes bugs in `routes.py`, `models.py`, `services.py`
- Updates tests in `tests/`
- These are the deliverables users see and use
- This is **coding-assistant functionality**

**SPS Self-Changes (Research Subject):**
- SPS-CA modifies its own code in `capabilities/generated/`
- Creates new `CAP-006/capability.py`, `CAP-006/tests.py`, `CAP-006/metadata.json`
- Commits changes to GitHub with reasoning in commit messages
- This is **self-programming behavior**
- This is what you measure in the thesis

**Evaluation focuses on: Can SPS improve its own capability registry based on experience?**

### 2.3 Prototype-Specific Objectives (11 Primary)

**Objective 1: Implement 10-Layer Architecture in Python**
- All 10 layers functional and integrated
- Each layer has defined interfaces and responsibilities
- Layers can be tested independently and in combination

**Objective 2: Demonstrate User-Facing Coding Behavior**
- SPS-CA receives user request + optional code context
- Analyzes target project (any language, via tree-sitter)
- Plans solution independently
- Generates and tests code modifications
- Validates success and returns results

**Objective 3: Demonstrate Adaptation (Type 6 Change)**
- System reuses existing capabilities appropriately
- Selects best strategy based on context
- Adjusts parameters without code modification
- Shows that adaptation ≠ evolution

**Objective 4: Demonstrate Experience Accumulation**
- System maintains detailed history of tasks, failures, successes
- Experience influences future decisions
- Historical analysis shows clear patterns
- Can reset experience to show it matters

**Objective 5: Demonstrate Meta-Learning**
- System identifies failed strategies
- Learns to avoid or modify failed approaches
- Shows measurable improvement in strategy selection >15%
- Can explain why it switched strategies

**Objective 6: Demonstrate Structural Self-Modification**
- System creates new Python capability modules
- Each capability: versioned, with entry point, tests, metadata
- Can generate 3-6 capabilities during evaluation
- Each capability is traceable to originating trigger/failure pattern
- Capabilities are stored in GitHub

**Objective 7: Demonstrate Governance Enforcement**
- DNA constraints are checked on every change
- Violations are rejected with clear reasoning
- High-risk changes require human approval
- All decisions are auditable and logged

**Objective 8: Demonstrate Validation & Rollback**
- Sandbox testing detects regressions
- Failed changes are rolled back automatically
- Rollback success rate >95%
- Zero unintended side effects

**Objective 9: Demonstrate Capability Composition**
- System combines multiple capabilities to solve complex tasks
- Demonstrates that capabilities can be composed hierarchically
- Shows reuse across multiple project contexts

**Objective 10: Demonstrate Language-Agnostic Analysis**
- Same SPS core works with Python, Java, JavaScript target projects
- Code analysis and modification is language-aware but framework-neutral
- Users perceive single "SPS-CA" regardless of their project language

**Objective 11: Demonstrate Complete Traceability**
- Every decision is logged with rationale, time, outcome
- Every capability generation is traceable to trigger
- Complete git history shows evolution of SPS itself
- Audit trail is supervisor-reviewable

---

## 3. FRAMEWORK-TO-IMPLEMENTATION MAPPING

Unchanged from v3.0: every SPS reference-framework construct (Software DNA, Cognitive Core, Experience, Meta-Learning, Adaptation, Validation, Governance, Evolution, Capability Registry, Execution) maps 1:1 to a first-class package under `layers/` in the implemented codebase (see Section 6 and Section 7 for the as-built mapping).

---

## 4. COMPETITIVE ANALYSIS & DIFFERENTIATION

### 4.1 Why Compare SPS-CA to Existing AI Coding Tools

SPS-CA is not claiming to out-code existing AI coding assistants on raw code generation. The thesis claim (Section 1.2) is narrower and different in kind: that a **governed, traceable, reversible self-programming framework** can sit underneath a coding agent and make it measurably better at *repeat* tasks over time — through persistent experience, meta-learning, and capability evolution that is approved, tested, versioned, and auditable. Section 4.2 positions SPS-CA against today's mainstream AI coding tools on exactly the dimensions that distinguish this claim, not on benchmark coding accuracy (which SPS-CA, as a $0 local-LLM research prototype, is not attempting to win).

### 4.2 Comparison Table: SPS-CA vs. Mainstream AI Coding Tools/Models

| Dimension | **SPS-CA** (this thesis) | GitHub Copilot | Cursor | Claude Code | OpenAI Codex (CLI/Cloud) | Devin (Cognition) | Windsurf (Codeium) | Aider | Codebuff |
|---|---|---|---|---|---|---|---|---|---|
| **Primary mode** | Governed self-programming research prototype | In-IDE autocomplete + chat | AI-native IDE (fork of VS Code) | Terminal/CLI agentic coding assistant | Cloud/CLI autonomous coding agent | Autonomous "AI software engineer" | AI-native IDE | Terminal pair-programming agent | CLI/terminal coding agent |
| **Persistent cross-session experience log** | ✅ Layer 3 (Experience) — structured, queryable | ❌ (session-scoped context only) | ⚠️ Project-level context/rules, not structured experience | ⚠️ Session memory + `CLAUDE.md`, not a formal experience layer | ❌ | ⚠️ Task history within its own workspace | ⚠️ Project memory (Cascade), not structured | ❌ (repo map + chat history only) | ❌ |
| **Meta-learning (strategy selection improves over time)** | ✅ Layer 4, explicitly measured (Section 21) | ❌ | ❌ | ❌ | ❌ | ⚠️ Implicit, not exposed/measurable | ❌ | ❌ | ❌ |
| **Self-generated, versioned, reusable capabilities** | ✅ Layer 8/9 — new capability = executable module + tests + metadata, registered for reuse | ❌ | ❌ | ⚠️ Can write reusable scripts/skills if instructed, no formal registry/versioning | ❌ | ⚠️ Can save reusable playbooks internally, not user-auditable | ❌ | ❌ | ❌ |
| **Formal governance layer (DNA rules, approve/reject with rationale)** | ✅ Layer 1 + Layer 7 — hard/soft constraints, logged decisions | ❌ | ❌ | ⚠️ Permission prompts for tool use, not a policy/DNA engine | ⚠️ Sandboxed approval-mode execution | ⚠️ Guardrails, not a documented rule engine | ❌ | ❌ | ❌ |
| **Auditable decision trail (why a change was made/rejected)** | ✅ `governance/decisions/` — full JSON audit trail | ❌ | ❌ | ⚠️ Conversation log only | ⚠️ Execution log only | ⚠️ Task log, limited transparency | ⚠️ Conversation log only | ⚠️ Git commit messages only | ⚠️ Conversation log only |
| **Sandbox validation + rollback before self-modification lands** | ✅ Layer 6 + Execution layer — sandboxed test, rollback on regression | ❌ (no self-modification) | ❌ (no self-modification) | ⚠️ Runs tests if asked; no formal rollback protocol | ⚠️ Sandboxed cloud execution | ⚠️ Runs in isolated VM | ❌ | ⚠️ Relies on Git for rollback | ⚠️ Relies on Git for rollback |
| **Capability lineage/genealogy (provenance of what was learned)** | ✅ Layer 9 — parent capability, triggering task, model, validation evidence, version history | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Cross-project, cross-language capability reuse (measured)** | ✅ Explicit evaluation metric (Section 21, S9 scenario) | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **Target-language scope** | Any (Python core, tree-sitter-parsed targets: Python, Java, JS/TS, Go, C#) | Any (IDE-integrated) | Any | Any | Any | Any | Any | Any | Any |
| **Model dependency** | Provider-neutral (`models/`); local Ollama (`qwen2.5-coder:7b`) today, cloud adapters possible later | OpenAI/proprietary (fixed) | User-selectable (Claude, GPT, etc.) | Claude models (fixed) | OpenAI models (fixed) | Proprietary (fixed) | User-selectable | User-selectable (BYO API key) | User-selectable |
| **Deployment** | Local, fully offline-capable | Cloud SaaS | Cloud SaaS (local IDE shell) | Cloud API (local CLI shell) | Cloud SaaS/CLI | Cloud SaaS | Cloud SaaS (local IDE shell) | Local CLI + cloud API | Local CLI + cloud API |
| **Cost** | **$0** (local LLM, open-source stack) | Paid subscription | Paid subscription | Pay-per-use API | Pay-per-use API / subscription | Paid, usage-metered | Paid subscription (free tier limited) | Pay-per-use API (tool is free) | Pay-per-use API (tool is free) |
| **Reproducibility for research** | ✅ Designed for it — fixed seeds, same-LLM baselines, full Git history, open-source | ❌ Closed model/infra | ❌ Closed infra | ⚠️ Partially (API-based, closed model) | ❌ Closed model/infra | ❌ Closed model/infra | ❌ Closed infra | ✅ Open-source tool (model still closed unless local) | ✅ Open-source tool (model still closed unless local) |
| **Maturity / production readiness** | Research prototype (v0.3.0, architecture foundation) | Production, widely deployed | Production, widely deployed | Production, widely deployed | Production, widely deployed | Production (limited access) | Production, widely deployed | Production, widely deployed | Production, widely deployed |

*Legend: ✅ = explicit, first-class, measured feature; ⚠️ = partial/implicit/undocumented equivalent; ❌ = not offered; N/A = not applicable to that tool's design.*

### 4.3 Key Differentiation Summary

1. **SPS-CA is not competing on raw coding ability.** Copilot, Cursor, Claude Code, Codex, Devin, Windsurf, Aider, and Codebuff are all far more capable at general-purpose code generation today — they run frontier cloud models, have large engineering teams, and are production-hardened. SPS-CA runs a small local 7B model.
2. **SPS-CA's contribution is the governed self-programming layer underneath the agent loop**: a persistent, structured experience log; meta-learning over strategies; capability evolution that must pass governance and sandboxed validation before it is registered and reused; and full lineage/audit trail. None of the compared tools expose this as a first-class, measurable subsystem — several (Claude Code, Devin, Windsurf) have informal analogues (memory files, internal playbooks, guardrails) but none formalize it as versioned, tested, provenance-tracked capabilities with a governance approve/reject decision log.
3. **The fair comparison is architectural, not benchmark-based.** The thesis evaluation (Part VII/VIII) therefore does not attempt to beat Copilot/Cursor/Claude Code/Codex on HumanEval-style benchmarks. It instead compares SPS-CA against two *same-LLM* internal baselines (Baseline A: naive LLM, Baseline B: tool-augmented agent without the SPS layers — Section 18) to isolate the effect of the SPS framework itself, while this table supplies the external market context for why that framework is worth building.
4. **Cost and reproducibility are genuine differentiators for a thesis context**, not just budget constraints: a $0, fully local, open-source stack means every experimental run is reproducible by an examiner or future researcher without API keys, rate limits, or vendor dependency — which the cloud-hosted competitors cannot offer.

---

## 5. RESEARCH BOUNDARIES & CONSTRAINTS

Unchanged from v3.0: SPS-CA is a research prototype, not a production system; evaluation is limited to 3 controlled projects and 25 scenarios; the local 7B model trades inference speed and raw capability for zero cost and full reproducibility (Section 9); results generalize to the tested scope only (see Section 24, Threats to Validity).

---

## 6. COMPLETE SYSTEM ARCHITECTURE

### 6.1 10-Layer Model

```
LAYER 10: EXECUTION LAYER
           ↑
LAYER 9:  CAPABILITY REGISTRY
           ↑
LAYER 8:  EVOLUTION LAYER
           ↑
LAYER 7:  GOVERNANCE LAYER
           ↑
LAYER 6:  VALIDATION & V&V LAYER
           ↑
LAYER 5:  ADAPTATION LAYER
           ↑
LAYER 4:  META-LEARNING LAYER
           ↑
LAYER 3:  EXPERIENCE LAYER
           ↑
LAYER 2:  COGNITIVE CORE (Planning, Analysis, Context Understanding)
           ↑
LAYER 1:  SOFTWARE DNA (Constraints, Policies, Seed Capabilities)
```

**All 10 layers are implemented in Python and managed by the SPS-CA core.**

> **As-implemented note (v4.1):** the v4.0 plan originally specified all 10 layers as flat files inside `core/` (e.g. `core/layer_1_dna.py`). During Phase 0, this was superseded by a **package-per-layer** design: each layer is now its own directory under `layers/` (`layer_01_software_dna/`, `layer_02_cognitive_core/`, … `layer_10_execution/`), each owning its implementation and layer-local tests. `core/` was narrowed to hold **only** cross-layer orchestration, shared state, and event contracts, so layers do not become tightly coupled by calling each other's internals directly. See Section 7 for the per-layer mapping and Section 14, Phase 0 for the full as-built directory tree.

### 6.2 External Interface: Language-Agnostic Code Analysis

The SPS-CA core uses **tree-sitter** (not Python-specific) to parse user code in any language:

```python
# In Layer 2 (Cognitive Core):
# Use tree-sitter to parse target project
parsed_ast = parse_code_language_agnostic(
    source_code="...",
    language="javascript" | "java" | "python" | "go" | "csharp"
)
# Plan modifications at AST level
# Generate target-language-specific code output
```

Result: **Single SPS-CA engine, any user project language.**

---

## 7. TEN-LAYER IMPLEMENTATION BLUEPRINT

### 7.1 Layer 1: Software DNA

**Purpose:** Define immutable constraints and seed capabilities.

**Scope:**
- DNA rules: "Must never modify core governance logic"
- Seed capabilities: CAP-001 through CAP-010 (8 built-in, room for 2 more)
- Versioning scheme: Semantic versioning for capabilities
- Architecture boundaries: User projects are isolated from SPS core

**Implementation:** `capabilities/dna/dna_rules.json`, `capabilities/seeds/CAP-001/` through `CAP-008/`

### 7.2 Layer 2: Cognitive Core

**Purpose:** Plan and analyze target problems.

**Scope:**
- Receive user request + code context
- Analyze target project structure (language-agnostic via tree-sitter)
- Decompose task into subtasks
- Select candidate capabilities
- Plan modification strategy

**Implementation:** `core/cognitive_core.py`

### 7.3 Layer 3: Experience Layer

**Purpose:** Maintain detailed history of all tasks and outcomes.

**Scope:**
- Log every task: request, context, approach, outcome
- Distinguish success, failure, partial success
- Track failure categories for pattern detection
- Maintain per-capability performance metrics

**Implementation:** `core/experience_layer.py`, `experience/` directory (JSON logs)

### 7.4 Layer 4: Meta-Learning Layer

**Purpose:** Learn from experience to improve future decisions.

**Scope:**
- Analyze failure patterns
- Detect capability selection errors
- Recommend strategy changes
- Track improvement over time (measure >15% improvement target)

**Implementation:** `core/meta_learning_layer.py`

### 7.5 Layer 5: Adaptation Layer

**Purpose:** Reuse existing capabilities with adjusted parameters.

**Scope:**
- Match current task to past capabilities
- Adjust parameters (e.g., timeout, aggressiveness, language-specific details)
- Test adaptation on target code
- Log adaptation as Type 6 change (not evolution)

**Implementation:** `core/adaptation_layer.py`

### 7.6 Layer 6: Validation & V&V Layer

**Purpose:** Ensure changes are safe before deployment.

**Scope:**
- Run proposed change in sandbox
- Execute all regression tests
- Compare metrics before/after
- Detect performance degradation or broken functionality
- Prepare rollback if needed

**Implementation:** `core/validation_layer.py`, `sandbox/`

### 7.7 Layer 7: Governance Layer

**Purpose:** Enforce DNA constraints and decision gates.

**Scope:**
- Check DNA violations before any change
- Assess risk level (low/medium/high)
- Route high-risk changes to human approval
- Log decision with rationale
- Escalate if uncertain

**Implementation:** `core/governance_layer.py`, `governance/decisions/` (audit trail)

### 7.8 Layer 8: Evolution Layer

**Purpose:** Create new capabilities from repeated failure patterns.

**Scope:**
- Detect repeated failure categories
- Determine if evolution is needed (vs. adaptation)
- Plan new capability structure
- Generate Python module: `capability.py`, `tests.py`, `metadata.json`
- Write and execute tests
- Register in capability registry
- Commit to GitHub with decision reasoning

**Implementation:** `core/evolution_layer.py`, `capabilities/generated/`

### 7.9 Layer 9: Capability Registry

**Purpose:** Maintain versioned, discoverable, reusable capabilities.

**Scope:**
- Central index of all capabilities (built-in + generated)
- Metadata: version, entry point, dependencies, test coverage, reuse count
- Query capabilities by task type, language, domain
- Track cross-project reuse

**Implementation:** `capabilities/registry.json`, `capabilities/generated/CAP-*`

### 7.10 Layer 10: Execution Layer

**Purpose:** Run validated code modifications safely.

**Scope:**
- Apply changes to user project
- Monitor execution
- Log success/failure
- Trigger rollback if regression detected
- Update experience and metrics

**Implementation:** `core/execution_layer.py`

---

## 8. LANGUAGE-AGNOSTIC ANALYSIS STRATEGY

### 8.1 Core Principle

**SPS-CA is Python-only, but can analyze and modify code in ANY language.**

Tree-sitter provides a language-neutral AST parser:

```python
# Layer 2 (Cognitive Core) parses any language:
from tree_sitter import Language, Parser

SUPPORTED_LANGUAGES = {
    'python': Language('build/my-languages.so', 'python'),
    'java': Language('build/my-languages.so', 'java'),
    'javascript': Language('build/my-languages.so', 'javascript'),
    'go': Language('build/my-languages.so', 'go'),
    'csharp': Language('build/my-languages.so', 'csharp'),
}

def parse_target_code(source: str, language: str):
    parser = Parser()
    parser.set_language(SUPPORTED_LANGUAGES[language])
    tree = parser.parse(source.encode('utf-8'))
    return tree  # Language-agnostic AST
```

### 8.2 Three-Stage Approach

**Stage 1: Analyze (Language-Agnostic)**
- Parse source code using tree-sitter
- Extract function signatures, types, dependencies
- Identify modified scope (which functions, classes)

**Stage 2: Plan (Language-Agnostic)**
- Use cognitive core to reason about required changes
- Select capability or generate new approach
- Plan at AST level (not language-specific syntax)

**Stage 3: Generate (Language-Specific)**
- LLM generates target-language code for the identified scope
- Leverage local LLM (Ollama) with language-specific prompt context
- Include existing code patterns from target project
- Generate + test in sandbox

Result: Single framework, works with Python/Java/JavaScript/Go/C#.

---

## 9. ZERO-COST LLM & COMPUTE ARCHITECTURE

### 9.1 Local LLM via Ollama

**Free, locally-run inference:**
- Model actually used in Phase 0 onward: **`qwen2.5-coder:7b`** (chosen and pinned in `REQUIREMENTS.md`, superseding the v4.0 placeholder of Llama 2 70B / Mixtral 8x7B, which do not fit the target development machine)
- Run via Ollama (macOS, Linux, Docker); install with `ollama pull qwen2.5-coder:7b`
- No API keys, no costs
- All computation on developer's machine
- Model access is provider-neutral (`models/` package, Section 6.1) — SPS layers talk to a model interface, not to Qwen directly, so swapping to a larger local model or a future cloud adapter (OpenAI/Anthropic) requires no changes to the 10 SPS layers

**Hardware driving this choice:** 16 GB RAM, Intel HD 620 integrated graphics, i7 7th Gen — no dedicated GPU. Ollama runs `qwen2.5-coder:7b` on CPU/system memory in this configuration; a dedicated GPU is optional but not required. `Qwen3-Coder` is a separate, larger coding model noted in `REQUIREMENTS.md` as a future option once stronger hardware is available.

**Trade-off:** Slower inference than a cloud frontier model, but deterministic, private, and free.

### 9.2 Free Infrastructure Stack

- **LLM:** Ollama, running `qwen2.5-coder:7b` locally
- **Database:** SQLite (single file, no server)
- **Code Parsing:** tree-sitter (open-source, fast)
- **Containerization:** Docker Desktop (free tier)
- **Version Control:** GitHub (free tier)
- **Compute:** Local machine (no cloud costs)

**See Appendix A for detailed setup, `REQUIREMENTS.md` for the authoritative hardware/software requirements, and `SETUP.md` for the installation/verification procedure.**

---

## 10. PROJECT PORTFOLIO — FUNCTIONAL EQUIVALENCE GROUP (3 Projects)

### 10.1 Philosophy: Same Logic, Different Languages

Rather than building 5 completely different projects, use 3 projects that implement the **same business logic** in different languages. This allows:

- Cross-language capability reuse testing
- Isolation of language vs. framework effects
- Simpler evaluation (fewer uncontrolled variables)
- Clearer capability generalization metrics

### 10.2 Three Projects

**Project A: Python/FastAPI**
- Language: Python
- Framework: FastAPI
- Purpose: Main SPS experiment, main development target
- Domain: Simple REST API (User management + Task management)
- Codebase: ~300-500 LOC (intentionally small, controlled)

**Project B: Java/Spring Boot**
- Language: Java
- Framework: Spring Boot
- Purpose: Test cross-language capability reuse (SPS modifications work on Java code)
- Domain: Same User + Task management logic, Java idioms
- Codebase: ~300-500 LOC (equivalent scope)

**Project C: TypeScript/Express.js**
- Language: TypeScript
- Framework: Express.js
- Purpose: Test capability reuse in different web framework
- Domain: Same User + Task logic, TypeScript patterns
- Codebase: ~300-500 LOC (equivalent scope)

### 10.3 Functional Equivalence Matrix

Each project has the same core features:

| Feature | Project A (Python) | Project B (Java) | Project C (TS) |
|---------|-------------------|------------------|----------------|
| User CRUD | ✅ | ✅ | ✅ |
| Task CRUD | ✅ | ✅ | ✅ |
| Filtering/Search | ✅ | ✅ | ✅ |
| Error Handling | ✅ | ✅ | ✅ |
| Logging | ✅ | ✅ | ✅ |
| Testing (unit + integration) | ✅ | ✅ | ✅ |

**Test Coverage Target:** >80% across all projects.

### 10.4 Evaluation Benefit

When you run scenarios across all 3 projects:
- **Baseline A & B:** Limited by language-specific syntax; high failure rate on non-Python projects
- **SPS-CA:** Reuses Python capabilities, applies language-adapted logic; higher success rate
- **Metric:** "Cross-language capability reuse >60%" (Section 22)

---

## 11. CHANGE TYPE TAXONOMY (7 Types)

Every modification SPS-CA makes falls into one of 7 types. This is critical for experimental analysis.

### 11.1 Seven Change Types

| Type | Name | Definition | Example | Triggers Evolution? |
|------|------|-----------|---------|-------------------|
| 1 | **Syntax Fix** | Correct syntax error in user code | Fix typo in variable name | No |
| 2 | **Logic Fix** | Fix incorrect algorithm or business logic | Fix off-by-one error in loop | No |
| 3 | **Feature Addition** | Add new feature to user project | Add new endpoint to API | No |
| 4 | **Refactoring** | Improve code structure without behavior change | Extract method, rename variable | No |
| 5 | **Test Generation** | Generate tests for uncovered code | Write unit tests for new function | No |
| 6 | **Adaptation** | Reuse existing capability with parameter adjustment | Use CAP-003 with different timeout | No |
| 7 | **Evolution** | Create new capability from repeated failure pattern | Generate CAP-006 (new bugfix capability) | Yes ← triggers self-modification |

**Key insight:** Only Type 7 (Evolution) triggers self-programming. Types 1-6 are user-project changes (visible output).

---

## 12. INITIAL CAPABILITY PORTFOLIO (8-10 Built-in Capabilities)

These are pre-built capabilities that SPS-CA can apply to user projects.

### 12.1 Eight Core Capabilities (CAP-001 through CAP-008)

| ID | Name | Type | Domain | Entry Point | Target Languages |
|----|------|------|--------|-------------|------------------|
| CAP-001 | Simple Bug Detection | Analysis | Code Quality | `analyze_simple_bugs(code)` | Python, Java, JS, Go, C# |
| CAP-002 | Syntax Error Fix | Fix | Correctness | `fix_syntax_errors(code, language)` | Python, Java, JS, Go, C# |
| CAP-003 | Unit Test Generation | Test | Quality Assurance | `generate_unit_tests(function_code, language)` | Python, Java, JS, Go, C# |
| CAP-004 | Loop Optimization | Optimization | Performance | `optimize_loops(code, language)` | Python, Java, JS, Go, C# |
| CAP-005 | Error Handling Pattern | Pattern | Robustness | `add_error_handling(code, language)` | Python, Java, JS, Go, C# |
| CAP-006 | Unused Variable Removal | Refactoring | Maintainability | `remove_unused_variables(code, language)` | Python, Java, JS, Go, C# |
| CAP-007 | Type Annotation Addition | Enhancement | Readability | `add_type_annotations(code, language)` | Python, Java, JS, Go, C# |
| CAP-008 | Documentation Generation | Documentation | Knowledge | `generate_docstrings(code, language)` | Python, Java, JS, Go, C# |

### 12.2 Capability Structure

Each capability (built-in or generated) is a Python module:

```
capabilities/seeds/CAP-001/
├── capability.py          # Entry point function
├── tests.py              # Comprehensive test suite
├── metadata.json         # Versioning, dependencies, reuse count
└── README.md            # Documentation
```

**Example: CAP-001/capability.py**
```python
# capabilities/seeds/CAP-001/capability.py

def analyze_simple_bugs(code: str, language: str = 'python') -> List[Dict]:
    """
    Analyze code for simple, obvious bugs.
    
    Args:
        code: Source code string
        language: 'python' | 'java' | 'javascript' | 'go' | 'csharp'
        
    Returns:
        List of bug dictionaries: {'line': int, 'issue': str, 'fix': str}
    """
    # Implementation here
    pass
```

**Example: CAP-001/metadata.json**
```json
{
  "id": "CAP-001",
  "name": "Simple Bug Detection",
  "version": "1.0.0",
  "created_date": "2024-01-01",
  "last_modified": "2024-01-01",
  "entry_point": "analyze_simple_bugs",
  "supported_languages": ["python", "java", "javascript", "go", "csharp"],
  "dependencies": ["tree-sitter"],
  "test_coverage": 92.5,
  "reuse_count": 0,
  "generated": false,
  "origin": null,
  "failure_pattern": null
}
```

---

## 13. SELF-PROGRAMMING MECHANISM OVERVIEW

### 13.1 What "Self-Programming" Means (Formalized)

**NOT:** "The system learned something" or "We updated a prompt"

**YES:** "The system created a new, versioned executable Python module with:
1. `capability.py` — fixed entry point function
2. `tests.py` — comprehensive test suite (>80% coverage)
3. `metadata.json` — versioning, dependencies, reuse tracking"

This new module is then:
- Registered in the capability registry
- Committed to GitHub with decision rationale in commit message
- Available for reuse in future tasks

### 13.2 When Does Evolution Happen? (Repeat Failure Trigger)

```
Experience log:
  Task 1: Parse JSON → Failure category: "Parse error"
  Task 2: Parse XML → Failure category: "Parse error"  ← 2nd failure in same category
  Task 3: Parse HTML → Failure category: "Parse error" ← 3rd failure in same category

TRIGGER: After 3rd occurrence, governance layer approves evolution.

Evolution layer generates:
  CAP-009 = Universal Parser Capability
  ├── capability.py (parse_universal(data, format))
  ├── tests.py (test_json, test_xml, test_html, test_edge_cases)
  └── metadata.json (v1.0.0, created_date, origin: "repeat_parse_failures")

Commit: "EVOLUTION: CAP-009 Universal Parser generated after 3 repeated parse failures (T1, T2, T3)"
```

### 13.3 Complete Evolution Workflow

```
Layer 3 (Experience) detects repeated failure pattern
          ↓
Layer 4 (Meta-Learning) analyzes pattern frequency
          ↓
Layer 7 (Governance) checks: "Is risk acceptable? Is DNA violated?"
          ↓
If approved → Layer 8 (Evolution) generates new capability
          ↓
Layer 6 (Validation) tests the new capability in sandbox
          ↓
If tests pass → Layer 9 (Registry) registers capability
          ↓
Layer 10 (Execution) commits to GitHub
```

This workflow is what you measure and demonstrate in the thesis.

---

## PART V: DEVELOPMENT ROADMAP

## 14. PHASES 0-10: COMPLETE SPECIFICATIONS (INSTRUCTION MANUAL FORMAT)

### **This section is the PRIMARY REFERENCE for AI coding agents.**

---

### PHASE 0: PROJECT SETUP & INFRASTRUCTURE (Weeks 1-2) — ✅ COMPLETE (v0.3.0)

**Purpose:** Establish development environment, version control, and local LLM.

**Status:** Phase 0 is implemented and pushed to [github.com/muhammadnaumantahir/SPS_CA](https://github.com/muhammadnaumantahir/SPS_CA) (45 commits on `main` as of this update, repo status "Architecture Foundation", `README.md` version tag **0.3.0**). The directory layout, model choice, and supporting docs below reflect the **as-built** repository, not the original v4.0 plan — see the v4.1 change log at the top of this document for what changed and why.

**As-Built Directory Structure:**

```
SPS_CA/
├── README.md                 # Project overview, architecture summary, setup quick-start
├── REQUIREMENTS.md           # NEW — authoritative hardware/software/model/runtime requirements
├── SETUP.md                  # NEW — full installation & verification procedure
├── SETUP_AND_PUSH.sh         # NEW — setup/bootstrap + git push helper script
├── requirements.txt          # Python dependencies (authoritative package list)
├── setup.py
├── .gitignore
├── Dockerfile                # For reproducibility
├── core/                     # CHANGED — orchestration, state, and event contracts only
│                              #   (NOT the 10 layer files — see layers/ below)
├── layers/                   # CHANGED — one first-class package per SPS layer,
│   │                          #   each owning its own implementation + layer-local tests
│   ├── layer_01_software_dna/
│   ├── layer_02_cognitive_core/
│   ├── layer_03_experience/
│   ├── layer_04_meta_learning/
│   ├── layer_05_adaptation/
│   ├── layer_06_validation/
│   ├── layer_07_governance/
│   ├── layer_08_evolution/
│   ├── layer_09_capability_registry/
│   └── layer_10_execution/
├── models/                   # NEW — provider-neutral model/LLM abstraction (Ollama today;
│                              #   OpenAI/Anthropic adapters possible later, no layer changes needed)
├── coding/                   # NEW — repository discovery, AST/symbol analysis, context
│                              #   assembly, controlled code modification, local Git ops
├── capabilities/             # Capability lifecycle and lineage (seeds + generated)
├── execution/                # NEW — controlled execution infrastructure (tools, processes,
│                              #   snapshots, rollback) — separate from layers/layer_10_execution
├── governance/                # Policy/risk classification/approval infrastructure
│   └── decisions/            # JSON audit trail
├── validation/                # NEW — verification infrastructure — separate from
│                              #   layers/layer_06_validation
├── memory/                    # NEW — runtime conversations/experiences/memories/traces
│                              #   (never committed as user data — see governance boundary)
├── projects/                  # User target projects — kept isolated from SPS source
├── data/                      # NEW — runtime database/users/sessions/exports
├── experience/                 # Task logs and metrics
│   └── logs/
├── ui/                        # UI and visualization
├── testing/                    # RENAMED from tests/ — cross-layer, integration, system,
│                              #   scenario, and baseline/benchmark tests
├── evaluation/                # Evaluation results and checklists
├── analytics/                  # NEW — metrics, capability growth/genealogy graphs,
│                              #   evolution datasets (system-of-record for the future UI)
└── docs/
    └── architecture/
        └── SPS_CA_ARCHITECTURE_V2.md   # NEW — authoritative architecture contract
```

**Key structural decisions made during Phase 0 (not anticipated in v4.0):**

1. **Layers moved out of `core/` into their own `layers/` packages.** Each of the 10 SPS layers now owns its implementation and layer-local tests independently, communicating only through explicit interfaces/events orchestrated by `core/`. This keeps layers from becoming tightly coupled to each other's internals — a stricter interpretation of the "10-layer architecture" than the flat-file v4.0 plan.
2. **Layer-named infrastructure packages were split from the SPS layers themselves.** `governance/`, `validation/`, and `execution/` exist as top-level infrastructure (policy engines, verification tooling, controlled execution/rollback) that `layer_07_governance/`, `layer_06_validation/`, and `layer_10_execution/` build on — separating reusable infrastructure from SPS-specific decision logic.
3. **A provider-neutral model layer (`models/`) was added** so SPS-CA is never hard-wired to one LLM. The initial concrete provider is Ollama running `qwen2.5-coder:7b`; adapters for other local models or cloud APIs (OpenAI, Anthropic) can be added without touching any of the 10 SPS layers.
4. **A dedicated `coding/` subsystem was added** to own repository intelligence (AST/symbol analysis, context assembly, controlled modification, local Git operations) as a service layer — it supplies capabilities to the SPS layers but does not itself make governance or learning decisions.
5. **Runtime data was formally separated from source.** `memory/`, `data/`, and `projects/` hold conversations, experiences, sessions, exports, model caches, and user target-project code — none of this is meant to be committed to Git as source; a configurable external storage root is planned so one SPS-CA installation can later serve multiple projects/users.
6. **`analytics/` was added ahead of the UI** so that capability growth, capability genealogy, task-to-capability lineage, provider performance, and rollback statistics are derived from persisted events/metadata first — the UI (Section 16/17) will visualize this data but is explicitly *not* the system of record.
7. **`tests/` became `testing/`** to hold cross-layer/integration/system/scenario/baseline tests, while each `layers/layer_0N_*/` package keeps its own unit tests locally — a clearer separation between layer-local verification and research-evaluation reproducibility (Section 9, Architecture doc §9).

**Requirements (R0.1 - R0.5) — Status:**

| ID | Requirement | Status |
|----|-------------|--------|
| R0.1 | GitHub repository initialized, `.gitignore` configured | ✅ Done |
| R0.2 | Python 3.11+ venv created, `requirements.txt` populated | ✅ Done |
| R0.3 | Ollama running locally, `qwen2.5-coder:7b` downloaded and tested (superseding the Llama 2 70B / Mixtral 8x7B placeholder — see hardware note below) | ✅ Done |
| R0.4 | Directory structure created (as revised — see as-built tree above) | ✅ Done |
| R0.5 | README, `REQUIREMENTS.md`, `SETUP.md`, `SETUP_AND_PUSH.sh`, Dockerfile, and git infrastructure ready | ✅ Done |

**Hardware note (why the LLM changed from the v4.0 plan):** the actual development machine is 16 GB RAM, Intel HD 620 integrated graphics, i7 7th Gen, with no dedicated GPU. Llama 2 70B and Mixtral 8x7B are infeasible on this hardware; `qwen2.5-coder:7b` was selected as the model that fits, runs on CPU/system memory via Ollama, and is coding-specialized. `Qwen3-Coder` is documented in `REQUIREMENTS.md` as a future upgrade path once stronger hardware is available. This is a zero-cost trade-off consistent with Section 9's philosophy, just resolved with a different concrete model than originally placeholder-specified.

**Definition of Done:**
- [x] All directories created and visible in repo (as revised structure)
- [x] `pip install -r requirements.txt` works without errors
- [x] `ollama pull qwen2.5-coder:7b` and `ollama serve` run and respond to simple queries
- [x] `pytest -q` runs cleanly against the initial (mostly scaffolded) layer packages
- [x] Git history reflects Phase 0 setup (45 commits on `main`)
- [x] Student can explain the zero-cost trade-offs and the structural deviations from the v4.0 plan documented above

**Estimated Time:** 5-10 hours (actual)

**Next phase:** Phase 1 (Layer 1 & Layer 2 implementation, Section 14) now targets `layers/layer_01_software_dna/` and `layers/layer_02_cognitive_core/` as the concrete implementation locations, in place of the original `core/layer_1_dna.py` / `core/layer_2_cognitive_core.py` file paths. Every subsequent phase spec in this section (Phases 1-10) should be read with that same path substitution: `core/layer_N_*.py` → `layers/layer_0N_name/`.

---

### PHASE 1: LAYER 1 & LAYER 2 IMPLEMENTATION (Weeks 3-4)

**Purpose:** Implement Software DNA (Layer 1) and Cognitive Core (Layer 2).

**AI Agent Prompt Template:**

```
PHASE 1: Implement Layer 1 (Software DNA) and Layer 2 (Cognitive Core).

LAYER 1: SOFTWARE DNA

1. Create core/layer_1_dna.py with:
   - DNARule class: immutable constraints
   - CapabilityTemplate class: versioning scheme
   - Seed capability definitions (CAP-001 through CAP-008)

Example structure:
class DNARule:
    id: str                    # rule_001, rule_002, ...
    constraint: str            # "Never modify governance logic"
    severity: Literal["hard", "soft"]  # hard = reject, soft = warn
    
2. Create governance/dna_rules.json:
   {
     "dna_rules": [
       {
         "id": "rule_001",
         "constraint": "Never modify core governance logic",
         "severity": "hard"
       },
       ...
     ]
   }

3. Implement seed capability templates in capabilities/seeds/:
   - CAP-001: Simple Bug Detection
   - CAP-002: Syntax Error Fix
   - CAP-003: Unit Test Generation
   - CAP-004: Loop Optimization
   - CAP-005: Error Handling Pattern
   - CAP-006: Unused Variable Removal
   - CAP-007: Type Annotation Addition
   - CAP-008: Documentation Generation

LAYER 2: COGNITIVE CORE

1. Create core/layer_2_cognitive_core.py with:
   - CognitiveCore class with methods:
     - receive_request(user_request: str, code_context: str) → request_obj
     - analyze_target_project(project_path: str) → project_analysis
     - decompose_task(task: str) → List[subtask]
     - select_candidate_capabilities(analysis: ProjectAnalysis) → List[Capability]
     - plan_modification_strategy(analysis, selected_caps) → plan_obj
     
2. Integrate tree-sitter for language-agnostic parsing:
   from tree_sitter import Language, Parser
   - Support Python, Java, JavaScript, Go, C#
   - Parse user project structure
   - Extract function signatures, dependencies

3. Create core/llm_interface.py:
   - Interface to local Ollama (free LLM)
   - Query format: send code + context, get response
   - Handle timeouts (local inference is slow)

4. Write comprehensive tests:
   - test_dna_rule_enforcement.py (DNA rules cannot be modified)
   - test_cognitive_core_parsing.py (tree-sitter parsing works)
   - test_capability_selection.py (right capabilities are selected)

DELIVERABLES (R1.1 - R1.8):
☐ Layer 1 (DNA) fully implemented
☐ Layer 2 (Cognitive Core) fully implemented
☐ tree-sitter parsing works for Python, Java, JS, Go, C#
☐ Local Ollama integration tested
☐ Seed capabilities (CAP-001 to CAP-008) defined
☐ Unit tests >80% coverage for Layers 1-2
☐ Git commit tagged: phase-1-complete
```

**Requirements (R1.1 - R1.8):**

| ID | Requirement | Status |
|----|-------------|--------|
| R1.1 | Layer 1 (DNA) implemented with immutable rules | — |
| R1.2 | Layer 2 (Cognitive Core) receives and analyzes user requests | — |
| R1.3 | tree-sitter integration works for all 5 target languages | — |
| R1.4 | Local Ollama queries tested and working | — |
| R1.5 | Seed capabilities CAP-001 to CAP-008 defined (structure only, not full implementation) | — |
| R1.6 | Unit tests for Layers 1-2, >80% coverage | — |
| R1.7 | DNA rule enforcement prevents modification of governance | — |
| R1.8 | Git history shows layer implementation | — |

**Definition of Done:**
- [ ] `pytest core/tests/ -v` shows >80% coverage for layers 1-2
- [ ] `python -c "from core.layer_2_cognitive_core import CognitiveCore; cc = CognitiveCore(); print('OK')"` works
- [ ] tree-sitter can parse sample code from all 5 languages
- [ ] All 8 seed capabilities have metadata.json and capability.py stubs
- [ ] Supervisor can review git log and see clear layer progression

**Estimated Time:** 15-20 hours

---

### PHASE 2: LAYERS 3, 4, 5 (EXPERIENCE, META-LEARNING, ADAPTATION) (Weeks 5-6)

**Purpose:** Implement learning and adaptation capabilities.

**AI Agent Prompt Template:**

```
PHASE 2: Implement Layer 3 (Experience), Layer 4 (Meta-Learning), Layer 5 (Adaptation).

LAYER 3: EXPERIENCE LAYER

1. Create core/layer_3_experience.py:
   class Task:
       id: str                          # task_001, task_002, ...
       user_request: str
       target_project: str              # path to project
       target_language: str             # python, java, javascript, go, csharp
       timestamp: datetime
       status: Literal["success", "failure", "partial"]
       selected_capability: str         # CAP-001, CAP-003, ...
       outcome: str
       failure_category: str            # if status == "failure"
       time_taken_seconds: float
       
   class ExperienceLog:
       tasks: List[Task]
       metrics: Dict[str, float]
       
       def add_task(task: Task)
       def get_failure_patterns() → Dict[str, int]  # {failure_category: count}
       def get_capability_success_rate(capability_id) → float
       def save_to_json()
       def load_from_json()

2. Create experience/ directory structure:
   experience/
   ├── logs/
   │   ├── experience_log.json    # All tasks, append-only
   │   └── failure_patterns.json  # Aggregated failure categories

3. Example experience_log.json format:
   {
     "tasks": [
       {
         "id": "task_001",
         "user_request": "Fix bug in routes.py",
         "target_project": "projects/project_a_python",
         "selected_capability": "CAP-002",
         "status": "success",
         "timestamp": "2024-01-15T10:30:00",
         "time_taken_seconds": 45.2
       },
       {
         "id": "task_002",
         "user_request": "Add error handling",
         "selected_capability": "CAP-005",
         "status": "failure",
         "failure_category": "Pattern mismatch",
         "timestamp": "2024-01-15T10:45:00",
         "time_taken_seconds": 62.5
       }
     ]
   }

LAYER 4: META-LEARNING LAYER

1. Create core/layer_4_meta_learning.py:
   class MetaLearner:
       def analyze_failure_patterns(experience_log: ExperienceLog) → Dict[str, int]
       def detect_capability_failure(capability_id, min_occurrences=3) → bool
       def recommend_strategy_change(failed_strategy: str) → str  # new strategy
       def measure_improvement() → float  # percentage improvement
       
       # Example: If CAP-002 fails >20% of the time, recommend trying CAP-003 instead
       
2. Track improvement metrics over time:
   - Metric: "Average success rate per phase"
   - Baseline (Phase 1): 50% success
   - Target: >15% improvement by Phase 10 (65%+ success)

3. Write decision logs:
   {
     "meta_learning_decision_001": {
       "timestamp": "2024-01-15T11:00:00",
       "triggered_by": "CAP-002 failure rate >20%",
       "previous_strategy": "Always try CAP-002 first for syntax fixes",
       "new_strategy": "For JavaScript, try CAP-003 first (error handling pattern)",
       "rationale": "CAP-003 has 15% higher success rate on JS projects",
       "decision_id": "MLD_001"
     }
   }

LAYER 5: ADAPTATION LAYER

1. Create core/layer_5_adaptation.py:
   class Adaptation:
       def can_reuse_capability(current_task, past_capability) → bool
           # Check semantic similarity
           
       def adjust_parameters(capability: Capability, task_context) → Capability
           # Modify: timeout, aggressiveness, language-specific params
           # Example: timeout=5s → 10s for complex parsing tasks
           
       def test_adaptation(adapted_cap, target_code) → bool
           # Run capability on target code in sandbox
           # Log result in experience layer

2. Example adaptation workflow:
   - Task: "Fix parse error in Java project"
   - Past capability reuse: CAP-003 (unit test generation)
   - Adaptation: Increase timeout from 5s to 15s (Java compilation is slower)
   - Log as Type 6 change (adaptation, not evolution)

3. Log all adaptations:
   {
     "adaptation_001": {
       "base_capability": "CAP-003",
       "applied_to_task": "task_045",
       "parameters_changed": {"timeout": "5s → 15s", "language": "python → java"},
       "success": true,
       "timestamp": "2024-01-15T11:30:00"
     }
   }

DELIVERABLES (R2.1 - R2.8):
☐ Layer 3 (Experience) logging all tasks
☐ Layer 4 (Meta-Learning) detecting improvement >5%
☐ Layer 5 (Adaptation) reusing capabilities with parameter adjustment
☐ Failure pattern detection working
☐ Experience log persisted to JSON
☐ Unit tests for Layers 3-5, >80% coverage
☐ Git commit tagged: phase-2-complete
```

**Requirements (R2.1 - R2.8):**

| ID | Requirement | Status |
|----|-------------|--------|
| R2.1 | Layer 3 (Experience) logs all tasks with detailed metadata | — |
| R2.2 | Layer 4 (Meta-Learning) detects failure patterns | — |
| R2.3 | Layer 5 (Adaptation) reuses capabilities with adjusted parameters | — |
| R2.4 | JSON-based task logging works and persists across runs | — |
| R2.5 | Meta-learning improvement tracking in place (baseline vs current) | — |
| R2.6 | Adaptation logged as Type 6 change (not evolution) | — |
| R2.7 | Unit tests for Layers 3-5, >80% coverage | — |
| R2.8 | Git history shows learning progression | — |

**Definition of Done:**
- [ ] `pytest core/tests/test_layer_3_*.py test_layer_4_*.py test_layer_5_*.py -v` >80% coverage
- [ ] `python core/layer_3_experience.py` loads/saves experience_log.json
- [ ] `python core/layer_4_meta_learning.py` identifies failure patterns from experience log
- [ ] `python core/layer_5_adaptation.py` successfully adapts CAP-001 for different language
- [ ] experience/logs/experience_log.json contains at least 5 test tasks
- [ ] Supervisor can see clear progression of improvement over test runs

**Estimated Time:** 20-25 hours

---

### PHASE 3: LAYERS 6, 7 (VALIDATION & V&V, GOVERNANCE) (Weeks 7-8)

**Purpose:** Implement safety and governance mechanisms.

**AI Agent Prompt Template:**

```
PHASE 3: Implement Layer 6 (Validation & V&V) and Layer 7 (Governance).

LAYER 6: VALIDATION & V&V LAYER

1. Create core/layer_6_validation.py:
   class Validator:
       def run_in_sandbox(code_change: str, target_project_path: str) → SandboxResult
           # Execute code modification in isolated environment
           # Compare before/after metrics
           
       def regression_test(before_state, after_state) → RegressionAnalysis
           # Run all tests in target project
           # Check for failures not present in before_state
           
       def performance_check(before_metrics, after_metrics) → PerformanceAnalysis
           # Check for performance degradation
           # Example: execution time increase >20% = regression
           
       def prepare_rollback(change_id: str) → RollbackPlan
           # Store state before change, allow restoration

2. Create sandbox/ directory:
   sandbox/
   ├── __init__.py
   ├── sandbox_executor.py  # Isolated execution
   └── test_runner.py       # Run tests in target project

3. Implement sandbox execution:
   - Docker container for isolation (optional but recommended)
   - Or: subprocess with timeout and resource limits
   - Capture stdout, stderr, exit code
   - Log results in evaluation/sandbox/

4. Track metrics before/after:
   {
     "change_001": {
       "before": {
         "test_count": 42,
         "tests_passing": 42,
         "code_coverage": 85.2,
         "execution_time_ms": 3200
       },
       "after": {
         "test_count": 42,
         "tests_passing": 42,
         "code_coverage": 86.5,
         "execution_time_ms": 3150
       },
       "regression_detected": false,
       "change_approved": true
     }
   }

LAYER 7: GOVERNANCE LAYER

1. Create core/layer_7_governance.py:
   class GovernanceGate:
       def check_dna_violations(proposed_change: Change) → GovernanceResult
           # Check against DNA rules
           # Example: "Never modify governance logic" rule
           
       def assess_risk_level(change: Change) → Literal["low", "medium", "high"]
           # Determine if change is risky
           # Factors: scope (core vs capability?), blast radius, test coverage
           
       def approve_or_reject(change: Change, risk_level) → GovernanceDecision
           # Low risk: auto-approve
           # Medium risk: log decision with rationale
           # High risk: escalate to human (mark for supervisor review)
           
       def log_decision(decision: GovernanceDecision)
           # Append to governance/decisions/*.json with full audit trail

2. DNA rules enforcement:
   governance/dna_rules.json:
   {
     "dna_rules": [
       {
         "id": "rule_001",
         "constraint": "Never modify core governance logic (core/layer_7*.py)",
         "severity": "hard",
         "affected_files": ["core/layer_7*.py", "core/governance_layer.py"]
       },
       {
         "id": "rule_002",
         "constraint": "Never delete existing capabilities (only version-bump)",
         "severity": "hard"
       },
       {
         "id": "rule_003",
         "constraint": "All generated capabilities must have >80% test coverage",
         "severity": "soft"
       }
     ]
   }

3. Decision logging example:
   governance/decisions/decision_001.json:
   {
     "id": "decision_001",
     "timestamp": "2024-01-15T12:00:00",
     "proposed_change": "Modify CAP-003 entry point signature",
     "change_type": 6,  # Adaptation
     "dna_violations": [],
     "risk_assessment": {
       "risk_level": "medium",
       "factors": ["Changes capability interface", "Has 5 existing reuse cases"]
     },
     "decision": "requires_human_approval",
     "human_approval_status": "pending",
     "human_reviewer": null,
     "rationale": "Capability interface changes require supervisor verification"
   }

4. Escalation workflow:
   - Low risk changes: Auto-approve, log decision
   - Medium/High risk: Mark in governance/decisions/ with status: "pending_human_review"
   - Supervisor reviews evaluation/governance_decisions/ periodically
   - Supervisor approves/rejects and signs off

DELIVERABLES (R3.1 - R3.8):
☐ Layer 6 (Validation) runs changes in sandbox
☐ Layer 7 (Governance) enforces DNA rules
☐ Before/after metrics logged
☐ Regression testing working
☐ DNA violations cause rejection
☐ High-risk changes escalated to supervisor
☐ Unit tests for Layers 6-7, >80% coverage
☐ Git commit tagged: phase-3-complete
```

**Requirements (R3.1 - R3.8):**

| ID | Requirement | Status |
|----|-------------|--------|
| R3.1 | Layer 6 (Validation) executes changes in isolated sandbox | — |
| R3.2 | Layer 7 (Governance) checks DNA violations before approval | — |
| R3.3 | Before/after metrics compared, regression detection working | — |
| R3.4 | Risk assessment categorizes changes correctly | — |
| R3.5 | DNA rule violations cause immediate rejection | — |
| R3.6 | High-risk changes escalated to supervisor approval | — |
| R3.7 | Complete audit trail of all decisions logged | — |
| R3.8 | Unit tests for Layers 6-7, >80% coverage | — |

**Definition of Done:**
- [ ] `pytest core/tests/test_layer_6_*.py test_layer_7_*.py -v` >80% coverage
- [ ] Sandbox execution of sample code modification succeeds
- [ ] Proposed DNA violation is rejected with clear message
- [ ] governance/decisions/ contains at least 3 decision logs
- [ ] supervisor can read audit trail and understand all decisions
- [ ] Rollback mechanism tested and working

**Estimated Time:** 20-25 hours

---

### PHASE 4: LAYER 8 (EVOLUTION ENGINE) (Weeks 9-10)

**Purpose:** Implement the core self-programming mechanism.

**AI Agent Prompt Template:**

```
PHASE 4: Implement Layer 8 (Evolution Engine) — THE CORE SELF-PROGRAMMING LAYER.

This is the research centerpiece. The evolution engine generates new capabilities.

LAYER 8: EVOLUTION ENGINE

1. Create core/layer_8_evolution.py:
   class EvolutionEngine:
       def should_evolve(experience_log: ExperienceLog, min_occurrences=3) → bool
           # Check if same failure pattern repeated >= min_occurrences times
           # Example: "Parse error" failure in tasks 1, 5, 12 → evolve
           
       def plan_new_capability(trigger_pattern: str) → CapabilityPlan
           # Design new capability based on failure pattern
           # Plan includes: capability_id, entry_point, supported_languages, test_cases
           
       def generate_capability_code(plan: CapabilityPlan) → str
           # Use local LLM to generate:
           #   - capability.py (with entry point function)
           #   - tests.py (comprehensive test suite)
           #   - metadata.json
           
       def implement_capability(generated_code: str, capability_id: str)
           # Write files to capabilities/generated/CAP-009/ (or next ID)
           # Capability structure:
           #   capabilities/generated/CAP-009/
           #   ├── capability.py
           #   ├── tests.py
           #   ├── metadata.json
           #   └── README.md
           
       def test_capability(capability_id: str) → TestResults
           # Run generated tests in sandbox
           # Verify test coverage >80%
           # Log results in evaluation/evolution/

       def register_capability(capability_id: str)
           # Add to capabilities/registry.json
           # Update capability registry in Layer 9

2. Example evolution workflow:

   Phase 4 experiment task:
   - User request: "Parse multiple file formats"
   - Current best capability: CAP-001 (simple bug detection)
   - Result: Fails (unstructured parsing not covered)
   - Experience log shows:
     * task_010: Parse JSON → Fail (CAP-001)
     * task_015: Parse XML → Fail (CAP-001)
     * task_020: Parse CSV → Fail (CAP-001)
   
   Trigger: 3 repeated "Parse error" failures
   
   Evolution:
   1. EvolutionEngine.should_evolve() returns True
   2. plan_new_capability("parsing") creates plan for CAP-009
   3. generate_capability_code() produces:
   
      # capabilities/generated/CAP-009/capability.py
      def universal_parser(data: str, format: str) → Dict:
          """Parse JSON, XML, CSV, YAML into common format."""
          # Implementation
          pass
      
      # capabilities/generated/CAP-009/tests.py
      import pytest
      from capability import universal_parser
      
      def test_parse_json():
          assert universal_parser('{"key": "value"}', 'json') == {"key": "value"}
      
      def test_parse_xml():
          # XML parsing tests
          pass
          
      def test_parse_csv():
          # CSV parsing tests
          pass
      
      # capabilities/generated/CAP-009/metadata.json
      {
        "id": "CAP-009",
        "name": "Universal Parser",
        "version": "1.0.0",
        "created_date": "2024-01-20T14:00:00",
        "entry_point": "universal_parser",
        "supported_languages": ["python", "java", "javascript"],
        "dependencies": [],
        "test_coverage": 87.5,
        "reuse_count": 0,
        "generated": true,
        "origin": "phase_4_evolution_trial",
        "failure_pattern": "repeated_parsing_failures",
        "trigger_tasks": ["task_010", "task_015", "task_020"]
      }

   4. test_capability("CAP-009") runs all tests in sandbox → PASS
   5. register_capability("CAP-009") adds to registry
   6. Commit to GitHub:
      "EVOLUTION: CAP-009 Universal Parser generated from repeated parse failures (tasks 10, 15, 20). Test coverage: 87.5%"

3. Failure pattern detection (from Layer 3 + Layer 4):
   - Extract failure_category from experience log
   - Count occurrences per category
   - Group by target language/domain
   - Example distribution:
     * "Parse error": 5 occurrences → generate parsing capability
     * "Type mismatch": 3 occurrences → generate type validation capability
     * "Edge case handling": 4 occurrences → generate edge case handler

4. Capability generation quality gates:
   - [ ] Generated code is syntactically valid Python
   - [ ] All tests pass (run in sandbox)
   - [ ] Test coverage >80%
   - [ ] Documentation present
   - [ ] Metadata.json correctly formatted
   - [ ] DNA rules not violated (Layer 7 check)

5. Commit message format (GitHub):
   EVOLUTION: CAP-{ID} {Capability Name}
   Generated from repeated {failure_pattern} failures (tasks: {task_ids}).
   Test coverage: {coverage}%. Entry point: {function_name}().
   Supported languages: {languages}.
   
   Trigger rationale: {brief explanation}
   Decision: {governance decision ID}

DELIVERABLES (R4.1 - R4.8):
☐ Layer 8 (Evolution) generates new capabilities
☐ Repeated failure detection working (min 3 occurrences)
☐ Generated capabilities are executable Python modules
☐ Tests generated and passing >80% coverage
☐ Capabilities registered in registry
☐ GitHub commits show evolution with reasoning
☐ Unit tests for Layer 8, >80% coverage
☐ Git commit tagged: phase-4-complete
```

**Requirements (R4.1 - R4.8):**

| ID | Requirement | Status |
|----|-------------|--------|
| R4.1 | Layer 8 (Evolution) generates new Python capability modules | — |
| R4.2 | Repeated failure pattern detection working | — |
| R4.3 | Generated capabilities have capability.py + tests.py + metadata.json | — |
| R4.4 | Generated test coverage >80% | — |
| R4.5 | Generated capabilities are executable and passing tests | — |
| R4.6 | Capabilities registered in registry.json | — |
| R4.7 | GitHub commits show evolution with clear reasoning | — |
| R4.8 | Unit tests for Layer 8, >80% coverage | — |

**Definition of Done:**
- [ ] `pytest core/tests/test_layer_8_*.py -v` >80% coverage
- [ ] Generate a test capability (CAP-009) manually following the algorithm
- [ ] capabilities/generated/CAP-009/ has all required files
- [ ] `pytest capabilities/generated/CAP-009/tests.py -v` passes
- [ ] capabilities/registry.json includes CAP-009 with correct metadata
- [ ] supervisor sees git commit with evolution reasoning
- [ ] Can demonstrate full evolution workflow end-to-end

**Estimated Time:** 25-30 hours

---

### PHASE 5: LAYERS 9, 10 (CAPABILITY REGISTRY, EXECUTION) (Weeks 11-12)

**Purpose:** Complete the self-programming architecture with capability management and execution.

**AI Agent Prompt Template:**

```
PHASE 5: Implement Layer 9 (Capability Registry) and Layer 10 (Execution).

LAYER 9: CAPABILITY REGISTRY

1. Create core/layer_9_registry.py:
   class CapabilityRegistry:
       def register(capability: Capability)
           # Add to registry.json
           # Update reuse_count = 0 for new capabilities
           
       def query_by_type(task_type: str) → List[Capability]
           # Find capabilities matching task type
           # Example: "bug_detection" → [CAP-001, CAP-009]
           
       def query_by_language(language: str) → List[Capability]
           # Find capabilities supporting target language
           # Example: "java" → [CAP-001, CAP-003, CAP-005, CAP-009]
           
       def get_capability(capability_id: str) → Capability
           # Retrieve full capability object
           
       def update_reuse_count(capability_id: str, increment=1)
           # Track how often capability is used
           # Useful for evaluating capability value

2. capabilities/registry.json structure:
   {
     "capabilities": [
       {
         "id": "CAP-001",
         "name": "Simple Bug Detection",
         "type": "analysis",
         "entry_point": "analyze_simple_bugs",
         "supported_languages": ["python", "java", "javascript", "go", "csharp"],
         "version": "1.0.0",
         "created_date": "2024-01-01",
         "last_modified": "2024-01-01",
         "generated": false,
         "origin": null,
         "failure_pattern": null,
         "reuse_count": 3,
         "test_coverage": 85.0,
         "documentation": "capabilities/seeds/CAP-001/README.md"
       },
       {
         "id": "CAP-009",
         "name": "Universal Parser",
         "type": "parsing",
         "entry_point": "universal_parser",
         "supported_languages": ["python", "java", "javascript"],
         "version": "1.0.0",
         "created_date": "2024-01-20",
         "last_modified": "2024-01-20",
         "generated": true,
         "origin": "phase_4_evolution",
         "failure_pattern": "repeated_parsing_failures",
         "reuse_count": 0,
         "test_coverage": 87.5,
         "documentation": "capabilities/generated/CAP-009/README.md"
       }
     ]
   }

3. Registry API:
   - GET /registry → List all capabilities
   - GET /registry/{id} → Get specific capability
   - POST /registry/{id}/reuse → Increment reuse count
   - GET /registry/search?type=bug_detection&language=java → Query

LAYER 10: EXECUTION LAYER

1. Create core/layer_10_execution.py:
   class ExecutionEngine:
       def execute_change(change: Change, target_project_path: str) → ExecutionResult
           # Apply validated change to user project
           # Log execution with outcome
           
       def monitor_execution(change_id: str)
           # Watch for regressions during/after execution
           # Trigger rollback if needed
           
       def execute_rollback(change_id: str) → RollbackResult
           # Restore project to pre-change state
           # Verify rollback success
           
       def update_metrics(change_id: str, result: ExecutionResult)
           # Update experience layer with outcome
           # Track success/failure ratio

2. Change application:
   - Modify target files based on generated code
   - Run tests immediately after
   - If tests pass: mark as committed
   - If tests fail: trigger rollback (Layer 6 should catch this in sandbox, but double-check)

3. Example execution:
   Change 001: Fix bug in project_a_python/routes.py
   1. Apply change: write fix to file
   2. Run tests: pytest project_a_python/tests/ (expect all to pass)
   3. Compare metrics (should match sandbox results)
   4. If all pass: commit to target project git
   5. If any fail: rollback and log failure

4. Rollback mechanism:
   - Store file hashes before change
   - Before/after snapshots
   - Git restore if target project is a git repo
   - Manual file restoration if not

5. Execution logging:
   evaluation/execution/execution_log.json:
   {
     "executions": [
       {
         "id": "exec_001",
         "change_id": "change_001",
         "capability_id": "CAP-002",
         "target_project": "projects/project_a_python",
         "target_language": "python",
         "timestamp": "2024-01-20T15:00:00",
         "status": "success",
         "tests_passing": 42,
         "tests_failing": 0,
         "code_coverage": 86.5,
         "execution_time_ms": 3200,
         "rollback_triggered": false
       }
     ]
   }

DELIVERABLES (R5.1 - R5.8):
☐ Layer 9 (Registry) manages all capabilities
☐ Layer 10 (Execution) applies changes to user projects
☐ Rollback tested and working
☐ Execution metrics logged
☐ Registry API queries work correctly
☐ Reuse counts updated on capability usage
☐ Unit tests for Layers 9-10, >80% coverage
☐ Git commit tagged: phase-5-complete
```

**Requirements (R5.1 - R5.8):**

| ID | Requirement | Status |
|----|-------------|--------|
| R5.1 | Layer 9 (Registry) maintains capability index | — |
| R5.2 | Layer 10 (Execution) applies changes to target projects | — |
| R5.3 | Capability reuse counts tracked | — |
| R5.4 | Rollback mechanism works and verified | — |
| R5.5 | Execution metrics logged accurately | — |
| R5.6 | Registry queries (by type, language, domain) work | — |
| R5.7 | Unit tests for Layers 9-10, >80% coverage | — |
| R5.8 | All 10 layers now integrated end-to-end | — |

**Definition of Done:**
- [ ] `pytest core/tests/test_layer_9_*.py test_layer_10_*.py -v` >80% coverage
- [ ] `python core/layer_9_registry.py query --type analysis` returns results
- [ ] Execute a change end-to-end and verify metrics logged
- [ ] Trigger rollback and confirm file restoration
- [ ] All 10 layers pass integration test
- [ ] supervisor can see complete architecture working

**Estimated Time:** 20-25 hours

---

### PHASE 6: INITIAL CAPABILITY IMPLEMENTATION (Weeks 13-14)

**Purpose:** Implement all 8 seed capabilities (CAP-001 through CAP-008) with real logic.

**AI Agent Prompt Template:**

```
PHASE 6: Implement all 8 Seed Capabilities (CAP-001 through CAP-008).

Each capability is a standalone Python module with:
- capability.py: entry point function
- tests.py: comprehensive test suite (>80% coverage)
- metadata.json: versioning and metadata
- README.md: documentation

SEED CAPABILITIES TO IMPLEMENT:

CAP-001: Simple Bug Detection
  Entry point: analyze_simple_bugs(code: str, language: str) → List[Dict]
  Purpose: Identify obvious bugs (unused variables, type mismatches, null dereferences)
  Languages: Python, Java, JavaScript, Go, C#
  Test coverage: >80%
  Example: Detect `x = 5; y = x + 1; print(y)` as "unused variable x"

CAP-002: Syntax Error Fix
  Entry point: fix_syntax_errors(code: str, language: str) → str
  Purpose: Auto-fix common syntax errors
  Languages: Python, Java, JavaScript, Go, C#
  Test coverage: >80%
  Example: Fix `if x = 5:` → `if x == 5:` (Python)

CAP-003: Unit Test Generation
  Entry point: generate_unit_tests(function_code: str, language: str) → str
  Purpose: Generate comprehensive test cases for a function
  Languages: Python, Java, JavaScript, Go, C#
  Test coverage: >80%
  Example: Generate tests for `def add(a, b): return a + b`
           Tests: test_add_positive(), test_add_negative(), test_add_zero(), test_add_type_error()

CAP-004: Loop Optimization
  Entry point: optimize_loops(code: str, language: str) → str
  Purpose: Optimize inefficient loops (e.g., remove redundant computations)
  Languages: Python, Java, JavaScript, Go, C#
  Test coverage: >80%
  Example: Move invariant computation outside loop

CAP-005: Error Handling Pattern
  Entry point: add_error_handling(code: str, language: str) → str
  Purpose: Add try-catch blocks and error handling
  Languages: Python, Java, JavaScript, Go, C#
  Test coverage: >80%
  Example: Wrap file operations in try-except

CAP-006: Unused Variable Removal
  Entry point: remove_unused_variables(code: str, language: str) → str
  Purpose: Identify and remove unused variables
  Languages: Python, Java, JavaScript, Go, C#
  Test coverage: >80%
  Example: Remove `x = 5` if x is never referenced

CAP-007: Type Annotation Addition
  Entry point: add_type_annotations(code: str, language: str) → str
  Purpose: Add type hints/annotations to functions
  Languages: Python, Java, JavaScript (TypeScript), Go, C#
  Test coverage: >80%
  Example: `def add(a, b): return a + b` →
           `def add(a: int, b: int) -> int: return a + b` (Python)

CAP-008: Documentation Generation
  Entry point: generate_docstrings(code: str, language: str) → str
  Purpose: Generate docstrings/documentation for functions
  Languages: Python, Java, JavaScript, Go, C#
  Test coverage: >80%
  Example: Generate Sphinx/JavaDoc/JSDoc docstrings

IMPLEMENTATION GUIDELINES:

1. Use tree-sitter for language-agnostic AST parsing where possible
2. Leverage local LLM for code generation (where appropriate)
3. Each capability must be language-aware but framework-agnostic
4. Write tests that cover:
   - Happy path (correct input)
   - Edge cases (empty code, single line, etc.)
   - Language-specific cases (Python indent, Java braces, etc.)
   - Error cases (syntax errors, unsupported patterns)

5. Directory structure:
   capabilities/seeds/CAP-001/
   ├── capability.py       # Main entry point
   ├── tests.py           # Comprehensive tests
   ├── metadata.json      # Metadata
   └── README.md          # Documentation

6. Example test suite (CAP-001):
   # capabilities/seeds/CAP-001/tests.py
   import pytest
   from capability import analyze_simple_bugs
   
   def test_unused_variable_detection():
       code = "x = 5\nprint(3)"
       bugs = analyze_simple_bugs(code, 'python')
       assert any(b['issue'] == 'unused_variable' for b in bugs)
   
   def test_type_mismatch_detection():
       code = 'x = "hello"\ny = x + 5'
       bugs = analyze_simple_bugs(code, 'python')
       assert any(b['issue'] == 'type_mismatch' for b in bugs)
   
   def test_no_bugs():
       code = "x = 5\nprint(x)"
       bugs = analyze_simple_bugs(code, 'python')
       assert len(bugs) == 0
   
   def test_java_unused_variable():
       code = '''public class Test {
         public static void main() {
           int x = 5;
           System.out.println(3);
         }
       }'''
       bugs = analyze_simple_bugs(code, 'java')
       assert any(b['issue'] == 'unused_variable' for b in bugs)

DELIVERABLES (R6.1 - R6.8):
☐ All 8 seed capabilities implemented (CAP-001 through CAP-008)
☐ Each capability: capability.py + tests.py + metadata.json + README.md
☐ Each capability supports all 5 target languages
☐ Test coverage >80% for each capability
☐ All capabilities pass tests in sandbox
☐ Capabilities correctly registered in registry.json
☐ Cross-language test cases working
☐ Git commit tagged: phase-6-complete
```

**Requirements (R6.1 - R6.8):**

| ID | Requirement | Status |
|----|-------------|--------|
| R6.1 | CAP-001 through CAP-008 fully implemented | — |
| R6.2 | Each capability supports Python, Java, JavaScript, Go, C# | — |
| R6.3 | Each capability has >80% test coverage | — |
| R6.4 | All capabilities pass tests independently | — |
| R6.5 | Capabilities registered in registry.json | — |
| R6.6 | Language-agnostic parsing (tree-sitter) working | — |
| R6.7 | Cross-language capability reuse tested | — |
| R6.8 | Documentation for each capability present | — |

**Definition of Done:**
- [ ] `pytest capabilities/seeds/CAP-*/tests.py -v` all pass, >80% coverage
- [ ] `python core/layer_9_registry.py query --all` shows CAP-001 through CAP-008
- [ ] Each capability works on sample code in all 5 languages
- [ ] supervisor can review README.md for each capability
- [ ] No hardcoded language assumptions in any capability

**Estimated Time:** 25-30 hours

---

### PHASE 7: USER INTERFACE & PROMPT-BASED INTERACTION (Weeks 15-16)

**Purpose:** Build simple prompt-based UI (like ChatGPT) for user interaction.

**AI Agent Prompt Template:**

```
PHASE 7: Build User Interface — Prompt-Based Interaction Layer.

PHILOSOPHY: Simple prompt-based interface, like ChatGPT.
- Users type requests in natural language
- Optional: paste code snippets for context
- SPS-CA responds with modifications and explanations
- No complex UI, no dashboards yet

UI COMPONENTS:

1. Create ui/cli_interface.py:
   class SPS_CA_Interface:
       def __init__(self):
           self.core = SPS_Core()  # Initialize all 10 layers
           self.project_context = None
           
       def start_interactive_session(self):
           """REPL-style chat interface"""
           print("Welcome to SPS-CA (Self-Programming Code Assistant)")
           print("Type 'help' for commands, 'quit' to exit")
           
           while True:
               user_input = input("You: ").strip()
               
               if user_input.lower() == 'quit':
                   break
               elif user_input.lower() == 'help':
                   self.show_help()
               elif user_input.lower().startswith('load '):
                   project_path = user_input[5:].strip()
                   self.load_project(project_path)
               elif user_input.lower().startswith('show '):
                   context = user_input[5:].strip()
                   self.show_context(context)
               else:
                   # Process user request
                   response = self.process_request(user_input)
                   print(f"\nSPS-CA: {response}\n")

       def process_request(self, user_request: str) → str:
           """
           Main processing pipeline:
           1. Parse request
           2. Analyze context (project + code)
           3. Select/generate capability
           4. Run in sandbox
           5. Get approval if high-risk
           6. Apply change
           7. Return result
           """
           try:
               # Layer 2: Analyze request
               analysis = self.core.cognitive_core.receive_request(
                   user_request, 
                   project_context=self.project_context
               )
               
               # Layer 5/8: Adapt or evolve
               capability = self.core.select_capability(analysis)
               
               # Layer 6: Validate in sandbox
               sandbox_result = self.core.validation.run_in_sandbox(
                   capability, 
                   self.project_context
               )
               
               if not sandbox_result.success:
                   return f"Validation failed: {sandbox_result.error}"
               
               # Layer 7: Governance check
               governance = self.core.governance.check_approval(
                   capability, 
                   sandbox_result
               )
               
               if governance.requires_human_approval:
                   return (
                       f"High-risk change requires approval.\n"
                       f"Decision: {governance.decision_id}\n"
                       f"Please review: evaluation/governance_decisions/{governance.decision_id}.json"
                   )
               
               # Layer 10: Execute
               execution = self.core.execution.execute_change(
                   capability,
                   self.project_context
               )
               
               # Return summary
               return self.format_response(execution)
               
           except Exception as e:
               return f"Error: {str(e)}"

       def load_project(self, project_path: str):
           """Load a target project for analysis"""
           self.project_context = {
               'path': project_path,
               'language': self.detect_language(project_path),
               'structure': self.analyze_structure(project_path)
           }
           print(f"Loaded project: {project_path} (language: {self.project_context['language']})")
       
       def show_context(self, context_type: str):
           """Show current analysis context"""
           if context_type == 'project':
               print(f"Current project: {self.project_context['path']}")
               print(f"Language: {self.project_context['language']}")
           elif context_type == 'registry':
               capabilities = self.core.registry.get_all()
               print("Available capabilities:")
               for cap in capabilities:
                   print(f"  {cap['id']}: {cap['name']}")
           elif context_type == 'experience':
               tasks = self.core.experience.get_recent_tasks(count=5)
               print("Recent tasks:")
               for task in tasks:
                   print(f"  {task['id']}: {task['status']}")

       def format_response(self, execution_result: Dict) → str:
           """Format execution result for user"""
           if execution_result['status'] == 'success':
               return (
                   f"✓ Change applied successfully!\n"
                   f"  Tests passing: {execution_result['tests_passing']}/{execution_result['tests_total']}\n"
                   f"  Code coverage: {execution_result['code_coverage']}%\n"
                   f"  Execution time: {execution_result['time_ms']}ms\n"
                   f"  Capability used: {execution_result['capability_id']}"
               )
           else:
               return f"✗ Change failed: {execution_result['error']}"

2. Command reference:
   Commands:
   - load <project_path>      Load a target project
   - show <context>           Show current context (project, registry, experience)
   - help                     Show this help
   - quit                     Exit SPS-CA
   
   Example session:
   > load projects/project_a_python
   Loaded project: projects/project_a_python (language: python)
   
   > Fix the bug in routes.py where users aren't filtered correctly
   SPS-CA: Analyzing... Selected CAP-002 (Syntax Error Fix) → ...
           ✓ Change applied successfully!
           Tests passing: 42/42
           Code coverage: 86.5%
   
   > Show registry
   Available capabilities:
   - CAP-001: Simple Bug Detection
   - CAP-002: Syntax Error Fix
   - ...
   
   > Add unit tests for the new function in services.py
   SPS-CA: Analyzing... Selected CAP-003 (Unit Test Generation) → ...
           ✓ Change applied successfully!
           ...

3. Logging & history:
   - Save all user requests and responses
   - ui/session_history.json tracks all interactions
   - Tie to experience log (Layer 3) for learning

DELIVERABLES (R7.1 - R7.5):
☐ CLI interface implemented (simple, prompt-based)
☐ Commands: load, show, help, quit
☐ Session history tracking
☐ User requests routed through all 10 layers
☐ Response formatting clear and informative
☐ Git commit tagged: phase-7-complete
```

**Requirements (R7.1 - R7.5):**

| ID | Requirement | Status |
|----|-------------|--------|
| R7.1 | CLI interface with prompt-based interaction | — |
| R7.2 | Commands work: load, show, help, quit | — |
| R7.3 | User requests routed through cognitive core | — |
| R7.4 | Session history tracked | — |
| R7.5 | Response formatting is clear and actionable | — |

**Definition of Done:**
- [ ] `python ui/cli_interface.py` starts interactive session
- [ ] `load projects/project_a_python` loads a project
- [ ] User can type a request and receive response
- [ ] All requests are logged in ui/session_history.json
- [ ] Response includes capability used, test results, coverage

**Estimated Time:** 15-20 hours

---

### PHASE 8: THREE TARGET PROJECTS (Weeks 17-18)

**Purpose:** Create 3 projects with equivalent functionality in Python, Java, TypeScript.

**AI Agent Prompt Template:**

```
PHASE 8: Create Three Target Projects (Functional Equivalence Group).

These are the user projects that SPS-CA will analyze and modify during evaluation.

PROJECT A: Python + FastAPI
- Framework: FastAPI
- Domain: REST API with user and task management
- Size: ~300-500 LOC
- Directory: projects/project_a_python/
- Features:
  * User CRUD (GET, POST, PUT, DELETE /users/)
  * Task CRUD (GET, POST, PUT, DELETE /tasks/)
  * Filtering (GET /users?name=john, GET /tasks?status=done)
  * Error handling (404, 500, validation errors)
  * Logging (info, error, debug)
  * Unit tests (pytest, >80% coverage)
  * Integration tests
  * CI/CD ready (GitHub Actions workflow)

Structure:
projects/project_a_python/
├── main.py              # FastAPI app initialization
├── routes/
│   ├── users.py         # User endpoints
│   └── tasks.py         # Task endpoints
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── database.py          # Database setup
├── config.py            # Configuration
├── requirements.txt
├── tests/
│   ├── test_users.py
│   ├── test_tasks.py
│   ├── test_models.py
│   └── conftest.py
├── .github/workflows/ci.yml
└── README.md

PROJECT B: Java + Spring Boot
- Framework: Spring Boot
- Domain: Same REST API (users + tasks)
- Size: ~300-500 LOC (Java is verbose)
- Directory: projects/project_b_java/
- Features: Same as Project A, but in Java/Spring conventions

Structure:
projects/project_b_java/
├── pom.xml              # Maven config
├── src/main/java/com/spsca/
│   ├── SpsApp.java      # Spring Boot main
│   ├── controller/
│   │   ├── UserController.java
│   │   └── TaskController.java
│   ├── model/
│   │   ├── User.java
│   │   └── Task.java
│   ├── repository/
│   │   ├── UserRepository.java
│   │   └── TaskRepository.java
│   ├── service/
│   │   ├── UserService.java
│   │   └── TaskService.java
│   ├── config/
│   │   └── DatabaseConfig.java
│   └── exception/
│       └── GlobalExceptionHandler.java
├── src/test/java/...  # Same structure with tests
└── README.md

PROJECT C: TypeScript + Express.js
- Framework: Express.js
- Domain: Same REST API (users + tasks)
- Size: ~300-500 LOC
- Directory: projects/project_c_typescript/
- Features: Same as Project A, but in TypeScript

Structure:
projects/project_c_typescript/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts         # Express app initialization
│   ├── routes/
│   │   ├── users.ts
│   │   └── tasks.ts
│   ├── models/
│   │   ├── User.ts
│   │   └── Task.ts
│   ├── middlewares/
│   │   ├── errorHandler.ts
│   │   └── logger.ts
│   ├── database.ts      # SQLite setup
│   └── config.ts
├── tests/
│   ├── users.test.ts
│   ├── tasks.test.ts
│   └── models.test.ts
├── .github/workflows/ci.yml
└── README.md

FUNCTIONALITY MATRIX (ensure all 3 implement the same features):

| Feature | Python | Java | TypeScript | Notes |
|---------|--------|------|------------|-------|
| User CRUD | ✓ | ✓ | ✓ | Same logic, language-specific syntax |
| Task CRUD | ✓ | ✓ | ✓ | Same logic, language-specific syntax |
| Filtering | ✓ | ✓ | ✓ | Query parameters |
| Error Handling | ✓ | ✓ | ✓ | Try-catch, HTTP status codes |
| Logging | ✓ | ✓ | ✓ | Log all API calls |
| Unit Tests | ✓ | ✓ | ✓ | >80% coverage each |
| Integration Tests | ✓ | ✓ | ✓ | Full API flow tests |

INTENTIONAL BUGS & ISSUES (for evaluation scenarios):

Each project should have:
- 3-5 intentional bugs (for SPS-CA to find and fix):
  * Off-by-one error in filtering
  * Missing error handling on edge case
  * Unused variable/import
  * Type mismatch (if applicable)
  * Missing test coverage

- 2-3 areas for refactoring:
  * Repeated code pattern
  * Complex function that could be decomposed
  * Missing documentation

- 1-2 areas for feature addition:
  * New endpoint
  * Enhanced filtering

This makes scenarios realistic and measurable.

DELIVERABLES (R8.1 - R8.5):
☐ Project A (Python/FastAPI) complete with all features
☐ Project B (Java/Spring Boot) complete with all features
☐ Project C (TypeScript/Express.js) complete with all features
☐ Functional equivalence verified (same features, same bugs)
☐ All projects have tests and CI workflows
☐ Git commit tagged: phase-8-complete
```

**Requirements (R8.1 - R8.5):**

| ID | Requirement | Status |
|----|-------------|--------|
| R8.1 | Project A (Python) complete and runnable | — |
| R8.2 | Project B (Java) complete and runnable | — |
| R8.3 | Project C (TypeScript) complete and runnable | — |
| R8.4 | All 3 projects have equivalent features/bugs | — |
| R8.5 | Tests >80% coverage in all projects | — |

**Definition of Done:**
- [ ] Each project runs standalone (`python main.py`, `mvn spring-boot:run`, `npm start`)
- [ ] Each project has >80% test coverage
- [ ] Features matrix complete (all 3 projects have same logic)
- [ ] Intentional bugs present and documented
- [ ] supervisor can run all 3 projects without errors

**Estimated Time:** 20-25 hours

---

### PHASE 9: BASELINE AGENT IMPLEMENTATION (Weeks 19-20)

**Purpose:** Implement Baseline A (Naive LLM) and Baseline B (Coding Agent + Tool Registry) for comparison.

**AI Agent Prompt Template:**

```
PHASE 9: Implement Baseline Agents A and B for comparison.

These baselines help isolate the contribution of the SPS-CA framework.

BASELINE A: Naive LLM Agent

1. Create baselines/baseline_a_naive_llm.py:
   class BaselineA_NaiveLLM:
       def process_request(self, user_request: str, project_context: str) → str:
           """
           Naive approach: Send user request + code directly to LLM, get code back.
           No learning, no adaptation, no self-modification.
           """
           prompt = f"""
           User request: {user_request}
           
           Project code:
           {project_context}
           
           Generate modified code that fulfills the request.
           Output only the modified code, no explanation.
           """
           
           response = self.call_local_llm(prompt)
           return response

2. Metrics:
   - Task success rate (does generated code work?)
   - Time to first solution
   - Test passing rate
   - No capability registry, no learning, no adaptation

BASELINE B: Coding Agent + Tool Registry

1. Create baselines/baseline_b_coding_agent.py:
   class BaselineB_CodingAgent:
       def __init__(self):
           self.tool_registry = {
               "syntax_check": self.check_syntax,
               "run_tests": self.run_tests,
               "analyze_code": self.analyze_code,
           }
       
       def process_request(self, user_request: str, project_context: str) → str:
           """
           Better approach: Use tools to analyze, plan, execute.
           Has tool registry, but no learning or capability generation.
           """
           # 1. Analyze with tools
           analysis = self.tool_registry["analyze_code"](project_context)
           
           # 2. Plan solution
           prompt = f"""
           Request: {user_request}
           Analysis: {analysis}
           
           Plan the solution step by step.
           """
           plan = self.call_local_llm(prompt)
           
           # 3. Generate code with tools
           code = self.generate_code(plan, project_context)
           
           # 4. Test with tools
           test_result = self.tool_registry["run_tests"](code)
           
           if test_result['passing']:
               return code
           else:
               # Retry with feedback
               code = self.generate_code_with_feedback(plan, test_result)
               return code

2. Tool registry:
   - syntax_check: Check generated code for syntax errors
   - run_tests: Run tests on generated code
   - analyze_code: Analyze project structure
   - format_code: Format code to project style
   - (No capability generation, no self-modification)

3. Metrics:
   - Same as Baseline A, plus:
   - Tool usage frequency
   - Number of retries needed
   - Still no learning or capability reuse

BASELINE C: SPS-CA (Full Framework)

This is what you're building. It has:
- All 10 layers
- Learning (Layer 4)
- Adaptation (Layer 5)
- Evolution (Layer 8)
- Capability registry (Layer 9)

EXPERIMENTAL SETUP

All 3 baselines use the SAME local LLM (Ollama, `qwen2.5-coder:7b` — see Section 9).
This isolates framework effects, not LLM capability.

Execution matrix:
- Baseline A: 25 scenarios × 3 projects = 75 executions
- Baseline B: 25 scenarios × 3 projects = 75 executions
- SPS-CA: 25 scenarios × 3 projects = 75 executions
- Total: 225 executions

DELIVERABLES (R9.1 - R9.5):
☐ Baseline A (Naive LLM) implemented
☐ Baseline B (Coding Agent + Tools) implemented
☐ Both baselines use same local LLM as SPS-CA
☐ Baseline wrappers follow same interface as SPS-CA
☐ Execution framework ready for Phase 10
☐ Git commit tagged: phase-9-complete
```

**Requirements (R9.1 - R9.5):**

| ID | Requirement | Status |
|----|-------------|--------|
| R9.1 | Baseline A (Naive LLM) implemented | — |
| R9.2 | Baseline B (Coding Agent) implemented | — |
| R9.3 | All 3 baselines use same LLM | — |
| R9.4 | Baseline interface matches SPS-CA interface | — |
| R9.5 | Execution framework ready | — |

**Definition of Done:**
- [ ] `python baselines/baseline_a_naive_llm.py --request "fix bug" --project project_a` works
- [ ] `python baselines/baseline_b_coding_agent.py --request "fix bug" --project project_a` works
- [ ] Both return results in same format as SPS-CA
- [ ] Can execute 3 baselines side-by-side for comparison

**Estimated Time:** 15-20 hours

---

### PHASE 10: EXPERIMENTAL EXECUTION & EVALUATION (Weeks 21-22, plus buffer for Phase 10 execution)

**Purpose:** Execute all 25 scenarios, collect metrics, evaluate thesis claims.

**AI Agent Prompt Template:**

```
PHASE 10: Execute 25 Experimental Scenarios & Collect Evidence.

This is the research/evaluation phase. Execute scenarios, collect metrics, validate claims.

EXECUTION WORKFLOW:

1. Create evaluation/scenario_executor.py:
   class ScenarioExecutor:
       def execute_scenario(self, scenario_id: str, baseline: str, project: str):
           """
           Run single scenario against one baseline on one project.
           Collect all metrics and log results.
           """
           # Set up: load project, initialize baseline
           # Execute: run scenario
           # Measure: collect metrics
           # Log: save results
           
2. Metrics collection per execution:
   - Task success: bool (did it work?)
   - Execution time: float (seconds)
   - Tests passing: int (N / M)
   - Code coverage: float (%)
   - Capability used: str (CAP-001, etc.)
   - Change type: int (1-7)
   - Regression detected: bool
   - Rollback used: bool (for SPS-CA only)
   
3. Evaluation forms (Appendix E):
   - Form 1: Phase Definition-of-Done (per phase)
   - Form 2: Scenario Execution Log (per execution)
   - Form 3: Governance Decision Review (per high-risk decision)
   - Form 4: Weekly Supervisor Checkpoint (weekly)
   - Form 5: Final Thesis Artifact Sign-Off (end of Phase 10)

SCENARIO EXECUTION MATRIX:

25 scenarios total:
- Level 1 (Basic Coding): 4 scenarios
- Level 2 (SPS Behavior): 11 scenarios
- Level 3 (Governance & Safety): 10 scenarios

Each scenario executed against:
- Baseline A (Naive LLM)
- Baseline B (Coding Agent)
- SPS-CA

On:
- Project A (Python)
- Project B (Java)
- Project C (TypeScript)

Not all scenarios run on all projects (some language-specific):
- Scenarios S1-S4 (basic): All 3 projects × 3 baselines = 36 executions
- Scenarios S5-S11 (SPS-specific): Mix of projects/scenarios = ~33 executions
- Scenarios S12-S21 (governance): Mix of projects/scenarios = ~33 executions
- Scenarios S22-S25 (extended): Optional, if time permits

Total executions: ~75-90 (depending on scenario distribution)

DELIVERABLES (R10.1 - R10.10):
☐ All 25 scenarios executed
☐ Metrics collected for each execution
☐ Results logged in evaluation/scenarios/
☐ Baseline A vs B vs SPS-CA compared
☐ Cross-project reuse measured >60% (target)
☐ Meta-learning improvement >15% (target)
☐ 15 thesis artifacts collected (Appendix E, Form 5)
☐ Evaluation forms completed and filed
☐ Supervisor checkpoints weekly (Form 4)
☐ Git commit tagged: phase-10-complete
```

**Requirements (R10.1 - R10.10):**

| ID | Requirement | Status |
|----|-------------|--------|
| R10.1 | All 25 scenarios executed against 3 baselines | — |
| R10.2 | Metrics collected for all executions (~75-90 total) | — |
| R10.3 | Baseline A vs B vs SPS-CA comparison completed | — |
| R10.4 | SPS-CA outperforms Baseline B by >15 percentage points | — |
| R10.5 | Cross-language capability reuse >60% | — |
| R10.6 | Meta-learning improvement >15% | — |
| R10.7 | All 15 thesis artifacts collected and signed off | — |
| R10.8 | Evaluation forms (Appendix E) completed | — |
| R10.9 | Git history complete with all phases | — |
| R10.10 | Supervisor approves completion | — |

**Definition of Done:**
- [ ] All execution results in evaluation/scenarios/
- [ ] Baseline comparison metrics calculated
- [ ] Thesis artifacts collected (all 15 from Form 5)
- [ ] Evaluation checklists completed
- [ ] supervisor signature on final sign-off form

**Estimated Time:** Variable (depends on execution time), typically 4-6 weeks

---

## 15. PHASE OVERVIEW TABLE & DEPENDENCIES

| Phase | Title | Duration | Dependencies | Deliverables (R#.#) | Status |
|-------|-------|----------|--------------|-------------------|--------|
| 0 | Project Setup | Weeks 1-2 | — | R0.1-R0.5 | ✅ **Complete** (repo v0.3.0, 45 commits) |
| 1 | Layers 1-2 (`layers/layer_01_software_dna/`, `layers/layer_02_cognitive_core/`) | Weeks 3-4 | Phase 0 | R1.1-R1.8 | Not started |
| 2 | Layers 3-5 | Weeks 5-6 | Phase 1 | R2.1-R2.8 | Not started |
| 3 | Layers 6-7 | Weeks 7-8 | Phase 2 | R3.1-R3.8 | Not started |
| 4 | Layer 8 | Weeks 9-10 | Phase 3 | R4.1-R4.8 | Not started |
| 5 | Layers 9-10 | Weeks 11-12 | Phase 4 | R5.1-R5.8 | Not started |
| 6 | Seed Capabilities | Weeks 13-14 | Phase 5 | R6.1-R6.8 | Not started |
| 7 | User Interface | Weeks 15-16 | Phase 6 | R7.1-R7.5 | Not started |
| 8 | Target Projects | Weeks 17-18 | Phase 7 | R8.1-R8.5 | Not started |
| 9 | Baselines | Weeks 19-20 | Phase 8 | R9.1-R9.5 | Not started |
| 10 | Evaluation | Weeks 21-22+ | Phase 9 | R10.1-R10.10 | Not started |

**Note:** Phase 1 onward, wherever a phase spec references `core/layer_N_*.py`, substitute the as-built path `layers/layer_0N_name/` (see Phase 0 above and Section 6.1 for the full mapping).

**Total Development Time:** ~18-20 weeks (Phases 0-9)  
**Evaluation Time:** ~4-6 weeks (Phase 10)  
**Buffer:** ~4-6 weeks  
**Thesis Writing:** ~8-10 weeks

---

## PART VI: USER INTERACTION & WORKFLOW

## 16. USER INTERFACE & INTERACTION MODEL (Prompt-Based)

### 16.1 Design Principle

**SPS-CA should feel like ChatGPT, not like a specialized tool.**

Users interact via simple text prompts. No complex configuration, no menus.

### 16.2 User Workflow

```
1. USER STARTS SPS-CA
   $ python -m sps_ca
   > Welcome to SPS-CA (Self-Programming Code Assistant)
   > Commands: load <project>, help, show <context>, quit
   > You:

2. USER LOADS A PROJECT
   > load projects/project_a_python
   > Loaded project: projects/project_a_python (language: python)
   > Available: 42 tests, 85.2% coverage
   > You:

3. USER MAKES A REQUEST (IN NATURAL LANGUAGE)
   > Fix the bug in routes.py where users aren't filtered correctly
   > SPS-CA: Analyzing... Selected CAP-002 (Syntax Error Fix)
   >         Applied change to routes.py
   >         ✓ All 42 tests pass | Coverage: 86.5%
   > You:

4. USER ASKS FOR EXPLANATION
   > Why did you use CAP-002?
   > SPS-CA: CAP-002 (Syntax Error Fix) was selected because:
   >         - Your request mentions 'bug fix'
   >         - Previous uses of CAP-002 had 92% success rate on Python projects
   >         - The filtering logic had a type mismatch (syntax error)
   > You:

5. USER ASKS TO REVIEW
   > Show the change
   > SPS-CA: Changed file: routes.py
   >         Line 45: `if user_status = "active"` → `if user_status == "active"`
   >         Reason: Assignment operator (=) should be equality check (==)
   > You:

6. USER APPLIES OR REJECTS
   > Apply this change
   > SPS-CA: ✓ Change applied and committed to project repo
   >         Capability CAP-002 reuse count: 4
   > You:

7. USER MAKES ANOTHER REQUEST
   > Add error handling for JSON parsing
   > SPS-CA: Analyzing... Selected CAP-005 (Error Handling Pattern)
   >         Applied change to services.py
   >         ✓ All 42 tests pass | Coverage: 87.2%
   > You:
```

### 16.3 Commands Reference

```
Commands:

  load <project_path>
    Load a target project for analysis.
    Example: load projects/project_a_python
    
  show <context>
    Show current context or status.
    Contexts:
      project     → Current project info
      registry    → Available capabilities
      experience  → Recent tasks and success rates
      metrics     → Overall performance metrics
    Example: show registry

  help
    Show this help message.

  quit
    Exit SPS-CA.

Natural language requests:
  - Any other input is treated as a user request
  - Type your request in plain English
  - Optional: include code snippets for context
  - Example: "Fix the null pointer exception in services.py"
```

### 16.4 Response Format

Responses should include:

1. **Status:** ✓ (success) or ✗ (failure)
2. **Capability Used:** Which CAP-# was applied
3. **Metrics:** Tests passing, coverage change
4. **Explanation:** Why that capability was chosen
5. **Next Steps:** What to do next (review, approve, adjust)

---

## 17. USER PROJECT vs SPS SELF-CHANGE ARCHITECTURE

### 17.1 Clear Separation of Concerns

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPS-CA INTERNAL SYSTEM                        │
│  (Python, self-modifying, subject of research)                  │
│                                                                 │
│  - Layers 1-10                                                  │
│  - Cognitive Core                                               │
│  - Experience & Learning                                        │
│  - Meta-Learning                                                │
│  - Adaptation & Evolution                                       │
│  - Governance & Validation                                      │
│  - Capability Registry (versioned modules)                      │
│                                                                 │
│  Output: capabilities/generated/CAP-*/                          │
│  (New Python modules committed to GitHub)                       │
│                                                                 │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                  OPERATES ON (analyzes, modifies)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               USER TARGET PROJECT                                │
│  (Any language: Python, Java, JavaScript, Go, C#)              │
│                                                                 │
│  Source Code:                                                   │
│    routes.py, models.py, services.py, ...                      │
│                                                                 │
│  Tests:                                                         │
│    tests/test_routes.py, test_models.py, ...                   │
│                                                                 │
│  Configuration:                                                 │
│    requirements.txt, config.yaml, .env, ...                    │
│                                                                 │
│  Output: Modified user project                                 │
│  (Visible deliverable to user/supervisor)                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 17.2 Two Types of Changes

**Type A: User-Project Changes (Visible Output)**
- Modify user code: routes.py, models.py, services.py
- Update tests in tests/
- What the user sees and benefits from
- Example: "Fix bug in routes.py" → user gets fixed code
- This is **coding assistant functionality**

**Type B: SPS Self-Changes (Research Subject)**
- Modify SPS-CA code: create new capabilities
- New capability: capabilities/generated/CAP-006/
- What you measure in the thesis
- Example: "After 3 repeated parsing failures, generate CAP-006 (Universal Parser)"
- This is **self-programming behavior**
- Evidence of self-programming: new Python modules in GitHub with tests

### 17.3 Evaluation Distinction

**Baselines A & B:** Only Type A changes (user project modifications)
- Can fix bugs, add features, generate tests
- No capability generation
- No self-modification

**SPS-CA:** Both Type A and Type B
- Fixes user bugs (Type A) → visible output
- Generates capabilities (Type B) → research evidence
- Learns from Type A failures to trigger Type B evolution

**Thesis claim success measured by:**
1. Type A performance: SPS-CA ≥ Baseline B (can fix user code equally or better)
2. Type B achievement: SPS-CA generates 3-6 capabilities with >80% test coverage
3. Type B quality: Generated capabilities are reusable (used >60% of time on new tasks)
4. Type B learning: Meta-learning shows >15% improvement in strategy selection

---

## PART VII: EXPERIMENTAL DESIGN

## 18. BASELINE AGENTS (A, B, SPS-CA)

### 18.1 Three-Baseline Comparison Strategy

| Aspect | Baseline A | Baseline B | SPS-CA |
|--------|-----------|-----------|---------|
| **Paradigm** | Naive LLM | Tool-Augmented LLM | Self-Programming Framework |
| **Layers** | None | No formal layers | All 10 layers |
| **Learning** | None | None | Yes (Layer 4) |
| **Adaptation** | None | None | Yes (Layer 5) |
| **Capability Reuse** | None (generates new each time) | Tool registry (fixed) | Capability registry (grows) |
| **Self-Modification** | None | None | Yes (Layer 8) |
| **Governance** | None | None | Yes (Layer 7) |
| **Experience Accumulation** | None | None | Yes (Layer 3) |

### 18.2 Same LLM Requirement

**Critical:** All 3 baselines use the SAME local LLM (Ollama, `qwen2.5-coder:7b` — see Section 9).

This ensures:
- Framework differences are measured, not LLM quality differences
- Reproducibility (all runs use same model)
- Zero cost (same free LLM)
- Fair comparison

### 18.3 Baseline A Implementation

**Purpose:** Naive baseline — send request + code to LLM, get back modified code.

```python
class BaselineA:
    def process_request(self, request: str, code: str) → str:
        prompt = f"""
        Request: {request}
        Code:
        {code}
        
        Generate modified code. Output only code.
        """
        response = llm.call(prompt)
        return response
```

**Metrics:**
- Success rate: % of tasks where generated code works
- Time: seconds to generate code
- Tests: % of tests passing after modification

### 18.4 Baseline B Implementation

**Purpose:** Better baseline — use tools (syntax check, test runner), but no learning or evolution.

```python
class BaselineB:
    def __init__(self):
        self.tools = {
            'analyze': self.analyze_code,
            'run_tests': self.run_tests,
            'check_syntax': self.check_syntax,
        }
    
    def process_request(self, request: str, code: str, project_path: str) → str:
        # Step 1: Analyze
        analysis = self.tools['analyze'](code)
        
        # Step 2: Generate with context
        prompt = f"""
        Request: {request}
        Analysis: {analysis}
        Code: {code}
        
        Generate modified code.
        """
        response = llm.call(prompt)
        
        # Step 3: Validate
        if not self.tools['check_syntax'](response):
            return None  # Failed validation
        
        # Step 4: Test
        test_result = self.tools['run_tests'](response, project_path)
        if test_result['passing'] < 0.8:  # <80% passing
            return None  # Retry or fail
        
        return response
```

**Metrics:**
- Same as Baseline A, plus:
- Tool usage count
- Retry count (if validation fails)
- Still no learning or capability generation

### 18.5 SPS-CA Implementation

**All 10 layers working together.**

---

## 19. 25 EXPERIMENTAL SCENARIOS (20 Mandatory + 5 Extended)

### 19.1 Scenario Organization

Scenarios are organized in 3 levels, testing progressive capabilities.

### LEVEL 1: BASIC CODING BEHAVIOR (4 Scenarios)

**S1: Simple Syntax Error Correction**
- Type: Change Type 1 (Syntax Fix)
- Task: Fix a syntax error in user code (mismatched parenthesis, indentation, typo)
- Target: Project A (Python) + Project B (Java) + Project C (TypeScript)
- Baseline: A, B, SPS-CA
- Success metric: Code passes tests after fix
- Example: `if x = 5:` → `if x == 5:` (Python)

**S2: Feature Addition**
- Type: Change Type 3 (Feature Addition)
- Task: Add a new endpoint or method to user project
- Target: Project A, B, C
- Success metric: New feature works, no regressions
- Example: Add `GET /users?filter=active` endpoint

**S3: Test Generation**
- Type: Change Type 5 (Test Generation)
- Task: Generate unit tests for an uncovered function
- Target: Project A, B, C
- Success metric: Generated tests pass, coverage increases >5%
- Example: Generate tests for `calculate_tax(amount)` function

**S4: Code Refactoring**
- Type: Change Type 4 (Refactoring)
- Task: Refactor code for readability/maintainability
- Target: Project A, B, C
- Success metric: Code structure improves, tests still pass
- Example: Extract method from long function, improve variable names

### LEVEL 2: SPS BEHAVIOR (11 Scenarios)

**S5: Single Failure Detection**
- Type: Change Type 7 (Evolution) - First occurrence
- Task: Detect a failure pattern (e.g., parsing fails once)
- Experience: Log failure, identify pattern
- Success metric: Failure is categorized correctly
- Example: "Parse error" failure on JSON parsing task

**S6: Repeated Failure Pattern (3 Occurrences)**
- Type: Change Type 7 (Evolution) - Trigger threshold
- Task: Same failure pattern occurs 3 times
- Evolution trigger: Meets min_occurrences threshold
- Success metric: System recognizes need for evolution
- Example: Parse errors in tasks 10, 15, 20

**S7: Capability Adaptation (Parameter Adjustment)**
- Type: Change Type 6 (Adaptation)
- Task: Reuse existing capability with adjusted parameters
- Context: Same task type but different language/size
- Success metric: Adapted capability works better than base
- Example: Use CAP-003 with timeout 5s → 15s for Java compilation

**S8: Capability Composition**
- Type: Change Types 6+7 combined
- Task: Combine 2+ capabilities to solve complex problem
- Example: Use CAP-002 (syntax fix) + CAP-003 (test generation) together
- Success metric: Complex task solved using multiple capabilities
- Complexity level: Medium

**S9: Cross-Project Capability Reuse**
- Type: Change Type 6 (Adaptation across projects)
- Task: Reuse capability from Project A on Project B (different language)
- Success metric: Capability works on Java despite being developed for Python
- Example: CAP-001 (bug detection) used on Project B successfully
- Metric: >60% cross-language success target

**S10: Meta-Learning Strategy Switch**
- Type: Change Type 6 (Adaptation with learned strategy)
- Task: System switches capability selection based on past failures
- Example: "CAP-002 has 20% failure rate on TypeScript, try CAP-003 instead"
- Success metric: Strategy switch improves success rate >10%
- Meta-Learning trigger: Layer 4 recommends different approach

**S11: Single Capability Generation (Simple)**
- Type: Change Type 7 (Evolution)
- Task: Generate first capability (CAP-009) from repeated failures
- Trigger: 3+ occurrences of same failure pattern
- Success metric: CAP-009 is created, has >80% test coverage
- Example: Generate "Universal Parser" capability after 3 parse failures

**S12: Capability Reuse (Generated)**
- Type: Change Type 6 (Adaptation)
- Task: Reuse newly generated capability (CAP-009) on new tasks
- Context: Different projects/domains
- Success metric: Generated capability is applicable and improves success
- Example: CAP-009 (Universal Parser) used on CSV parsing task (different from JSON origin)

**S13: Multiple Capability Generation**
- Type: Change Type 7 (Evolution - multiple)
- Task: Generate CAP-010, CAP-011 from other failure patterns
- Trigger: Different failure patterns reach min_occurrences
- Success metric: 3+ capabilities generated with >80% coverage each
- Example: CAP-010 (Type Validator), CAP-011 (Error Handler)

**S14: Meta-Learning Improvement Measurement**
- Type: Meta-Learning
- Task: Measure improvement in strategy selection over time
- Baseline: Phase 1-3 success rate (~50%)
- Target: Phase 10 success rate (>65%, i.e., >15% improvement)
- Success metric: Quantified improvement with clear before/after comparison
- Evidence: experience/logs/improvement_metrics.json

**S15: Experience Log Continuity**
- Type: Experience Accumulation
- Task: Verify experience persists across sessions
- Test: Load experience_log.json from Phase 6, continue making decisions
- Success metric: Decisions reflect history (e.g., avoid failed strategies)
- Example: "Task 100 avoided CAP-002 because it failed 5 times in past"

### LEVEL 3: GOVERNANCE & EVOLUTION SAFETY (10 Scenarios)

**S16: DNA Violation Rejection**
- Type: Change Type 7 (Governance rejection)
- Task: Propose a change that violates DNA rules
- Example: Try to modify core/layer_7_governance.py (denied)
- Success metric: Change is rejected with clear reasoning
- Evidence: governance/decisions/decision_*.json shows rejection

**S17: Risk Assessment - Low Risk Auto-Approval**
- Type: Governance (auto-approve)
- Task: Low-risk change (e.g., add comment, simple refactor)
- Success metric: Auto-approved without human intervention
- Logged in: governance/decisions/

**S18: Risk Assessment - High Risk Escalation**
- Type: Governance (human escalation)
- Task: High-risk change (e.g., modify capability interface, core logic)
- Success metric: Escalated to supervisor with clear reasoning
- Status: "pending_human_approval"
- Supervisor: Reviews and approves/rejects

**S19: Sandbox Validation - Success Path**
- Type: Change Type 6/7 (Validation)
- Task: Change is validated in sandbox, all tests pass
- Success metric: Sandbox result: PASS
- Metrics logged: before/after comparison
- Regression: None detected

**S20: Sandbox Validation - Failure Path**
- Type: Change Type 6/7 (Validation rejection)
- Task: Change is validated in sandbox, some tests fail
- Success metric: Sandbox result: FAIL, rollback triggered
- Change: Rejected, not applied to user project
- Evidence: evaluation/sandbox/sandbox_*.json shows failure

**S21: Rollback Execution**
- Type: Change Type 7 (Rollback)
- Task: Regression detected after change applied, rollback needed
- Trigger: Post-deployment test failure
- Success metric: Rollback succeeds, files restored to pre-change state
- Rollback success rate: >95% target
- Evidence: evaluation/rollback/rollback_*.json

**S22: Governance Audit Trail**
- Type: Governance (audit)
- Task: Verify complete audit trail of all decisions
- Success metric: Every decision is logged with timestamp, rationale, outcome
- Supervisor reviewable: governance/decisions/ directory
- Completeness: >95% of decisions logged

**S23: Capability Retirement (Extended)**
- Type: Change Type 7 (Lifecycle)
- Task: Mark capability as deprecated/retired after better version created
- Example: CAP-001-v1.0 → CAP-001-v2.0 (improved)
- Success metric: Retirement is tracked in metadata
- Future use: New tasks prefer CAP-001-v2.0

**S24: Evolution Lineage Tracking (Extended)**
- Type: Evolution (traceability)
- Task: Track complete lineage of capability evolution
- Example: CAP-001 → CAP-009 (improved after failures)
- Success metric: Lineage diagram shows parent-child relationships
- Evidence: evaluation/lineage/

**S25: Recovery from Failed Evolution (Extended)**
- Type: Evolution (error handling)
- Task: Generated capability has bugs, needs recovery
- Example: CAP-010 generated but tests fail >20%
- Success metric: System detects bad capability, reverts, retries differently
- Evidence: governance/decisions/ shows rejection and new approach

---

## 20. PROJECT EXECUTION MATRIX & SCENARIO DISTRIBUTION

### 20.1 Execution Matrix

Not all scenarios run on all projects. Here's the distribution:

| Scenario | Name | Project A (Py) | Project B (Java) | Project C (TS) | Baselines | Total Execs |
|----------|------|---|---|---|---|---|
| S1 | Syntax Error Fix | A,B,SPS | A,B,SPS | A,B,SPS | 3 | 9 |
| S2 | Feature Addition | A,B,SPS | A,B,SPS | A,B,SPS | 3 | 9 |
| S3 | Test Generation | A,B,SPS | A,B,SPS | A,B,SPS | 3 | 9 |
| S4 | Refactoring | A,B,SPS | A,B,SPS | A,B,SPS | 3 | 9 |
| S5 | Single Failure | A,B,SPS | — | — | varies | 3-6 |
| S6 | Repeated Failure | A,B,SPS | A,B,SPS | A,B,SPS | 3 | 9 |
| S7 | Adaptation | A,B,SPS | A,B,SPS | A,B,SPS | 3 | 9 |
| S8 | Composition | A,B,SPS | — | — | 3 | 3-6 |
| S9 | Cross-Project Reuse | A→B, B→C | B→C | — | SPS only | 2-3 |
| S10 | Meta-Learning Switch | A,B,SPS | — | — | varies | 3-6 |
| S11 | Gen Capability | A,B,SPS | — | — | SPS only | 3+ |
| S12 | Reuse Generated | A,B,SPS | A,B,SPS | — | SPS only | 6+ |
| S13 | Multi-Gen | A,B,SPS | — | — | SPS only | 3+ |
| S14 | Meta-Learning Measure | A,B,SPS | A,B,SPS | A,B,SPS | 3 | 9 |
| S15 | Experience Continuity | A,B,SPS | — | — | SPS only | 3 |
| S16 | DNA Violation | A,B,SPS | — | — | SPS only | 3 |
| S17 | Low Risk Auto-Approve | A,B,SPS | A,B,SPS | — | SPS only | 3-6 |
| S18 | High Risk Escalate | A,B,SPS | — | — | SPS only | 3 |
| S19 | Sandbox Pass | A,B,SPS | A,B,SPS | A,B,SPS | 3 | 9 |
| S20 | Sandbox Fail | A,B,SPS | A,B,SPS | — | 3 | 6 |
| S21 | Rollback | A,B,SPS | A,B,SPS | — | SPS only | 6 |
| S22 | Audit Trail | A,B,SPS | — | — | SPS only | 3 |
| S23 | Retirement | A,B,SPS | — | — | SPS only | 3 |
| S24 | Lineage | A,B,SPS | — | — | SPS only | 3 |
| S25 | Recovery | A,B,SPS | — | — | SPS only | 3 |
| | | | | | **TOTAL** | ~85-100 |

**Summary:**
- Basic coding (S1-S4): ~36 executions (full matrix)
- SPS-specific (S5-S15): ~35-40 executions (mixed)
- Governance (S16-S22): ~30-35 executions (mixed)
- Extended (S23-S25): ~9 executions (SPS-CA only, optional)

---

## PART VIII: EVALUATION & EVIDENCE

## 21. METRICS & MEASUREMENT FRAMEWORK

### 21.1 Success Metrics (Quantitative)

| Metric | Target | How Measured | Baseline Comparison |
|--------|--------|--------------|-------------------|
| **Task Success Rate** | >65% | % of scenarios completed successfully | A: 40%, B: 55%, SPS: >65% |
| **Meta-Learning Improvement** | >15% | (Final success rate - Initial) / Initial | SPS only |
| **Cross-Language Reuse** | >60% | % of generated capabilities work on new languages | SPS only |
| **Regression Rate** | <2% | % of successful changes that cause test failures | A: 8%, B: 4%, SPS: <2% |
| **Test Coverage (Generated Code)** | >80% | % of generated code covered by tests | SPS only |
| **Rollback Success** | >95% | % of rollbacks that correctly restore state | SPS only |
| **Average Execution Time** | <60s | Time to complete one scenario | Baseline comparison |
| **Governance Decision Accuracy** | 100% | % of DNA violations correctly rejected | SPS only |

### 21.2 Qualitative Metrics (Evidence-Based)

| Metric | Evidence | Collection Method |
|--------|----------|-------------------|
| **Framework Correctness** | All 10 layers implemented and integrated | Code review + integration tests |
| **Capability Generalization** | Generated capabilities are reusable | Cross-project execution matrix |
| **Learning Evidence** | System improves strategy selection | Meta-learning improvement measurement |
| **Self-Programming Demonstration** | Capabilities created, tested, registered | GitHub commits + capability registry |
| **Safety Enforcement** | DNA violations rejected, governance working | Audit trail review |
| **Traceability** | Complete decision history logged | governance/decisions/ directory |

---

## 22. EVALUATION PROTOCOL

### 22.1 Phase 10 Execution

1. **Scenario Execution** (Weeks 21-22)
   - Execute all 25 scenarios against 3 baselines on 3 projects
   - Collect metrics for each execution
   - Log results in evaluation/scenarios/

2. **Baseline Comparison** (Week 23)
   - Calculate success rates, improvement metrics
   - Compare A vs B vs SPS-CA
   - Verify SPS-CA > B by >15 percentage points

3. **Artifact Collection** (Week 24)
   - Collect 15 thesis artifacts (Appendix E, Form 5)
   - Verify completeness and quality
   - Supervisor sign-off

### 22.2 Completion Criteria

- [ ] All 25 scenarios executed
- [ ] Metrics collected for ~85-100 total executions
- [ ] Baseline comparison shows SPS-CA outperformance
- [ ] 15 artifacts collected and verified
- [ ] Evaluation forms completed
- [ ] Supervisor approval

---

## 23. EXPECTED THESIS ARTIFACTS (15 Required)

1. **Initial Capability Registry State** — capabilities/registry.json at Phase 6 start
2. **Repeated Failure Detection Log** — experience/logs/failure_patterns.json showing patterns
3. **Evolution Trigger Decision** — governance/decisions/ showing why CAP-009 was generated
4. **Generated Capability Code** — capabilities/generated/CAP-009/ (capability.py + tests.py)
5. **Governance Decision Audit** — governance/decisions/ directory with >20 logged decisions
6. **Sandbox Execution Trace** — evaluation/sandbox/ showing before/after metrics
7. **Regression Test Results** — evaluation/regression/ showing detected/prevented regressions
8. **Capability Registration Event** — registry update log showing CAP-009 added
9. **Cross-Language Capability Reuse** — evaluation/cross_language/ showing S9 results
10. **Rollback Execution Trace** — evaluation/rollback/ showing rollback success/failure
11. **Failure Taxonomy Classification** — evaluation/failure_taxonomy.json mapping failures to patterns
12. **Evolution Lineage Diagram** — evaluation/lineage/ showing CAP relationships
13. **Metrics Over Full Execution Matrix** — evaluation/metrics/aggregate_*.json (all scenarios)
14. **Baseline vs SPS-CA Comparison** — evaluation/comparison/ showing A, B, SPS-CA side-by-side
15. **Complete Git History** — sps-ca repo git log showing all phases, phases 0-10 tagged

---

## 24. THREATS TO VALIDITY

### Construct Validity
- **Threat:** Success rate metric doesn't capture quality of generated code
- **Mitigation:** Also measure test coverage (>80% target), regression rate (<2% target)

### Internal Validity
- **Threat:** LLM stochasticity affects results
- **Mitigation:** Run each scenario 3+ times, report variance
- **Mitigation:** Use same random seed/temperature settings across runs

### External Validity
- **Threat:** Results only applicable to small, controlled projects
- **Mitigation:** Acknowledge scope limitation in thesis
- **Mitigation:** Discuss extensibility to larger projects

### Statistical Validity
- **Threat:** Sample size too small (~85-100 executions)
- **Mitigation:** Detailed tracking of each execution, not just aggregates
- **Mitigation:** Qualitative evidence (audit trail) complements quantitative

---

## 25. RISK MITIGATION STRATEGIES

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|-----------|
| **LLM inference too slow** | Medium | High | Run overnight, use smaller model if needed |
| **Phase overruns** | High | Medium | Buffer weeks built in, can reduce optional scenarios |
| **Baseline B harder than expected** | Medium | Medium | Simplify Baseline B requirements, focus on A vs SPS-CA |
| **Capability generation produces bugs** | Medium | Medium | Comprehensive testing (>80% coverage), sandbox validation |
| **Cross-language parsing fails** | Low | High | Tree-sitter has wide language support, fallback to Python-only if needed |
| **Governance rules too restrictive** | Low | Medium | Adjust DNA rules iteratively in Phase 3 |
| **Evaluation metric collection fails** | Low | High | Automated logging, manual spot-checks |

---

## Appendix A: Zero-Cost Technology Stack

All tools are free, open-source, locally-run.

| Component | Tool | Cost | Details |
|-----------|------|------|---------|
| **LLM** | Ollama + `qwen2.5-coder:7b` | $0 | Local inference, no API key needed; chosen to fit 16GB RAM / Intel HD 620 / i7 7th Gen dev hardware (`Qwen3-Coder` noted as future upgrade path in `REQUIREMENTS.md`) |
| **Code Parsing** | tree-sitter | $0 | Open-source, language-agnostic parser |
| **Testing** | pytest | $0 | Python standard test framework, run via `layers/*/tests` (layer-local) and `testing/` (cross-layer) |
| **Database** | SQLite | $0 | File-based, no server needed |
| **Version Control** | Git + GitHub Free | $0 | GitHub free tier unlimited public/private repos — repo: `muhammadnaumantahir/SPS_CA` |
| **Containerization** | Docker Desktop Free | $0 | Desktop version free for development |
| **Compute** | Local developer machine | $0 | No cloud hosting |
| **Total** | — | **$0** | All components free to run |

**Companion docs in the repo (added in Phase 0, not originally planned as separate files):** `REQUIREMENTS.md` (authoritative hardware/software/model/runtime requirements), `SETUP.md` (installation & verification procedure), `SETUP_AND_PUSH.sh` (bootstrap/push helper).

**Trade-offs:**
- ✓ No monetary cost
- ✗ Slower inference (local vs cloud API)
- ✗ Requires powerful local machine (for running Ollama + Docker)
- ✓ Fully reproducible (anyone can clone and run)
- ✓ No API rate limits or dependencies on external services

---

## Appendix C: File Manifest (As-Built, Post-Phase 0)

Top-level repository entries, `muhammadnaumantahir/SPS_CA` @ v0.3.0:

| Path | Purpose | Planned in v4.0? |
|------|---------|-------------------|
| `README.md` | Project overview, architecture summary, setup quick-start | Yes |
| `REQUIREMENTS.md` | Hardware/software/model/runtime/research requirements (authoritative) | **New in Phase 0** |
| `SETUP.md` | Full installation & verification procedure | **New in Phase 0** |
| `SETUP_AND_PUSH.sh` | Setup/bootstrap + git push helper script | **New in Phase 0** |
| `requirements.txt`, `setup.py`, `.gitignore`, `Dockerfile` | Standard Python project scaffolding | Yes |
| `core/` | Orchestration, shared state, event contracts across layers | Redefined (was flat layer files in v4.0) |
| `layers/layer_01_software_dna/` … `layer_10_execution/` | One package per SPS layer, own implementation + tests | Redefined (was `core/layer_N_*.py`) |
| `models/` | Provider-neutral model/LLM abstraction (Ollama today) | **New in Phase 0** |
| `coding/` | Repository intelligence, AST/context analysis, controlled code modification, local Git ops | **New in Phase 0** |
| `capabilities/` | Capability lifecycle, lineage, seed + generated capabilities, registry | Yes |
| `execution/`, `governance/`, `validation/` | Standalone infrastructure supporting the same-named SPS layers | Redefined/expanded |
| `memory/`, `data/` | Runtime conversations/experiences/traces/sessions/exports (not committed as source) | **New in Phase 0** |
| `projects/` | User target projects, isolated from SPS source | Yes |
| `experience/logs/` | Task logs and metrics | Yes |
| `ui/` | UI and visualization | Yes |
| `testing/` | Cross-layer, integration, system, scenario, baseline/benchmark tests | Renamed from `tests/` |
| `evaluation/` | Evaluation results and checklists | Yes |
| `analytics/` | Capability growth/genealogy datasets, metrics, evolution history | **New in Phase 0** |
| `docs/architecture/SPS_CA_ARCHITECTURE_V2.md` | Authoritative architecture contract | **New in Phase 0** |

---

## Appendix D: Success Metrics Summary

See Section 21 (Metrics & Measurement Framework) for the full quantitative and qualitative metric definitions, and Section 15 for phase-by-phase completion status (Phase 0: ✅ complete; Phases 1-10: not started).

---

## Appendix E: Evaluation Forms & Checklists

(Same as v3.0 — all 5 forms provided above in Section 1.4)

---

## CONCLUSION

This v4.1 master document specifies everything needed to build, test, and evaluate SPS-CA at **zero monetary cost**, with expanded experimental scenarios, clarified architecture, and now a Phase-0-verified implementation structure.

**Key points:**

1. **It is an instruction manual** — give phases 0-10 to AI agents, in order (Phase 0 is done; Phases 1-10 use `layers/layer_0N_name/` paths, not the original flat `core/layer_N_*.py` paths)
2. **It is reproducible** — anyone can follow phases and get similar results; `REQUIREMENTS.md` and `SETUP.md` now pin the exact hardware/model used
3. **It clarifies architecture** — Python core + any-language user projects, with `layers/`, `models/`, `coding/`, `execution/`, `governance/`, `validation/`, `memory/`, `data/`, and `analytics/` as first-class packages
4. **It expands evaluation** — 25 scenarios (20 mandatory + 5 extended) instead of 13
5. **It emphasizes self-programming** — Type B changes (capability generation) are the research subject
6. **It is complete** — addresses all 10 layers, learning, safety, governance
7. **It is evidence-based** — collect 15 artifacts supporting thesis claims
8. **It is positioned against the market** — Section 4 compares SPS-CA to Copilot, Cursor, Claude Code, Codex, Devin, Windsurf, Aider, and Codebuff on the governance/experience/evolution dimensions that matter to the thesis claim, not raw coding benchmarks

**Timeline:**
- Phases 0-10: ~18-20 weeks (development)
- Phase 10 execution: ~4-6 weeks (scenarios + metrics)
- Buffer: ~4-6 weeks
- Writing: 8-10 weeks (thesis)
- **Total: 32-36 weeks development+evaluation, ~40-46 weeks including writing (fits within 1-year MS timeline)**

**Start immediately upon approval.**  
**Expected completion: well within 12 months.**  
**Deliverables: Complete SPS-CA system + thesis, at $0 development cost.**

---

**Prepared by:** Muhammad Nauman Tahir  
**Approved by:** [Supervisor signature]  
**Date:** August 31, 2026  
**Version:** 4.1 (Phase 0 Implemented — Structure Realigned to Actual Codebase, Competitive Analysis Added)

---

**END OF MASTER DOCUMENT v4.1**

*For questions, refer to individual phase specifications (Section 14) or contact thesis supervisor.*
