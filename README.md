# SPS-CA: Self-Programming Code Assistant

**Version:** 0.1.0 (Phase 0: Setup)  
**Status:** Development (Phases 0-10 in progress)  
**Timeline:** ~18-20 weeks (development) + evaluation + thesis writing  
**Budget:** $0 (Zero-cost, free open-source stack)  

---

## 📋 Overview

**SPS-CA** is a research prototype implementing a reference framework for Self-Programming Software (SPS). It demonstrates how software can safely, tracefully, and reversibly modify its own logic through a 10-layer architecture.

### Key Features (In Development)

- ✅ **10-Layer Architecture:** Cognitive Core, Experience, Meta-Learning, Adaptation, Evolution, Governance, Validation, Execution
- ✅ **Language-Agnostic Analysis:** Parse and modify code in Python, Java, JavaScript, Go, C# (via tree-sitter)
- ✅ **Self-Programming:** Generate new capabilities from repeated failure patterns
- ✅ **Governance & Safety:** DNA constraints, decision gates, rollback mechanisms
- ✅ **Learning:** Accumulate experience, detect patterns, improve strategy selection
- ✅ **Traceability:** Complete audit trail of all decisions and modifications

### What This Is NOT

❌ Production-ready code generation  
❌ A general-purpose AI assistant  
❌ Autonomous code modification (without governance)  
❌ A replacement for human developers  

### What This IS

✅ A research prototype demonstrating self-programming framework concepts  
✅ An experimental platform for evaluating AI-driven code evolution  
✅ A thesis artifact for MS Computer Science (Virtual University of Pakistan)  
✅ A reference implementation of SPS concepts  

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPS-CA INTERNAL SYSTEM                        │
│  (Python-based, self-modifying, orchestration engine)          │
│                                                                 │
│  Layer 10: Execution Layer                                      │
│  Layer 9:  Capability Registry                                  │
│  Layer 8:  Evolution Layer (Self-Programming)                   │
│  Layer 7:  Governance Layer (Safety & DNA Enforcement)         │
│  Layer 6:  Validation & V&V Layer (Sandbox, Testing)           │
│  Layer 5:  Adaptation Layer (Parameter Adjustment)             │
│  Layer 4:  Meta-Learning Layer (Strategy Improvement)          │
│  Layer 3:  Experience Layer (Task Logging & History)           │
│  Layer 2:  Cognitive Core (Planning, Analysis, Context)        │
│  Layer 1:  Software DNA (Constraints, Seed Capabilities)       │
│                                                                 │
│  Output: capabilities/generated/CAP-*/ (versioned Python mods) │
│                                                                 │
└────────────────────────┬─────────────────────────────────────────┘
                         │ Analyzes & Modifies
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│            USER TARGET PROJECTS (Any Language)                   │
│  Python (FastAPI) | Java (Spring Boot) | TypeScript (Express)  │
│  Go, C#, etc.                                                   │
│                                                                 │
│  Source Code, Tests, Configuration                             │
│                                                                 │
│  Output: Modified user project (visible deliverable)           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Directory Structure

