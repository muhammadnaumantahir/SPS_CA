# PHASE 0: PROJECT SETUP & INFRASTRUCTURE CHECKLIST

**Status:** In Progress  
**Timeline:** Weeks 1-2  
**Student:** Muhammad Nauman Tahir  
**Supervisor:** Dr. Muhammad Salman Bashir  
**Start Date:** [TBD]  

---

## 📋 PHASE 0 DELIVERABLES CHECKLIST

Complete all items below to finish Phase 0. Check off as you complete.

### 1️⃣ ENVIRONMENT SETUP (Local Machine)

**You must complete these on your machine:**

- [ ] **Python 3.11+ Installed**
  - Verify: `python --version` (should be 3.11 or higher)
  - Instructions: See README.md Step 2

- [ ] **Virtual Environment Created**
  - Verify: `source venv/bin/activate` (you see `(venv)` in prompt)
  - Instructions: See README.md Step 3

- [ ] **Python Dependencies Installed**
  - Verify: `pip list | grep tree-sitter` (should show tree-sitter packages)
  - Run: `pip install -r requirements.txt`
  - Instructions: See README.md Step 4

- [ ] **Ollama Installed & Running**
  - Verify: `ollama list` (shows installed models)
  - Run: `ollama serve` in background terminal
  - Instructions: See README.md Step 5

- [ ] **LLM Model Downloaded (Qwen3-Coder 32B)**
  - Verify: `ollama list` shows `qwen2.5-coder:32b`
  - Run: `ollama pull qwen2.5-coder:32b` (~25GB, takes 1-2 hours first time)
  - Note: Keep this running during all development
  - Instructions: See README.md Step 5a

- [ ] **Ollama API Verified**
  - Test: `curl http://localhost:11434/api/tags`
  - Should return JSON with model list
  - Instructions: See README.md Step 5c

### 2️⃣ PROJECT FILES SETUP (GitHub Repository)

**I've created these files. Push them to your GitHub repo:**

Files to add to GitHub (already created by me):
- [ ] `requirements.txt` — Python dependencies
- [ ] `setup.py` — Package configuration
- [ ] `README.md` — Project overview & setup instructions
- [ ] `.gitignore` — Git ignore rules
- [ ] `Dockerfile` — Container reproducibility
- [ ] `core/__init__.py` — Core package placeholder
- [ ] `ui/__init__.py` — UI package placeholder
- [ ] `capabilities/__init__.py` — Capabilities package
- [ ] `baselines/__init__.py` — Baselines package
- [ ] `sandbox/__init__.py` — Sandbox package
- [ ] `PHASE_0_SETUP_CHECKLIST.md` — This file

All files are in `/home/claude/` — copy them to your local repo.

### 3️⃣ DIRECTORY STRUCTURE CREATION

**Verify these directories exist in your repo:**

Core directories:
- [ ] `core/` (exists from __init__.py)
- [ ] `core/tests/` (create: `mkdir -p core/tests`)
- [ ] `ui/` (exists from __init__.py)
- [ ] `capabilities/` (exists)
- [ ] `capabilities/seeds/` (create subdirectory)
- [ ] `capabilities/generated/` (create subdirectory)
- [ ] `sandbox/` (exists)
- [ ] `governance/` (create: `mkdir -p governance/decisions`)
- [ ] `experience/` (create: `mkdir -p experience/logs`)
- [ ] `evaluation/` (create: `mkdir -p evaluation/{scenarios,sandbox,regression,rollback,checklists,metrics}`)
- [ ] `baselines/` (exists)
- [ ] `projects/` (create: `mkdir -p projects`)
- [ ] `docs/` (create: `mkdir -p docs`)

Test directory structure:
```bash
# Run this to create all directories:
mkdir -p core/tests \
  capabilities/seeds capabilities/generated \
  projects \
  sandbox \
  governance/decisions \
  experience/logs \
  evaluation/{scenarios,sandbox,regression,rollback,checklists,metrics} \
  baselines \
  docs
```

### 4️⃣ GIT SETUP & INITIALIZATION

