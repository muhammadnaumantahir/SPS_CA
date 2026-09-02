# SPS-CA Complete Setup Guide

## Local / Google Colab

Clone the repository and install the existing dependencies as described below. The default AI Brain provider is Ollama and the default model is `qwen2.5-coder:7b`.

### Fresh Colab runtime

```bash
!git clone https://github.com/muhammadnaumantahir/SPS_CA.git
%cd SPS_CA
!bash scripts/colab_setup.sh
```

Verify Ollama:

```bash
!ollama list
!curl -s http://127.0.0.1:11434/api/tags
```

Run tests:

```bash
!bash scripts/run_tests.sh
```

## Local Windows setup

### 1. Clone

```bash
git clone https://github.com/muhammadnaumantahir/SPS_CA.git
cd SPS_CA
```

### 2. Python

Install Python 3.11 or newer, then create/activate a virtual environment:

```bash
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Ollama Brain

Install Ollama, then verify:

```bash
ollama --version
ollama list
ollama pull qwen2.5-coder:7b
```

The model provider is intentionally separate from SPS capabilities. The Brain can be switched to another provider later through `models/` without turning that provider into a capability.

### 4. Verify

```bash
python -c "import tree_sitter, pytest, pydantic; print('dependencies OK')"
pytest -q
```

## Run SPS-CA

### Advanced web dashboard

```bash
python ui/web_app.py
```

Open `http://127.0.0.1:8080` in a browser.

The dashboard provides:
- prompt and source-code workspace;
- separate Brain panel with provider/model status;
- live ten-layer architecture visualization;
- Brain reasoning and ordered capability plan;
- capability execution results;
- modified code and unified diff;
- complete JSON trace for research/evaluation;
- explicit separation of Brain, layers and capabilities.

The web dashboard's code mode is a controlled **preview** boundary. It does not silently mutate a user's local filesystem. Real project mutation remains under the Execution layer.

### CLI

```bash
python ui/cli_interface.py
```

Commands include `load`, `show project`, `show architecture`, `show registry`, `show brain`, `show experience`, `help`, and `quit`.

## Runtime data and security

Do not place real user projects, chats, credentials, or generated runtime data in Git. Never commit API keys, tokens or passwords. The Brain provider is configurable and should be supplied through runtime configuration/environment where applicable.

## Architecture reference

See `docs/ARCHITECTURE.md` for the canonical ten-layer model. The public architecture is:

1. Software DNA layer
2. Governance layer
3. Cognitive core
4. Knowledge core
5. Experience core
6. Meta-learning core
7. Adaptation core
8. Evolution core
9. Verification & Validation
10. Execution layer

**Brain:** separate AI intelligence service used by the Cognitive core and other controlled SPS processes.

**Capabilities:** separate executable skills registered/versioned independently of the Brain.
