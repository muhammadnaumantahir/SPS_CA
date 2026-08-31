# SPS-CA Complete Setup Guide

## Google Colab (recommended for the current prototype)

Colab is the easiest way to run SPS-CA when the development PC cannot comfortably store or run the selected local model.

### Fresh Colab runtime

Run these cells in order:

```bash
!git clone https://github.com/muhammadnaumantahir/SPS_CA.git
%cd SPS_CA
!bash scripts/colab_setup.sh
```

The default model is `qwen2.5-coder:7b`.

### Choose another model

Pass the Ollama model name as the script argument:

```bash
!bash scripts/colab_setup.sh qwen2.5-coder:7b
```

You can change the model later without changing SPS-CA code. Use a model that fits the GPU/RAM available in the current Colab runtime.

### Verify Ollama

```bash
!ollama list
!curl -s http://127.0.0.1:11434/api/tags
```

Test the model directly:

```bash
!ollama run qwen2.5-coder:7b "Write a Python hello-world program"
```

### Run tests

```bash
!bash scripts/run_tests.sh
```

### Run SPS-CA

The repository is currently an architecture foundation. After the application entry point is implemented, run it from the repository root. Until then, use the tests and layer modules as the verification entry points.

## Reusing the same Colab workflow after GitHub updates

For a new Colab runtime, always use:

```bash
!git clone https://github.com/muhammadnaumantahir/SPS_CA.git
%cd SPS_CA
!bash scripts/colab_setup.sh
```

For an existing cloned repository in the same runtime:

```bash
%cd /content/SPS_CA
!git pull origin main
!bash scripts/colab_setup.sh
```

It is safe to run the setup script after `git pull`. It reinstalls/updates Python dependencies, ensures Ollama is available, starts the local Ollama API, and pulls the selected model.

## Local Windows setup

### 1. Clone

```bash
git clone https://github.com/muhammadnaumantahir/SPS_CA.git
cd SPS_CA
```

### 2. Python

Install Python 3.11 or newer and verify:

```bash
python --version
```

### 3. Virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Ollama

Install Ollama from the official Ollama website, then verify:

```bash
ollama --version
ollama list
```

### 6. Local model

For a 16 GB RAM / Intel HD 620 / i7 7th Gen machine, start with:

```bash
ollama pull qwen2.5-coder:7b
```

Qwen2.5-Coder 7B and Qwen3-Coder are different models. Qwen3-Coder can be used on a stronger runtime.

### 7. Verify

```bash
python -c "import tree_sitter, pytest, pydantic; print('dependencies OK')"
pytest -q
```

## Runtime data and security

Do not place real user projects, chats, credentials, or generated runtime data in Git. Configure a separate runtime data root when those services are implemented. Never commit API keys, tokens or passwords.

## Troubleshooting

- If Python dependencies fail, verify Python is 3.11+ and that the intended environment is active.
- If Ollama is not found after installation, restart the terminal or runtime.
- If Ollama does not start in Colab, inspect `/tmp/ollama.log`.
- If a model is too large for the current Colab runtime, select a smaller model.
- If GitHub is unavailable from an office machine, use Colab for cloning and model execution.