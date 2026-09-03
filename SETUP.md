# SPS-CA Setup Guide

## Local / Google Colab

Clone the repository and install the dependencies. The default Brain provider is Ollama, with model selection resolved from the models currently installed on the connected Ollama server.

### Google Colab

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

Start the web application:

```bash
!python ui/web_app.py
```

### Local Windows

```powershell
git clone https://github.com/muhammadnaumantahir/SPS_CA.git
cd SPS_CA
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install Ollama, then verify and pull a coding model:

```powershell
ollama list
ollama pull qwen2.5-coder:7b
ollama serve
```

In a second terminal:

```powershell
cd SPS_CA
.venv\Scripts\activate
python ui/web_app.py
```

Open `http://127.0.0.1:8080`.

### Local Linux / macOS

```bash
git clone https://github.com/muhammadnaumantahir/SPS_CA.git
cd SPS_CA
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
ollama pull qwen2.5-coder:7b
ollama serve
python ui/web_app.py
```

## What the browser workspace provides

- Chat-first prompt and source-code workspace
- Automatic language detection
- Intent-safe capability routing
- Working code view
- Live request activity indicator while local inference is running
- Saved conversations
- Structured trace for completed turns
- Agree/Disagree feedback used as learning evidence
- Capability registry and provenance
- Evolution evidence and controlled self-programming visibility
- Ten-layer architecture view

The browser chat is a controlled preview boundary. It returns proposed source changes and capability results without silently mutating an arbitrary local project directory.

## CLI

```bash
python ui/cli_interface.py
```

The CLI exposes the same core assistant service for local use.

## Testing

The repository includes focused tests for the layers, capabilities, routing, learning, Evolution controls, evaluation harnesses, and UI/runtime boundaries.

Run the local suite with:

```bash
pytest -q
```

## Runtime configuration

Leave model selection empty to let Ollama resolve an installed model at request time. The provider refreshes model discovery when needed.

LLM generation has no default wall-clock cutoff. A specific caller can supply `timeout_seconds` when a bounded environment requires one.

Automatic Evolution remains deny-by-default. Explicitly enabled controlled environments can use the Evolution authority and action limits documented in `docs/SELF_PROGRAMMING.md`.

## Security

Do not place credentials, API keys, tokens, passwords, private source code, or production data in the repository. Public sharing of a local UI can expose submitted code and should be treated accordingly.

## Architecture

SPS-CA keeps the following ten layers stable:

1. Software DNA
2. Governance
3. Cognitive
4. Knowledge
5. Experience
6. Meta-Learning
7. Adaptation
8. Evolution
9. Verification & Validation
10. Execution

The Brain is a separate replaceable intelligence service. Capabilities are executable skills governed by the SPS control path.
