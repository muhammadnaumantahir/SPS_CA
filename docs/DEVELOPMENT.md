# Development Guide

## Repository conventions

SPS-CA is maintained as one coherent implementation. Documentation should describe the current architecture and behavior; design notes and completed implementation plans do not belong in the product documentation tree.

Use descriptive filenames. Benchmark size is a configuration/data property, not a filename naming convention.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the virtual environment with `.venv\\Scripts\\activate`.

Configure the Brain provider/model according to the files under `models/`.

## Tests

Run the complete suite:

```bash
pytest -q
```

Run targeted capability tests or layer tests by path when debugging a change. Scenario/evaluation assets live below `evaluation/` and `testing/`.

## Safe capability changes

A capability change should preserve its `CapabilityContext`/`CapabilityResult` contract, keep intent boundaries explicit, and include verification coverage. Changes that can modify files or execute code must pass the applicable Governance and Verification gates.

## Naming and cleanup checks

Before committing repository maintenance changes, inspect for:

```bash
grep -R "cap_[0-9][0-9][0-9]_" capabilities --exclude-dir=.git
find . -name '*1000*' -o -name '*phase*'
```

The first command should only report deliberately retained canonical identifiers or historical references where justified. The second should not reveal obsolete architecture/history filenames.

## Evaluation

The growth benchmark uses configurable scenario generation and evaluation scripts:

```bash
python scripts/generate_growth_scenarios.py
python scripts/evaluate_growth_scenarios.py
```

The current dataset contains 1000 cases, but the implementation should not depend on that filename or count.
