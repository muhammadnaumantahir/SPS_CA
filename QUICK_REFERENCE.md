# SPS-CA: Quick Reference Guide

**Your Role:** Environment setup, code review, testing, decision-making  
**My Role:** Code generation, architecture, documentation, iteration  
**Communication:** This chat  
**Timeline:** ~20 weeks development + evaluation

---

## 🎯 PROJECT AT A GLANCE

**What:** Self-Programming Software Prototype with 10-layer architecture  
**Why:** Thesis research — demonstrate framework for AI-driven code evolution  
**How:** Build 10 layers → implement 8 capabilities → run 25 scenarios → collect metrics  
**Timeline:** 20 weeks dev (Phases 0-10) + evaluation + thesis  
**Cost:** $0 (free open-source stack)  

---

## 📚 10 LAYERS (Overview)

```
Layer 10: Execution         → Apply changes safely to user projects
Layer 9:  Registry          → Manage versioned capabilities
Layer 8:  Evolution         → Generate new capabilities (self-programming!) ⭐
Layer 7:  Governance        → Enforce DNA rules, decision gates
Layer 6:  Validation        → Sandbox testing, regression detection
Layer 5:  Adaptation        → Reuse capabilities with adjustments
Layer 4:  Meta-Learning     → Improve strategy selection over time
Layer 3:  Experience        → Log all tasks and outcomes
Layer 2:  Cognitive Core    → Plan and analyze requests
Layer 1:  Software DNA      → Immutable constraints
```

**Research focus:** Layers 4, 5, 8 (learning, adaptation, evolution)

---

## 🗂️ FILE LAYOUT

```
sps-ca/
├── requirements.txt       ← Dependencies
├── setup.py              ← Package config
├── README.md             ← Setup + overview
├── Dockerfile            ← Reproducibility
│
├── core/                 ← 10 layers + tests
│   ├── layer_1_dna.py
│   ├── layer_2_cognitive_core.py
│   ├── ... (layers 3-10)
│   └── tests/            ← Your test runs here: pytest core/tests/ -v
│
├── capabilities/
│   ├── seeds/            ← Built-in (CAP-001 to CAP-008) — Phase 6
│   ├── generated/        ← Auto-created (CAP-009+) — Phase 4+
│   └── registry.json
│
├── projects/             ← Target projects for testing
│   ├── project_a_python/  ← FastAPI (Python) — Phase 8
│   ├── project_b_java/    ← Spring Boot (Java) — Phase 8
│   └── project_c_typescript/ ← Express.js (TypeScript) — Phase 8
│
├── evaluation/           ← Results & metrics
│   ├── scenarios/        ← Scenario execution logs
│   ├── metrics/          ← Aggregated results
│   └── checklists/       ← Evaluation forms
│
└── baselines/            ← Comparison agents (Phase 9)
    ├── baseline_a_naive_llm.py
    └── baseline_b_coding_agent.py
```

---

## 📅 PHASE SCHEDULE

| Week | Phase | Task | Your Time | My Time |
|------|-------|------|----------|---------|
| 1-2 | 0 | Setup (Ollama, Python, GitHub) | 8h | 2h |
| 3-4 | 1 | Layers 1-2 (DNA, Cognitive Core) | 4h | 15h |
| 5-6 | 2 | Layers 3-5 (Experience, Meta-L, Adapt) | 4h | 20h |
| 7-8 | 3 | Layers 6-7 (Validation, Governance) | 4h | 20h |
| 9-10 | 4 | Layer 8 (Evolution — SELF-PROGRAMMING!) | 4h | 25h |
| 11-12 | 5 | Layers 9-10 (Registry, Execution) | 4h | 20h |
| 13-14 | 6 | Seed Capabilities (CAP-001 to CAP-008) | 6h | 25h |
| 15-16 | 7 | User Interface (CLI, REPL) | 4h | 15h |
| 17-18 | 8 | Target Projects (Python, Java, TypeScript) | 8h | 20h |
| 19-20 | 9 | Baseline Agents (A, B for comparison) | 4h | 15h |
| 21-22+ | 10 | Evaluation (Run 25 scenarios, collect metrics) | 20h | 10h |
| **Total** | — | — | **70h** | **187h** |

**Your weekly commitment:** ~3-4 hours  
**My weekly commitment:** ~6-7 hours  

---

## 👨‍💼 PER-PHASE WORKFLOW

