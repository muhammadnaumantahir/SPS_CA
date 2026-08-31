#!/bin/bash

################################################################################
# SPS-CA PHASE 0: AUTOMATED SETUP & GITHUB PUSH SCRIPT
# 
# This script automates the entire Phase 0 setup:
# 1. Clones your GitHub repo (if needed)
# 2. Copies all Phase 0 files
# 3. Creates directory structure
# 4. Commits to git
# 5. Pushes to GitHub
#
# Usage:
#   bash SETUP_AND_PUSH.sh
#
# Prerequisites:
#   - Git installed: git --version
#   - GitHub SSH or HTTPS configured
#   - GitHub credentials working
#
################################################################################

set -e  # Exit on any error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  SPS-CA PHASE 0: AUTOMATED SETUP & GITHUB PUSH                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
REPO_URL="https://github.com/muhammadnaumantahir/SPS_CA.git"
REPO_DIR="$HOME/SPS_CA"
GITHUB_USER="muhammadnaumantahir"
GITHUB_EMAIL="nauman@example.com"  # Update with your actual email

echo "📋 Configuration:"
echo "   Repo URL: $REPO_URL"
echo "   Local path: $REPO_DIR"
echo "   GitHub user: $GITHUB_USER"
echo ""

# Step 1: Check if git is installed
echo "✓ Step 1: Checking git installation..."
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    echo "   macOS: brew install git"
    echo "   Linux: sudo apt-get install git"
    echo "   Windows: Download from https://git-scm.com"
    exit 1
fi
echo "  Git version: $(git --version)"
echo ""

# Step 2: Clone repo if needed
echo "✓ Step 2: Setting up repository..."
if [ ! -d "$REPO_DIR" ]; then
    echo "  Cloning repository from GitHub..."
    git clone "$REPO_URL" "$REPO_DIR"
    echo "  ✅ Repository cloned"
else
    echo "  Repository already exists at $REPO_DIR"
fi
echo ""

# Step 3: Change to repo directory
cd "$REPO_DIR"
echo "✓ Step 3: Working in $REPO_DIR"
echo ""

# Step 4: Configure git (if not already done)
echo "✓ Step 4: Configuring git..."
CURRENT_USER=$(git config user.name)
CURRENT_EMAIL=$(git config user.email)

if [ -z "$CURRENT_USER" ]; then
    echo "  Setting git user.name to $GITHUB_USER"
    git config user.name "$GITHUB_USER"
fi

if [ -z "$CURRENT_EMAIL" ]; then
    echo "  Setting git user.email to $GITHUB_EMAIL"
    git config user.email "$GITHUB_EMAIL"
fi

echo "  Git user: $(git config user.name) <$(git config user.email)>"
echo ""

# Step 5: Copy Phase 0 files
echo "✓ Step 5: Copying Phase 0 files..."

# Copy main files
echo "  Copying: requirements.txt, setup.py, README.md, .gitignore, Dockerfile"
cp /home/claude/requirements.txt . 2>/dev/null || echo "  ⚠️  requirements.txt not found, skipping"
cp /home/claude/setup.py . 2>/dev/null || echo "  ⚠️  setup.py not found, skipping"
cp /home/claude/README.md . 2>/dev/null || echo "  ⚠️  README.md not found, skipping"
cp /home/claude/.gitignore . 2>/dev/null || echo "  ⚠️  .gitignore not found, skipping"
cp /home/claude/Dockerfile . 2>/dev/null || echo "  ⚠️  Dockerfile not found, skipping"

# Copy checklist and reference
echo "  Copying: PHASE_0_SETUP_CHECKLIST.md, QUICK_REFERENCE.md"
cp /home/claude/PHASE_0_SETUP_CHECKLIST.md . 2>/dev/null || echo "  ⚠️  Checklist not found, skipping"
cp /home/claude/QUICK_REFERENCE.md . 2>/dev/null || echo "  ⚠️  Quick reference not found, skipping"

echo "  ✅ Files copied"
echo ""

# Step 6: Create directory structure
echo "✓ Step 6: Creating directory structure..."

mkdir -p core/tests
mkdir -p ui
mkdir -p capabilities/seeds
mkdir -p capabilities/generated
mkdir -p sandbox
mkdir -p governance/decisions
mkdir -p experience/logs
mkdir -p evaluation/{scenarios,sandbox,regression,rollback,checklists,metrics}
mkdir -p baselines
mkdir -p projects
mkdir -p docs

echo "  ✅ Directories created"
echo ""

# Step 7: Create __init__.py files for packages
echo "✓ Step 7: Creating Python package __init__.py files..."

cat > core/__init__.py << 'EOF'
"""
SPS-CA Core: 10-Layer Implementation

This package contains the complete architecture for Self-Programming Software (SPS).

Layers:
  1. Layer 1: Software DNA - Immutable constraints
  2. Layer 2: Cognitive Core - Planning and analysis
  3. Layer 3: Experience - Task logging
  4. Layer 4: Meta-Learning - Strategy improvement
  5. Layer 5: Adaptation - Parameter adjustment
  6. Layer 6: Validation - Sandbox testing
  7. Layer 7: Governance - DNA enforcement
  8. Layer 8: Evolution - Capability generation (SELF-PROGRAMMING!)
  9. Layer 9: Registry - Capability management
  10. Layer 10: Execution - Safe application and rollback
"""

__version__ = "0.1.0"
__status__ = "Development (Phase 0-10)"
EOF

cat > ui/__init__.py << 'EOF'
"""
SPS-CA User Interface: Prompt-Based Interaction Layer

Provides ChatGPT-like interface for users.
Created in Phase 7.
"""

__version__ = "0.1.0"
EOF