**Set up Git on your machine:**

- [ ] **Clone Repository**
  ```bash
  git clone https://github.com/muhammadnaumantahir/SPS_CA.git
  cd SPS_CA
  ```

- [ ] **Configure Git User** (if not already done)
  ```bash
  git config user.name "Muhammad Nauman Tahir"
  git config user.email "your_email@virtualuniversity.edu.pk"
  ```

- [ ] **Copy Phase 0 Files to Local Repo**
  - Copy all files from my `/home/claude/` to your local `SPS_CA/`
  - Maintain directory structure as shown above

- [ ] **Add All Files to Git**
  ```bash
  git add .
  ```

- [ ] **Create Initial Commit**
  ```bash
  git commit -m "PHASE 0: Initial project setup and directory structure"
  ```

- [ ] **Push to GitHub**
  ```bash
  git push origin main
  ```

- [ ] **Verify on GitHub**
  - Check: https://github.com/muhammadnaumantahir/SPS_CA
  - Should see all files in repo

### 5️⃣ TESTING & VERIFICATION

**Verify everything works:**

- [ ] **Test Python Installation**
  ```bash
  python -c "import sys; print(f'Python {sys.version}')"
  ```
  Expected: Shows Python 3.11+

- [ ] **Test Virtual Environment**
  ```bash
  which python  # Should show path inside venv
  pip list | head  # Should show installed packages
  ```

- [ ] **Test Tree-Sitter Installation**
  ```bash
  python -c "from tree_sitter import Language, Parser; print('✓ tree-sitter OK')"
  ```

- [ ] **Test Pytest Installation**
  ```bash
  pytest --version
  ```
  Expected: Shows pytest version (7.4.3+)

- [ ] **Test Ollama Connection**
  ```bash
  curl http://localhost:11434/api/tags
  ```
  Expected: JSON output with model info

- [ ] **Test LLM Model**
  ```bash
  curl http://localhost:11434/api/generate \
    -d '{"model":"qwen2.5-coder:32b","prompt":"print hello","stream":false}'
  ```
  Expected: JSON response from model

- [ ] **Test Directory Structure**
  ```bash
  ls -la core/
  ls -la capabilities/
  ls -la projects/
  ls -la evaluation/
  ```
  Expected: All directories exist

- [ ] **Run Initial Tests** (empty for now)
  ```bash
  pytest core/tests/ -v
  ```
  Expected: "no tests ran" (directory is empty until Phase 1)

### 6️⃣ DOCUMENTATION REVIEW

**Ensure you understand the project:**

- [ ] **Read README.md** — Project overview and architecture
- [ ] **Read Master Document** — Complete specification (SPS_CA_Master_Document_v4_0_UPDATED.md)
- [ ] **Review Directory Structure** — Understand layout
- [ ] **Review Development Plan** — Understand YOUR and MY responsibilities

### 7️⃣ COMMUNICATION SETUP

**Establish communication with student (me):**

- [ ] **Confirm Readiness** — Reply with checklist completion status
- [ ] **Resolve Any Issues** — Ask if stuck on any step
- [ ] **Set Weekly Sync Time** — Agree on meeting schedule (if needed)
- [ ] **Verify Chat Access** — Confirm you can reach me in this conversation

---

## ✅ PHASE 0 COMPLETION CRITERIA

Phase 0 is **COMPLETE** when ALL of the following are true:

1. ✅ Python 3.11+ installed and verified
2. ✅ Virtual environment created and activated
3. ✅ All Python dependencies installed (`pip install -r requirements.txt`)
4. ✅ Ollama running locally with Qwen3-Coder 32B model loaded
5. ✅ Ollama API responds to curl requests
6. ✅ GitHub repo exists with all Phase 0 files pushed
7. ✅ Directory structure complete and verified
8. ✅ Git configured and initial commit pushed
9. ✅ All test verifications pass without errors
10. ✅ Student can run `pytest core/tests/ -v` (even if empty)
11. ✅ Student can import `tree_sitter`, `pytest`, `pydantic` in Python
12. ✅ Student has read README.md and understands project scope
13. ✅ Student confirms readiness via chat

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Issue: "Python 3.11 not found"
**Solution:**
- Install Python 3.11 from python.org
- Or use homebrew: `brew install python@3.11`
- Verify: `python3.11 --version`