```
sps-ca/
├── README.md                              # This file
├── requirements.txt                       # Python dependencies
├── setup.py                               # Package configuration
├── Dockerfile                             # For reproducibility
├── .gitignore                             # Git ignore rules
│
├── core/                                  # 10-Layer Implementation
│   ├── __init__.py
│   ├── layer_1_dna.py                    # Layer 1: Software DNA
│   ├── layer_2_cognitive_core.py         # Layer 2: Cognitive Core
│   ├── layer_3_experience.py             # Layer 3: Experience
│   ├── layer_4_meta_learning.py          # Layer 4: Meta-Learning
│   ├── layer_5_adaptation.py             # Layer 5: Adaptation
│   ├── layer_6_validation.py             # Layer 6: Validation & V&V
│   ├── layer_7_governance.py             # Layer 7: Governance
│   ├── layer_8_evolution.py              # Layer 8: Evolution
│   ├── layer_9_registry.py               # Layer 9: Capability Registry
│   ├── layer_10_execution.py             # Layer 10: Execution
│   ├── llm_interface.py                  # Interface to local Ollama
│   └── tests/                            # Unit tests for all layers
│       ├── test_layer_1.py
│       ├── test_layer_2.py
│       └── ...
│
├── ui/                                    # User Interface
│   ├── __init__.py
│   ├── cli_interface.py                  # Command-line REPL interface
│   └── session_history.json              # Interaction history (created at runtime)
│
├── capabilities/                          # Capability Management
│   ├── seeds/                            # Built-in Capabilities (CAP-001 to CAP-008)
│   │   ├── CAP-001/                      # Simple Bug Detection
│   │   │   ├── capability.py
│   │   │   ├── tests.py
│   │   │   ├── metadata.json
│   │   │   └── README.md
│   │   ├── CAP-002/                      # Syntax Error Fix
│   │   ├── ... (CAP-003 through CAP-008)
│   │
│   ├── generated/                        # Generated Capabilities (created during evolution)
│   │   ├── CAP-009/                      # Will be created in Phase 4
│   │   └── ...
│   │
│   └── registry.json                     # Central capability registry
│
├── projects/                              # Target Projects for Testing
│   ├── project_a_python/                 # FastAPI (Python) - to be created Phase 8
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── models.py
│   │   ├── tests/
│   │   └── requirements.txt
│   │
│   ├── project_b_java/                   # Spring Boot (Java) - to be created Phase 8
│   │   ├── pom.xml
│   │   ├── src/main/java/...
│   │   └── src/test/java/...
│   │
│   └── project_c_typescript/             # Express.js (TypeScript) - to be created Phase 8
│       ├── package.json
│       ├── src/
│       ├── tests/
│       └── tsconfig.json
│
├── sandbox/                               # Isolated Execution Environment
│   ├── __init__.py
│   ├── sandbox_executor.py               # Execute changes safely in isolation
│   └── test_runner.py                    # Run tests in sandbox
│
├── governance/                            # Governance & Decision Logging
│   ├── dna_rules.json                    # Immutable DNA constraints
│   └── decisions/                        # Decision audit trail (created at runtime)
│       └── decision_001.json
│       └── decision_002.json
│       └── ...
│
├── experience/                            # Experience & Learning Logs
│   └── logs/                             # Task history (created at runtime)
│       ├── experience_log.json           # All tasks and outcomes
│       └── failure_patterns.json         # Aggregated failure categories
│
├── evaluation/                            # Evaluation Results & Metrics
│   ├── scenarios/                        # Scenario execution results
│   ├── sandbox/                          # Sandbox validation results
│   ├── regression/                       # Regression test results
│   ├── rollback/                         # Rollback execution traces
│   ├── checklists/                       # Evaluation forms (Appendix E)
│   ├── metrics/                          # Aggregated metrics
│   └── comparison/                       # Baseline A vs B vs SPS-CA
│
├── baselines/                             # Baseline Agents (Phase 9)
│   ├── __init__.py
│   ├── baseline_a_naive_llm.py           # Naive LLM (no learning)
│   ├── baseline_b_coding_agent.py        # Tool-augmented agent (no evolution)
│   └── tests/
│
└── docs/                                  # Documentation
    ├── architecture.md                   # Detailed architecture guide
    ├── phase_0_setup.md                  # This phase's documentation
    ├── phase_1_layers.md                 # (Created as phases progress)
    └── ...
```

---

## 🔧 Setup Instructions

### Prerequisites

- **Python:** 3.11 or higher
- **RAM:** ≥16GB (for running Ollama LLM locally)
- **Storage:** ≥100GB free (for LLM model + code + test data)
- **OS:** macOS, Linux, or Windows (with WSL2/Docker)
- **Git:** Latest version

### Step 1: Clone Repository

```bash
git clone https://github.com/muhammadnaumantahir/SPS_CA.git
cd SPS_CA
```