**Every phase follows this pattern:**

```
1. I write code (per spec)
   ↓
2. I push to GitHub
   ↓
3. You review locally
   - Run: pytest core/tests/ -v
   - Check: Coverage >80%?
   - Read: Code makes sense?
   - Test: Any issues?
   ↓
4. You approve or request changes
   ↓
5. If changes needed: I iterate, repeat 2-4
   ↓
6. You approve: "Phase X looks good!"
   ↓
7. I merge and tag: phase-X-complete
   ↓
8. File form: "Phase X complete" (Appendix E)
   ↓
9. Start Phase X+1
```

---

## 🧪 YOUR KEY RESPONSIBILITIES

### Every Phase

1. **Review Code**
   - Does it match the spec?
   - Is it readable?
   - Are comments clear?

2. **Run Tests**
   ```bash
   pytest core/tests/ -v          # Run all tests
   pytest --cov=core              # Check coverage
   ```
   - Coverage must be >80%
   - All tests must pass

3. **Approve or Reject**
   - Approve: "Phase X looks good, ready to merge"
   - Reject: "Need changes: [list]"

4. **File Form**
   - Appendix E, Form 1 (completion checklist)
   - Weekly checkpoint (Form 4)

### Phase 0 (NOW)

- [ ] Install Python 3.11+
- [ ] Create venv
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Download Ollama model (Qwen3-Coder 32B)
- [ ] Push all Phase 0 files to GitHub
- [ ] Verify everything works
- [ ] Confirm: "PHASE 0 COMPLETE"

### Phase 1 (Next)

- Review my Layers 1-2 code
- Run tests: `pytest core/tests/ -v`
- Check coverage: `pytest --cov=core`
- Approve when satisfied

---

## 🤖 MY KEY RESPONSIBILITIES

### Every Phase

1. **Write Code** (following spec exactly)
2. **Write Tests** (>80% coverage per phase)
3. **Document** (docstrings, comments, README)
4. **Push to GitHub** (clean commits, phase tags)
5. **Iterate** (fix issues from your feedback)

### Phase 0 (NOW)

✅ Create all these files:
- requirements.txt
- setup.py
- README.md
- .gitignore
- Dockerfile
- Package __init__ files
- Phase 0 checklist
- This quick reference

### Phase 1 (Next)

Generate:
- `core/layer_1_dna.py` (DNA rules, seed capabilities)
- `core/layer_2_cognitive_core.py` (planning, analysis)
- `core/tests/test_layer_1.py` (unit tests)
- `core/tests/test_layer_2.py` (unit tests)
- README for Layers 1-2

---

## 📊 KEY METRICS (Thesis Claims)

By end of Phase 10, we must demonstrate:

| Metric | Target | Measured How |
|--------|--------|--------------|
| **Task Success Rate** | >65% | % of 25 scenarios completed |
| **Meta-Learning** | >15% improvement | Baseline vs final success rate |
| **Cross-Language Reuse** | >60% | Capabilities work across languages |
| **Regression Rate** | <2% | Bugs introduced by changes |
| **Test Coverage** | >80% | Generated code coverage |
| **Rollback Success** | >95% | Failed changes restored correctly |
| **Governance Accuracy** | 100% | DNA rules enforced perfectly |

---

## 🔧 COMMANDS YOU'LL USE

```bash
# Setup (Phase 0)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ollama (Phase 0+)
ollama serve              # Start (keep running)
ollama pull qwen2.5-coder:32b  # Download model
ollama list               # Check installed models
curl http://localhost:11434/api/tags  # Test API

# Testing (Every Phase)
pytest core/tests/ -v                 # Run tests
pytest --cov=core                     # Check coverage
pytest core/tests/test_layer_1.py -v  # Run specific test

# Git (Every Phase)
git add .
git commit -m "PHASE X: description"
git push origin main

# Run SPS-CA (Phase 7+)
python -m ui.cli_interface

# Build Docker (Optional)
docker build -t sps-ca .
docker run -it sps-ca
```

---

## ⚠️ CRITICAL REQUIREMENTS

**MUST HAVE:**
1. ✅ Python 3.11+ (not 3.10!)
2. ✅ Ollama running with Qwen3-Coder 32B (keep in background)
3. ✅ ~16GB RAM (for Ollama)
4. ✅ ~100GB free disk (for model + code + data)
5. ✅ Git configured (username + email)
6. ✅ GitHub account with write access to repo

