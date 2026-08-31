# SPS-CA Complete Setup Guide

## 1. Clone

```bash
git clone https://github.com/muhammadnaumantahir/SPS_CA.git
cd SPS_CA
```

## 2. Python

Install Python 3.11 or newer and verify:

```bash
python --version
```

## 3. Virtual environment

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

## 4. Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Ollama

Install Ollama from its official website, then verify:

```bash
ollama --version
ollama list
```

## 6. Local coding model

For a 16 GB RAM / Intel HD 620 / i7 7th Gen office machine, start with:

```bash
ollama pull qwen2.5-coder:7b
ollama run qwen2.5-coder:7b
```

Qwen2.5-Coder 7B and Qwen3-Coder are different models. Qwen3-Coder can be used later on stronger hardware.

## 7. Verify Ollama API

With Ollama running:

```bash
curl http://localhost:11434/api/tags
```

On Windows PowerShell, this also works:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

## 8. Verify SPS-CA

```bash
python -c "import tree_sitter, pytest, pydantic; print('dependencies OK')"
pytest -q
```

## 9. Runtime data

Do not place real user projects, chats, credentials, or generated runtime data in Git. Configure a separate runtime data root when those services are implemented.

## 10. Optional future providers

The architecture supports provider adapters for future Ollama/local and cloud providers. API keys must be supplied through environment variables or a secure secret mechanism and must never be committed.

## 11. Office/GitHub restriction

If GitHub is unavailable from an office machine, SPS-CA can still operate against local project folders and Ollama. GitHub synchronization can be performed from an authorized development machine.

## 12. Troubleshooting

- If `python` is not found, reinstall Python and enable PATH integration.
- If activation is blocked in PowerShell, use the appropriate execution-policy setting approved by your organization or use Command Prompt.
- If Ollama cannot find the model, run `ollama list` and pull the model again.
- If dependencies fail, verify Python is 3.11+ and that `.venv` is active.

For architecture and research design, see `docs/architecture/SPS_CA_ARCHITECTURE_V2.md` and the documents under `docs/`.
