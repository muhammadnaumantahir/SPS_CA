# Development Guide

## Repository conventions

SPS-CA is maintained as one coherent implementation. Documentation describes the current architecture and behavior; abandoned design notes and completed implementation plans do not belong in the product surface.

Use descriptive filenames. Benchmark size is configuration/data, not a filename naming convention. Keep the ten SPS layers and the separate Brain boundary explicit.

## Environment requirements

- Python 3.11+
- Git and pip
- Ollama for local LLM inference
- pytest for testing
- 16 GB RAM is recommended for the local prototype
- A dedicated GPU is optional; CPU inference is supported by Ollama-compatible models, with lower throughput

For a modest 16 GB RAM office machine, `qwen2.5-coder:7b` is the intended starting model:

```bash
ollama pull qwen2.5-coder:7b
```

Larger models can be introduced through the provider abstraction without changing the SPS architecture.

Runtime data such as projects, sessions, conversations, memories, traces, model caches and generated artifacts should use a configurable data root outside the Git-controlled source tree whenever practical. Never commit API keys, tokens, passwords or credentials.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```text
.venv\Scripts\activate
```

Configure the Brain provider/model using the files under `models/`.

## Tests

Run the complete suite:

```bash
pytest -q
```

Run targeted capability or layer tests by path when debugging. Scenario and evaluation assets live below `evaluation/` and `testing/`.

The machine-readable layer vocabulary is `layers/architecture.py` and is covered by `layers/tests/test_architecture_manifest.py`.

## Safe capability changes

Capability implementations must preserve the `CapabilityContext` / `CapabilityResult` contract, keep intent boundaries explicit, and include verification coverage. Changes that modify files or execute code must pass the applicable Governance, Verification & Validation, and Execution boundaries.

## Repository hygiene checks

Before committing maintenance changes, inspect for duplicate capability identifiers, stale path references, obsolete architecture/history filenames, and files that contain only plans or placeholders. Useful checks include:

```bash
grep -R "cap_[0-9][0-9][0-9]_" capabilities --exclude-dir=.git
find . -name '*1000*' -o -name '*phase*'
```

Numeric capability identifiers are expected only in canonical registry/seed paths; benchmark counts should remain configuration/data concerns.

## Evaluation

Growth evaluation uses descriptive scripts:

```bash
python scripts/generate_growth_scenarios.py
python scripts/evaluate_growth_scenarios.py
```

The current dataset contains 1000 scenarios: 490 routing cases, 500 evolution-strategy cases, and 10 executable lifecycle proof cases. The number is an evaluation parameter, not an architectural concept.

## Documentation source of truth

- `README.md` — project overview, canonical flows, capabilities, and entry points
- `docs/ARCHITECTURE.md` — ten-layer architecture and Brain boundary
- `docs/PIPELINE.md` — runtime sequencing and SPS Growth Decision
- `docs/CAPABILITIES.md` — registry, lifecycle, and capability naming rules
- `docs/DEVELOPMENT.md` — environment, setup, testing, and repository conventions
- `docs/TROUBLESHOOTING.md` — local/Colab troubleshooting