### Step 2: Install Python 3.11+

**macOS:**
```bash
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-dev
```

**Windows:**
- Download from https://www.python.org/downloads/
- Install Python 3.11+

Verify:
```bash
python --version  # Should be 3.11+
```

### Step 3: Create Virtual Environment

```bash
python -m venv venv

# Activate (macOS/Linux):
source venv/bin/activate

# Activate (Windows):
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- `tree-sitter` (code parsing)
- `pydantic` (data validation)
- `pytest` (testing)
- `sqlalchemy` (database)
- `requests` (HTTP)
- And 20+ other dependencies

Verify:
```bash
python -c "import tree_sitter; import pytest; print('✓ Dependencies installed')"
```

### Step 5: Install & Configure Ollama (Local LLM)

Ollama runs large language models locally, without cloud API costs.

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
- Download from https://ollama.ai
- Install and run

**Step 5a: Download LLM Model**

Choose ONE model (Qwen3-Coder as recommended):

```bash
# Recommended: Qwen3-Coder 30B (best for code, ~25GB)
ollama pull qwen2.5-coder:32b

# Alternative: Llama2 70B (~40GB, better general reasoning)
# ollama pull llama2:70b

# Alternative: Mistral 8x7B (~25GB, smaller & faster)
# ollama pull mistral:8x7b
```

**Step 5b: Start Ollama Server**

In a terminal (keep running):
```bash
ollama serve
```

You should see:
```
Ollama is running on http://localhost:11434
```

**Step 5c: Test Ollama**

In another terminal:
```bash
ollama list  # Shows installed models
curl http://localhost:11434/api/tags  # Verify API is up
```

### Step 6: Create Directory Structure

The repository should already have the structure above. Verify:

```bash
ls -la core/           # Should exist
ls -la capabilities/   # Should exist
ls -la projects/       # Should exist
```

If any are missing, create them:
```bash
mkdir -p core/tests
mkdir -p capabilities/seeds capabilities/generated
mkdir -p projects
mkdir -p sandbox
mkdir -p governance/decisions
mkdir -p experience/logs
mkdir -p evaluation/{scenarios,sandbox,regression,rollback,checklists,metrics}
mkdir -p baselines
mkdir -p docs
```

### Step 7: Test Installation

```bash
# Test Python environment
python -c "import sys; print(f'Python {sys.version}')"

# Test Ollama is running (in separate terminal)
curl http://localhost:11434/api/tags

# Test pytest
pytest --version

# Run initial tests (if any exist)
pytest core/tests/ -v  # (May be empty until Phase 1)
```

All should succeed without errors.

### Step 8: Initialize Git (If Not Done)

```bash
git config user.name "Muhammad Nauman Tahir"
git config user.email "your_email@virtualuniversity.edu.pk"

git add .
git commit -m "PHASE 0: Initial project setup and directory structure"
git push origin main
```

---

## 📊 Phase Progress

| Phase | Title | Status | Weeks |
|-------|-------|--------|-------|
| 0 | Project Setup | 🟢 Current | 1-2 |
| 1 | Layers 1-2 | ⬜ Pending | 3-4 |
| 2 | Layers 3-5 | ⬜ Pending | 5-6 |
| 3 | Layers 6-7 | ⬜ Pending | 7-8 |
| 4 | Layer 8 | ⬜ Pending | 9-10 |
| 5 | Layers 9-10 | ⬜ Pending | 11-12 |
| 6 | Seed Capabilities | ⬜ Pending | 13-14 |
| 7 | User Interface | ⬜ Pending | 15-16 |
| 8 | Target Projects | ⬜ Pending | 17-18 |
| 9 | Baselines | ⬜ Pending | 19-20 |
| 10 | Evaluation | ⬜ Pending | 21-22+ |

---

## 🚀 Quick Start (After Setup)

Once all setup is complete:

```bash
# Terminal 1: Keep Ollama running
ollama serve