### Issue: "venv: command not found"
**Solution:**
- Install python-dev package
- Ubuntu: `sudo apt-get install python3.11-venv`
- macOS: Already included with Python 3.11

### Issue: "Ollama: command not found"
**Solution:**
- Download from https://ollama.ai
- Run installer
- Add to PATH if needed
- Verify: `ollama --version`

### Issue: "Model download taking too long (>2 hours)"
**Solution:**
- Model is large (~25GB)
- Check internet speed
- Keep terminal open while downloading
- Can pause/resume with Ctrl+C and rerun `ollama pull`

### Issue: "Ollama runs but API not responding"
**Solution:**
- Ensure `ollama serve` is running in a terminal
- Keep it running in background
- Try: `curl http://localhost:11434/api/tags`
- If fails: restart ollama serve

### Issue: "Git push fails"
**Solution:**
- Verify GitHub token/credentials
- Check repo URL: `git remote -v`
- Ensure you have push permission
- Try: `git push origin main -u`

### Issue: "pytest import error"
**Solution:**
- Activate venv: `source venv/bin/activate`
- Reinstall: `pip install --force-reinstall pytest`
- Verify: `pytest --version`

### Issue: "tree-sitter import error"
**Solution:**
- Reinstall: `pip install --force-reinstall tree-sitter`
- May need build tools: `sudo apt-get install build-essential` (Linux)
- Or Xcode Command Line Tools (macOS): `xcode-select --install`

---

## 📊 PROGRESS TRACKING

| Step | Status | Notes |
|------|--------|-------|
| Python 3.11+ | ⬜ | Verify in terminal |
| venv created | ⬜ | Activate before each session |
| Dependencies | ⬜ | `pip install -r requirements.txt` |
| Ollama installed | ⬜ | Keep running in background |
| LLM downloaded | ⬜ | ~25GB, may take 1-2 hours |
| GitHub repo | ⬜ | Push all Phase 0 files |
| Directories | ⬜ | All 12+ directories created |
| Git configured | ⬜ | Username + email set |
| Tests pass | ⬜ | `pytest core/tests/ -v` |
| Ready for Phase 1 | ⬜ | All checks complete |

---

## 🎯 NEXT STEPS (After Phase 0 Approval)

Once Phase 0 is complete and you confirm readiness:

1. **I will create Phase 1 code:**
   - Layer 1: Software DNA (dna_rules.json, layer_1_dna.py)
   - Layer 2: Cognitive Core (layer_2_cognitive_core.py)
   - Comprehensive tests (>80% coverage)

2. **You will:**
   - Review code in GitHub PR (or here in chat)
   - Run tests locally: `pytest core/tests/ -v`
   - Verify >80% coverage: `pytest --cov=core`
   - Ask questions or request changes
   - Approve when satisfied

3. **I will:**
   - Push to main with tag `phase-1-complete`
   - Update GitHub repo

4. **Repeat for Phases 2-10**

---

## 📞 SUPPORT

**Stuck on any step?**
- Ask in this chat → I'll help diagnose
- Reference the section in README.md → Step-by-step instructions
- Check Common Issues above → May have quick fix

**Timeline:**
- Phase 0 should take 4-8 hours (mostly waiting for model download)
- Once complete, move to Phase 1 immediately

---

## 📝 SIGN-OFF

**Phase 0 is complete when:**
- [ ] All checklist items checked ✅
- [ ] All tests pass ✅
- [ ] All files in GitHub ✅
- [ ] You reply: "PHASE 0 COMPLETE - Ready for Phase 1" ✅

**Then:**
- I create Phase 1 code
- You review and test
- Iterate until approved
- Move to Phase 2

---

**Version:** 1.0  
**Last Updated:** 2026-08-31  
**Next Phase:** Phase 1 (Layers 1-2)

---

**LET'S GO! 🚀**
