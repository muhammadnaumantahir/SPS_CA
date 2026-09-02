# SPS-CA: Self-Programming Code Assistant
## System Documentation
### Governed, Traceable, Reversible Self-Programming — Zero-Cost, Functional-Equivalence Edition

**Student:** Muhammad Nauman Tahir (MS240400054)
**Institution:** Virtual University of Pakistan
**Supervisor:** Dr. Muhammad Salman Bashir
**Budget:** $0 — see Section 9 (Zero-Cost LLM & Compute Architecture) and Appendix A
**Repository:** [github.com/muhammadnaumantahir/SPS_CA](https://github.com/muhammadnaumantahir/SPS_CA)

This document is the complete reference for SPS-CA: what it proves, how it is architected, how it is used, and how it is evaluated. Companion documents: `README.md` (quick overview), `docs/ARCHITECTURE.md` (layer/module reference), `SETUP.md` (installation), `REQUIREMENTS.md` (system requirements).

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

### PART V: USER INTERACTION & WORKFLOW
14. User Interface & Interaction Model (Prompt-Based)
15. User Project vs SPS Self-Change Architecture

### PART VI: EXPERIMENTAL DESIGN
16. Baseline Agents (A, B, SPS-CA)
17. **25 Experimental Scenarios (20 Mandatory + 5 Extended)**
18. Project Execution Matrix & Scenario Distribution

### PART VII: EVALUATION & EVIDENCE
19. Metrics & Measurement Framework
20. Evaluation Protocol
21. Expected Thesis Artifacts
22. Threats to Validity
23. Risk Mitigation Strategies

### PART VIII: APPENDICES
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

SPS-CA (Self-Programming Code Assistant) is a complete, working research prototype demonstrating a reference framework for Self-Programming Software (SPS). This document is the system's full technical and research documentation: what it does, how it is architected, how it is used, and how it is evaluated.

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
| **Total Codebase Scope** | ~5,500-7,500 lines (SPS core + tests) |
| **Development Budget** | **$0** — local open-weight LLM (Ollama), SQLite, tree-sitter, Docker, GitHub free tier |

### 1.5 How to Read This Document

**For Project Managers/Supervisors (skip to here if time-constrained):**
- Read: Executive Summary, Vision (Section 2), Key Facts (Section 1.4), Project Portfolio (Section 10), Baselines (Section 16)
- Time: 2-3 hours
- Output: Understand scope and deliverables

**For Engineers extending the system:**
- Read: Part II (Architecture & Design), `docs/ARCHITECTURE.md`, and the relevant `layers/layer_0N_*/` package for the module you're touching
- Output: Enough context to add capabilities, adjust governance rules, or extend target-project coverage

**For Researchers (thesis development):**
- Read: Entire document, focusing on Part IV (self-programming mechanism), Part VI (experimental design), Part VII (evaluation)
- Time: 4-6 hours initial read, then iterative reference
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

Every SPS reference-framework construct (Software DNA, Cognitive Core, Experience, Meta-Learning, Adaptation, Validation, Governance, Evolution, Capability Registry, Execution) maps 1:1 to a first-class package under `layers/` in the implemented codebase (see Section 6 and Section 7 for the mapping).

---

## 4. COMPETITIVE ANALYSIS & DIFFERENTIATION

### 4.1 Why Compare SPS-CA to Existing AI Coding Tools

SPS-CA is not claiming to out-code existing AI coding assistants on raw code generation. The thesis claim (Section 1.2) is narrower and different in kind: that a **governed, traceable, reversible self-programming framework** can sit underneath a coding agent and make it measurably better at *repeat* tasks over time — through persistent experience, meta-learning, and capability evolution that is approved, tested, versioned, and auditable. Section 4.2 positions SPS-CA against today's mainstream AI coding tools on exactly the dimensions that distinguish this claim, not on benchmark coding accuracy (which SPS-CA, as a $0 local-LLM research prototype, is not attempting to win).

### 4.2 Comparison Table: SPS-CA vs. Mainstream AI Coding Tools/Models

| Dimension | **SPS-CA** (this thesis) | GitHub Copilot | Cursor | Claude Code | OpenAI Codex (CLI/Cloud) | Devin (Cognition) | Windsurf (Codeium) | Aider | Codebuff |
|---|---|---|---|---|---|---|---|---|---|
| **Primary mode** | Governed self-programming research prototype | In-IDE autocomplete + chat | AI-native IDE (fork of VS Code) | Terminal/CLI agentic coding assistant | Cloud/CLI autonomous coding agent | Autonomous "AI software engineer" | AI-native IDE | Terminal pair-programming agent | CLI/terminal coding agent |
| **Persistent cross-session experience log** | ✅ Layer 3 (Experience) — structured, queryable | ❌ (session-scoped context only) | ⚠️ Project-level context/rules, not structured experience | ⚠️ Session memory + `CLAUDE.md`, not a formal experience layer | ❌ | ⚠️ Task history within its own workspace | ⚠️ Project memory (Cascade), not structured | ❌ (repo map + chat history only) | ❌ |
| **Meta-learning (strategy selection improves over time)** | ✅ Layer 4, explicitly measured (Section 19) | ❌ | ❌ | ❌ | ❌ | ⚠️ Implicit, not exposed/measurable | ❌ | ❌ | ❌ |
| **Self-generated, versioned, reusable capabilities** | ✅ Layer 8/9 — new capability = executable module + tests + metadata, registered for reuse | ❌ | ❌ | ⚠️ Can write reusable scripts/skills if instructed, no formal registry/versioning | ❌ | ⚠️ Can save reusable playbooks internally, not user-auditable | ❌ | ❌ | ❌ |
| **Formal governance layer (DNA rules, approve/reject with rationale)** | ✅ Layer 1 + Layer 7 — hard/soft constraints, logged decisions | ❌ | ❌ | ⚠️ Permission prompts for tool use, not a policy/DNA engine | ⚠️ Sandboxed approval-mode execution | ⚠️ Guardrails, not a documented rule engine | ❌ | ❌ | ❌ |
| **Auditable decision trail (why a change was made/rejected)** | ✅ `governance/decisions/` — full JSON audit trail | ❌ | ❌ | ⚠️ Conversation log only | ⚠️ Execution log only | ⚠️ Task log, limited transparency | ⚠️ Conversation log only | ⚠️ Git commit messages only | ⚠️ Conversation log only |
| **Sandbox validation + rollback before self-modification lands** | ✅ Layer 6 + Execution layer — sandboxed test, rollback on regression | ❌ (no self-modification) | ❌ (no self-modification) | ⚠️ Runs tests if asked; no formal rollback protocol | ⚠️ Sandboxed cloud execution | ⚠️ Runs in isolated VM | ❌ | ⚠️ Relies on Git for rollback | ⚠️ Relies on Git for rollback |
| **Capability lineage/genealogy (provenance of what was learned)** | ✅ Layer 9 — parent capability, triggering task, model, validation evidence, version history | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Cross-project, cross-language capability reuse (measured)** | ✅ Explicit evaluation metric (Section 19, S9 scenario) | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **Target-language scope** | Any (Python core, tree-sitter-parsed targets: Python, Java, JS/TS, Go, C#) | Any (IDE-integrated) | Any | Any | Any | Any | Any | Any | Any |
| **Model dependency** | Provider-neutral (`models/`); local Ollama (`qwen2.5-coder:7b`) today, cloud adapters possible later | OpenAI/proprietary (fixed) | User-selectable (Claude, GPT, etc.) | Claude models (fixed) | OpenAI models (fixed) | Proprietary (fixed) | User-selectable | User-selectable (BYO API key) | User-selectable |
| **Deployment** | Local, fully offline-capable | Cloud SaaS | Cloud SaaS (local IDE shell) | Cloud API (local CLI shell) | Cloud SaaS/CLI | Cloud SaaS | Cloud SaaS (local IDE shell) | Local CLI + cloud API | Local CLI + cloud API |
| **Cost** | **$0** (local LLM, open-source stack) | Paid subscription | Paid subscription | Pay-per-use API | Pay-per-use API / subscription | Paid, usage-metered | Paid subscription (free tier limited) | Pay-per-use API (tool is free) | Pay-per-use API (tool is free) |
| **Reproducibility for research** | ✅ Designed for it — fixed seeds, same-LLM baselines, full Git history, open-source | ❌ Closed model/infra | ❌ Closed infra | ⚠️ Partially (API-based, closed model) | ❌ Closed model/infra | ❌ Closed model/infra | ❌ Closed infra | ✅ Open-source tool (model still closed unless local) | ✅ Open-source tool (model still closed unless local) |
| **Maturity / production readiness** | Research prototype, functionally complete | Production, widely deployed | Production, widely deployed | Production, widely deployed | Production, widely deployed | Production (limited access) | Production, widely deployed | Production, widely deployed | Production, widely deployed |

*Legend: ✅ = explicit, first-class, measured feature; ⚠️ = partial/implicit/undocumented equivalent; ❌ = not offered; N/A = not applicable to that tool's design.*

### 4.3 Key Differentiation Summary

1. **SPS-CA is not competing on raw coding ability.** Copilot, Cursor, Claude Code, Codex, Devin, Windsurf, Aider, and Codebuff are all far more capable at general-purpose code generation today — they run frontier cloud models, have large engineering teams, and are production-hardened. SPS-CA runs a small local 7B model.
2. **SPS-CA's contribution is the governed self-programming layer underneath the agent loop**: a persistent, structured experience log; meta-learning over strategies; capability evolution that must pass governance and sandboxed validation before it is registered and reused; and full lineage/audit trail. None of the compared tools expose this as a first-class, measurable subsystem — several (Claude Code, Devin, Windsurf) have informal analogues (memory files, internal playbooks, guardrails) but none formalize it as versioned, tested, provenance-tracked capabilities with a governance approve/reject decision log.
3. **The fair comparison is architectural, not benchmark-based.** The evaluation design (Part VI/VII) therefore does not attempt to beat Copilot/Cursor/Claude Code/Codex on HumanEval-style benchmarks. It instead compares SPS-CA against two *same-LLM* internal baselines (Baseline A: naive LLM, Baseline B: tool-augmented agent without the SPS layers — Section 16) to isolate the effect of the SPS framework itself, while this table supplies the external market context for why that framework is worth building.
4. **Cost and reproducibility are genuine differentiators for a thesis context**, not just budget constraints: a $0, fully local, open-source stack means every experimental run is reproducible by an examiner or future researcher without API keys, rate limits, or vendor dependency — which the cloud-hosted competitors cannot offer.

---

## 5. RESEARCH BOUNDARIES & CONSTRAINTS

SPS-CA is a research prototype, not a production system; evaluation is limited to 3 controlled projects and 25 scenarios; the local 7B model trades inference speed and raw capability for zero cost and full reproducibility (Section 9); results generalize to the tested scope only (see Section 22, Threats to Validity).

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

> **Implementation note:** each of the 10 layers is its own package under `layers/` (`layer_01_software_dna/`, `layer_02_cognitive_core/`, … `layer_10_execution/`), owning its implementation and layer-local tests. `core/` holds **only** cross-layer orchestration, shared state, and event contracts, so layers are not tightly coupled by calling each other's internals directly. See Section 7 for the per-layer mapping and `docs/ARCHITECTURE.md` for the full directory tree.

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
- Model used: **`qwen2.5-coder:7b`** (pinned in `REQUIREMENTS.md`), sized to run on the target development machine (16GB RAM, no dedicated GPU)
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
- **Metric:** "Cross-language capability reuse >60%" (Section 19)

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

## PART V: USER INTERACTION & WORKFLOW

## 14. USER INTERFACE & INTERACTION MODEL (Prompt-Based)

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

## 15. USER PROJECT vs SPS SELF-CHANGE ARCHITECTURE

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

## PART VI: EXPERIMENTAL DESIGN

## 16. BASELINE AGENTS (A, B, SPS-CA)

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

## 17. 25 EXPERIMENTAL SCENARIOS (20 Mandatory + 5 Extended)

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
- Baseline: Early-session success rate (~50%)
- Target: Late-session success rate (>65%, i.e., >15% improvement)
- Success metric: Quantified improvement with clear before/after comparison
- Evidence: experience/logs/improvement_metrics.json

**S15: Experience Log Continuity**
- Type: Experience Accumulation
- Task: Verify experience persists across sessions
- Test: Load an existing experience_log.json, continue making decisions
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

## 18. PROJECT EXECUTION MATRIX & SCENARIO DISTRIBUTION

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

## PART VII: EVALUATION & EVIDENCE

## 19. METRICS & MEASUREMENT FRAMEWORK

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

## 20. EVALUATION PROTOCOL

### 20.1 Evaluation Execution

1. **Scenario Execution**
   - Execute all 25 scenarios against 3 baselines on 3 projects
   - Collect metrics for each execution
   - Log results in evaluation/scenarios/

2. **Baseline Comparison**
   - Calculate success rates, improvement metrics
   - Compare A vs B vs SPS-CA
   - Verify SPS-CA > B by >15 percentage points

3. **Artifact Collection**
   - Collect 15 thesis artifacts (Appendix E, Form 5)
   - Verify completeness and quality
   - Supervisor sign-off

### 20.2 Completion Criteria

- [ ] All 25 scenarios executed
- [ ] Metrics collected for ~85-100 total executions
- [ ] Baseline comparison shows SPS-CA outperformance
- [ ] 15 artifacts collected and verified
- [ ] Evaluation forms completed
- [ ] Supervisor approval

---

## 21. EXPECTED THESIS ARTIFACTS (15 Required)

1. **Initial Capability Registry State** — capabilities/registry.json baseline snapshot
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
15. **Complete Git History** — repository commit log showing full development and evaluation trail

---

## 22. THREATS TO VALIDITY

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

## 23. RISK MITIGATION STRATEGIES

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|-----------|
| **LLM inference too slow** | Medium | High | Run overnight, use smaller model if needed |
| **Schedule overruns** | High | Medium | Buffer time built in, can reduce optional scenarios |
| **Baseline B harder than expected** | Medium | Medium | Simplify Baseline B requirements, focus on A vs SPS-CA |
| **Capability generation produces bugs** | Medium | Medium | Comprehensive testing (>80% coverage), sandbox validation |
| **Cross-language parsing fails** | Low | High | Tree-sitter has wide language support, fallback to Python-only if needed |
| **Governance rules too restrictive** | Low | Medium | Adjust DNA rules iteratively based on observed rejections |
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

**Companion docs in the repo:** `REQUIREMENTS.md` (authoritative hardware/software/model/runtime requirements), `SETUP.md` (installation & verification procedure), `docs/ARCHITECTURE.md` (layer/module reference).

**Trade-offs:**
- ✓ No monetary cost
- ✗ Slower inference (local vs cloud API)
- ✗ Requires powerful local machine (for running Ollama + Docker)
- ✓ Fully reproducible (anyone can clone and run)
- ✓ No API rate limits or dependencies on external services

---

## Appendix C: File Manifest

Top-level repository entries, `muhammadnaumantahir/SPS_CA`:

| Path | Purpose |
|------|---------|
| `README.md` | Project overview, architecture summary, setup quick-start |
| `REQUIREMENTS.md` | Hardware/software/model/runtime/research requirements (authoritative) |
| `SETUP.md` | Full installation & verification procedure |
| `requirements.txt`, `setup.py`, `pytest.ini`, `.gitignore`, `Dockerfile` | Standard Python project scaffolding |
| `core/` | Orchestration, shared state, event contracts across layers |
| `layers/layer_01_software_dna/` … `layer_10_execution/` | One package per SPS layer, own implementation + tests — all 10 layers implemented |
| `models/` (`base/`, `ollama/`, `openai/`, `anthropic/`, `qwen/`, `registry/`) | Provider-neutral model/LLM abstraction, `qwen2.5-coder:7b` default |
| `coding/` | Repository intelligence, AST/context analysis, controlled code modification, local Git ops |
| `capabilities/` (`seeds/`, `generated/`, `lineage/`, `registry.json`, `seed_registry.py`) | Capability lifecycle, lineage, CAP-001–CAP-008 seed capabilities plus generated capabilities |
| `execution/`, `governance/` (`dna_rules.json`, `decisions/`), `validation/` | Standalone infrastructure supporting the same-named SPS layers |
| `memory/`, `data/` | Runtime conversations/experiences/traces/sessions/exports (not committed as source, `.gitkeep` only) |
| `projects/project_a_python/`, `project_b_java/`, `project_c_typescript/` | Three equivalent benchmark target projects (FastAPI / Spring Boot / Express) with matched seeded defects |
| `baselines/` (`baseline_a_naive_llm.py`, `baseline_b_coding_agent.py`, `local_llm.py`, `runner.py`) | Baseline A (naive LLM) and Baseline B (tool-augmented agent) comparison implementations |
| `evaluation/` (`scenarios.py`, `experiment_runner.py`, `metrics.py`, `checklists/`, subfolders for `baselines/`, `evolution/`, `regression/`, `rollback/`, `sandbox/`) | 25-scenario catalog, execution harness, metric aggregation |
| `experience/logs/` | Task logs and metrics |
| `ui/` (`cli_interface.py`) | Prompt-based CLI (`load`, `show`, `help`, `quit`) |
| `testing/` | Cross-layer, integration, system, scenario, baseline/benchmark tests |
| `analytics/` | Capability growth/genealogy datasets, metrics, evolution history |
| `sandbox/` | Sandboxed execution support for validation/evolution |
| `scripts/` (`colab_setup.sh`, `demo_evolution_cycle.py`, `model_smoke_test.py`, `run_tests.sh`) | Reproducibility and demo scripts |
| `docs/ARCHITECTURE.md` | Authoritative architecture reference |
| `docs/MASTER_DOCUMENT.md` | This document |
| `.github/workflows/` | CI workflows for the test suites |

---

## Appendix D: Success Metrics Summary

See Section 19 (Metrics & Measurement Framework) for the full quantitative and qualitative metric definitions.

---

## Appendix E: Evaluation Forms & Checklists

(All 5 forms provided above in Section 1.4)

---

## CONCLUSION

This document specifies the complete SPS-CA system at **zero monetary cost**: architecture, capabilities, user workflow, self-programming mechanism, and evaluation design.

**Key points:**

1. **It is complete** — all 10 layers implemented (`layers/layer_0N_name/`), plus supporting `models/`, `coding/`, `execution/`, `governance/`, `validation/`, `memory/`, `data/`, and `analytics/` infrastructure
2. **It is reproducible** — anyone can clone the repository and follow `SETUP.md`; `REQUIREMENTS.md` pins the exact hardware/model used
3. **It is language-agnostic on the target side** — Python core, any-language user projects via tree-sitter
4. **It has a comprehensive evaluation design** — 25 scenarios (20 mandatory + 5 extended) across three baselines and three target-language projects
5. **It emphasizes self-programming** — capability generation (Type B changes) is the research subject
6. **It is evidence-based** — 15 defined artifacts support the thesis claims
7. **It is positioned against the market** — Section 4 compares SPS-CA to Copilot, Cursor, Claude Code, Codex, Devin, Windsurf, Aider, and Codebuff on the governance/experience/evolution dimensions that matter to the thesis claim, not raw coding benchmarks

**Deliverables:** Complete SPS-CA system + thesis, at $0 development cost.

---

**Prepared by:** Muhammad Nauman Tahir

---

*For questions, refer to `docs/ARCHITECTURE.md`, `README.md`, or contact the thesis supervisor.*