# Terminal 2: Activate venv and run SPS-CA
source venv/bin/activate
python -m ui.cli_interface

# You should see:
# > Welcome to SPS-CA (Self-Programming Code Assistant)
# > Commands: load <project>, help, show <context>, quit
# > You:
```

(CLI interface created in Phase 7)

---

## 📖 Documentation

- **[Architecture Guide](docs/architecture.md)** — Detailed 10-layer architecture
- **[Master Document](../SPS_CA_Master_Document_v4_0_UPDATED.md)** — Complete specification
- **[Phase Specifications](docs/)** — Phase-by-phase instructions
- **[API Reference](docs/api.md)** — Layer interfaces (created during phases)

---

## 🧪 Testing

```bash
# Run all tests
pytest core/tests/ -v

# Run with coverage
pytest core/tests/ --cov=core --cov-report=html

# Run specific test file
pytest core/tests/test_layer_1.py -v

# Run with verbose output
pytest -vv

# Run with timeout (good for long LLM inference)
pytest --timeout=300
```

---

## 🛠️ Development Workflow

### During Development (Each Phase)

1. **Setup:** Create feature branch
2. **Code:** Implement layer/feature per spec
3. **Test:** Write unit tests (>80% coverage)
4. **Review:** Student reviews locally
5. **Fix:** Iterate on feedback
6. **Approve:** Student approves
7. **Merge:** Push to main with phase tag

### Git Workflow

```bash
# Create branch for phase
git checkout -b phase-N-dev

# Work on code...
# Add and commit
git add .
git commit -m "PHASE N: <description>"

# Push to GitHub
git push origin phase-N-dev

# After review/approval:
git checkout main
git merge phase-N-dev
git tag phase-N-complete
git push origin main --tags
```

---

## 💰 Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| LLM (Ollama) | $0 | Free, open-source, local |
| Code Parsing (tree-sitter) | $0 | Free, open-source |
| Database (SQLite) | $0 | Free, built-in |
| Testing (pytest) | $0 | Free, open-source |
| Hosting (GitHub Free) | $0 | Free tier unlimited |
| Compute (Local machine) | $0 | Your existing hardware |
| **TOTAL** | **$0** | ✅ Zero cost |

---

## ⚠️ Important Notes

1. **Ollama Setup:** Downloading the LLM model (~25-40GB) may take 1-2 hours on first setup.
2. **Model Size:** Qwen3-Coder 32B requires ~32GB RAM while running. If your machine has 16GB, use a smaller model (mistral:8x7b) or reduce batch size.
3. **Reproducibility:** Keep Ollama running with the same model throughout the project for consistent results.
4. **Python Version:** Must be 3.11+. Tree-sitter requires modern Python.
5. **Network:** Stable internet required for initial setup and Phase 10 (if needed).

---

## 📞 Support & Communication

- **Questions?** Ask in chat or GitHub Issues
- **Bug reports?** Create GitHub Issue with reproduction steps
- **Weekly syncs:** Friday updates on progress
- **Supervisor contact:** [Communicate via email/meeting as arranged]

---

## 📜 License

This project is part of a Master's thesis and is provided for research/educational purposes.

---

## 👨‍🎓 Author

**Muhammad Nauman Tahir**  
MS Computer Science  
Virtual University of Pakistan  
Student ID: MS240400054  

Supervisor: **Dr. Muhammad Salman Bashir**

---

## 🎯 Thesis Claim

> "A reference framework (SPS) exists that defines characteristics, design principles, and layered architecture necessary for software to safely, tracefully, and reversibly modify its own logic."

This repository implements SPS-CA to prove this claim through working code, 25 experimental scenarios, and measurable evidence.

---

**Status:** Phase 0 (Setup) ✅ IN PROGRESS  
**Next:** Phase 1 (Layers 1-2) — Awaiting approval  
**Last Updated:** 2026-08-31

---

*For complete project details, see the Master Document: SPS_CA_Master_Document_v4_0_UPDATED.md*