**MUST DO:**
1. ✅ Review code before approval
2. ✅ Run tests: `pytest core/tests/ -v`
3. ✅ Verify coverage >80%: `pytest --cov`
4. ✅ File completion forms (Appendix E)
5. ✅ Weekly sync updates
6. ✅ Communicate issues early

**MUST NOT:**
1. ❌ Skip testing/review
2. ❌ Merge code you haven't tested locally
3. ❌ Stop Ollama during development
4. ❌ Ignore feedback requests
5. ❌ Rush through phases

---

## 📞 COMMUNICATION

**How to reach me:**
- Ask in this chat
- I respond within hours (usually minutes)
- For bugs: Describe issue → I diagnose → I fix → you test

**Expected turnaround:**
- Code generation: 1-3 hours per phase
- Feedback response: <1 hour
- Issue fixes: <2 hours

**Weekly sync:**
- Friday updates (optional, unless blocked)
- Status: "Phase X on track" or "Phase X needs adjustment"
- Form 4 checkpoint

---

## 🎓 THESIS TIMELINE

```
Phases 0-10:        18-20 weeks (development)
Phase 10 execution: 4-6 weeks (scenarios)
Buffer:             4-6 weeks (adjustments)
Thesis writing:     8-10 weeks
TOTAL:              ~36-40 weeks (fits in 1-year MS program ✅)
```

---

## 🚀 READY TO START?

**Phase 0 Setup Checklist:**

- [ ] Read this quick reference
- [ ] Read README.md (complete setup guide)
- [ ] Read PHASE_0_SETUP_CHECKLIST.md (detailed steps)
- [ ] Install Python 3.11+
- [ ] Create venv
- [ ] Install dependencies
- [ ] Install Ollama + download model
- [ ] Push Phase 0 files to GitHub
- [ ] Verify all tests pass
- [ ] Reply: "PHASE 0 COMPLETE - Ready for Phase 1"

**Then:**
- I create Phase 1 code
- You review & test
- You approve → I merge
- Repeat for Phases 2-10

---

## 📚 REFERENCE DOCUMENTS

Must read (in order):
1. **QUICK_REFERENCE.md** (this file) — Overview
2. **README.md** — Setup + architecture
3. **PHASE_0_SETUP_CHECKLIST.md** — Detailed setup
4. **SPS_CA_Master_Document_v4_0_UPDATED.md** — Complete spec

Should read (as phases progress):
- Individual phase documentation (created in docs/)
- Code comments and docstrings
- GitHub commit messages

---

## ✅ PHASE 0 STATUS

| Item | Status | Notes |
|------|--------|-------|
| Project files | ✅ Ready | requirements.txt, setup.py, README, etc. |
| Directory structure | ✅ Ready | core/, capabilities/, projects/, etc. |
| Git configuration | ✅ Ready | setup.py configured, .gitignore ready |
| Documentation | ✅ Ready | README.md, checklists, quick reference |
| **Student setup** | ⏳ Waiting | Your turn: install Python, Ollama, dependencies |
| **GitHub push** | ⏳ Waiting | You copy files to repo and push |
| **Verification** | ⏳ Waiting | You run tests and confirm working |

---

## 🎯 IMMEDIATE NEXT STEPS

**For you RIGHT NOW:**

1. **Read README.md** — Full setup instructions
2. **Read PHASE_0_SETUP_CHECKLIST.md** — Step-by-step checklist
3. **Install Python 3.11+** — Verify: `python --version`
4. **Create venv** — Verify: `source venv/bin/activate`
5. **Install dependencies** — Run: `pip install -r requirements.txt`
6. **Install Ollama** — Download from https://ollama.ai
7. **Download model** — Run: `ollama pull qwen2.5-coder:32b` (1-2 hours)
8. **Copy files to repo** — Copy all files from my `/home/claude/` to your local SPS_CA/
9. **Git push** — `git add . && git commit -m "PHASE 0: ..." && git push`
10. **Verify & Test** — Run `pytest core/tests/ -v`
11. **Confirm** — Reply: "PHASE 0 COMPLETE"

**Time estimate:** 4-8 hours (mostly waiting for model download)

**Then:** I create Phase 1 code, you review it, approve it, move to Phase 2.

---

**LET'S BUILD THIS! 🚀**

Questions? Ask in chat. Let's go!
