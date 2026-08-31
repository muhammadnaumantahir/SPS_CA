# SPS-CA Requirements

## System requirements

### Minimum prototype environment

- Python 3.11+
- 16 GB RAM recommended for the initial local prototype
- Modern multi-core CPU
- At least 30 GB free disk space for the initial software/model setup; more is recommended for projects, models and runtime data
- Git
- Windows, Linux or macOS

### GPU

A dedicated GPU is optional for the initial prototype. On systems without a suitable GPU, Ollama can run supported models using CPU/system memory, although generation may be slower.

## Software requirements

- Python 3.11+
- pip
- Ollama for local LLM inference
- Git
- pytest for testing

Python's standard-library SQLite support does not need a separate `sqlite3` pip package.

## Initial model

For the current 16 GB RAM / Intel HD 620 / i7 7th Gen office machine:

```text
qwen2.5-coder:7b
```

Install with:

```bash
ollama pull qwen2.5-coder:7b
```

Qwen3-Coder is a separate, larger coding model and is a future option for stronger hardware.

## Python dependencies

The authoritative package list is `requirements.txt`. Do not duplicate the dependency list here; this document describes requirements and compatibility rather than pinning package versions.

## Future provider requirements

The model architecture is provider-neutral. Future adapters may support cloud APIs such as OpenAI or Anthropic and additional local providers. Those integrations require their respective credentials/configuration.

**Never commit API keys, tokens, passwords, or other secrets to the repository.**

## Runtime storage requirements

User projects, source code, conversations, sessions, memories, experiences, traces, model caches and generated capability artifacts are runtime data. They should use a configurable data root outside Git-controlled source whenever practical.

## Research requirements

The prototype should support reproducible comparison between:

1. Naive LLM coding baseline
2. Conventional tool-augmented coding agent baseline
3. SPS-CA with experience, adaptation, governance, validation and capability evolution

Evaluation should capture task outcomes, failures, capability reuse, validation, rollback, evolution and lineage metrics.