cat > capabilities/__init__.py << 'EOF'
"""
SPS-CA Capabilities: Built-in and Generated Capabilities

Subdirectories:
  - seeds/: Built-in capabilities (CAP-001 through CAP-008)
  - generated/: Dynamically generated capabilities (CAP-009+)
"""

__version__ = "0.1.0"
EOF

cat > baselines/__init__.py << 'EOF'
"""
SPS-CA Baselines: Comparison Agents

Three baselines for experimental evaluation:
  - Baseline A: Naive LLM
  - Baseline B: Coding Agent + Tool Registry
  - Baseline C: SPS-CA (Full framework)

Created in Phase 9.
"""

__version__ = "0.1.0"
EOF

cat > sandbox/__init__.py << 'EOF'
"""
SPS-CA Sandbox: Isolated Execution Environment

Provides safe execution for testing code modifications.
Used by Layer 6 (Validation & V&V).
"""

__version__ = "0.1.0"
EOF

echo "  ✅ Package __init__.py files created"
echo ""

# Step 8: Create .gitkeep files to preserve empty directories
echo "✓ Step 8: Creating .gitkeep files for empty directories..."

touch core/tests/.gitkeep
touch governance/decisions/.gitkeep
touch experience/logs/.gitkeep
touch evaluation/scenarios/.gitkeep
touch evaluation/sandbox/.gitkeep
touch evaluation/regression/.gitkeep
touch evaluation/rollback/.gitkeep
touch evaluation/checklists/.gitkeep
touch evaluation/metrics/.gitkeep
touch projects/.gitkeep
touch docs/.gitkeep

echo "  ✅ .gitkeep files created"
echo ""

# Step 9: Stage all files
echo "✓ Step 9: Staging files for git..."
git add -A
echo "  ✅ Files staged"
echo ""

# Step 10: Show what will be committed
echo "✓ Step 10: Files to be committed:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git diff --cached --name-status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 11: Commit
echo "✓ Step 11: Creating git commit..."
git commit -m "PHASE 0: Initial project setup and directory structure

- Added requirements.txt with all dependencies
- Added setup.py for package configuration
- Added comprehensive README.md with setup instructions
- Added .gitignore for Python and SPS-CA files
- Added Dockerfile for reproducible execution
- Created directory structure for all 10 layers
- Added package __init__.py files
- Added PHASE_0_SETUP_CHECKLIST.md with detailed steps
- Added QUICK_REFERENCE.md for project overview

Status: Phase 0 infrastructure ready for development
Timeline: 18-20 weeks (Phases 1-10) + evaluation + thesis
Budget: \$0 (zero-cost open-source stack)"

echo "  ✅ Commit created"
echo ""

# Step 12: Check remote
echo "✓ Step 12: Checking GitHub remote..."
REMOTE_URL=$(git config --get remote.origin.url)
echo "  Remote URL: $REMOTE_URL"
echo ""

# Step 13: Push to GitHub
echo "✓ Step 13: Pushing to GitHub..."
echo "  📤 Pushing to main branch..."

if git push origin main; then
    echo "  ✅ Successfully pushed to GitHub!"
else
    echo "  ⚠️  Push may have failed. Trying with -u flag..."
    git push -u origin main
    echo "  ✅ Pushed successfully!"
fi

echo ""

# Step 14: Create phase tag
echo "✓ Step 14: Creating phase completion tag..."
git tag -a phase-0-complete -m "PHASE 0: Project setup complete

All infrastructure files committed:
- Python dependencies (requirements.txt)
- Package configuration (setup.py)
- Project documentation (README.md)
- Git configuration (.gitignore, Dockerfile)
- Directory structure with __init__.py files
- Setup checklists and quick reference guides

Ready for Phase 1: Layers 1-2 (Cognitive Core + DNA)

Timestamp: $(date)"

if git push origin phase-0-complete; then
    echo "  ✅ Phase tag created and pushed"
else
    echo "  ⚠️  Could not push tag, but it's created locally"
fi

echo ""

# Final summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ PHASE 0 SETUP COMPLETE & PUSHED TO GITHUB!               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Summary:"
echo "   ✅ Repository: $REPO_DIR"
echo "   ✅ Remote: $REMOTE_URL"
echo "   ✅ Branch: main"
echo "   ✅ Tag: phase-0-complete"
echo ""
echo "📝 Next Steps:"
echo "   1. Read the documentation:"
echo "      - QUICK_REFERENCE.md (overview)"
echo "      - README.md (setup guide)"
echo "      - PHASE_0_SETUP_CHECKLIST.md (detailed steps)"
echo ""
echo "   2. Install Python 3.11+:"
echo "      macOS: brew install python@3.11"
echo "      Linux: sudo apt-get install python3.11"
echo "      Windows: Download from python.org"
echo ""
echo "   3. Create Python virtual environment:"
echo "      python -m venv venv"
echo "      source venv/bin/activate  # or: venv\\Scripts\\activate (Windows)"
echo ""
echo "   4. Install dependencies:"
echo "      pip install -r requirements.txt"
echo ""
echo "   5. Install & configure Ollama:"
echo "      Download: https://ollama.ai"
echo "      Run: ollama pull qwen2.5-coder:32b  (takes 1-2 hours)"
echo "      Start: ollama serve (keep running in background)"
echo ""
echo "   6. Verify installation:"
echo "      pytest --version"
echo "      python -c 'import tree_sitter; print(\"OK\")'"
echo "      curl http://localhost:11434/api/tags"
echo ""
echo "📞 Once setup is complete, reply:"
echo "   'PHASE 0 COMPLETE - Ready for Phase 1'"
echo ""
echo "Then I'll generate Phase 1 code (Layers 1-2) immediately!"
echo ""
