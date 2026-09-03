# SPS-CA

SPS-CA (Self-Programming System – Coding Assistant) is a coding system prototype built around a canonical ten-layer SPS architecture and a separate, replaceable Brain boundary.

## What makes SPS-CA different

A normal coding assistant can map a prompt directly to a tool or capability. SPS-CA records evidence, reasons about the task, evaluates existing capability fitness, and makes an explicit growth decision before evolution.

A disagreement is evidence, not an automatic capability-creation command.

## Canonical architecture

```text
                         USER
                          │
                 Prompt + Code/File
                          │
                          ▼
               CanonicalSPSPipeline
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
      SPS Architecture          Brain boundary
             │                         │
             ├─ L1 Software DNA       │
             ├─ L2 Governance         │
             ├─ L3 Cognitive ◄──────── Brain
             ├─ L4 Knowledge          │
             ├─ L5 Experience         │
             ├─ L6 Meta-Learning      │
             ├─ L7 Adaptation         │
             ├─ L8 Evolution ──► Capability
             │                 reuse/create
             ├─ L9 Verification
             └─ L10 Execution
                          │
                          ▼
                Result + Modified Code
                          │
                          ▼
                Experience / Trace / Evidence
                          │
                          ▼
                     Future Evolution
```

The authoritative layer manifest is `layers/architecture.py`. The Brain is deliberately outside the ten-layer count and is not a capability.

## SPS Growth Decision

```text
                 SPS Growth Decision
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
        Reuse          Adapt          Evolve
          │              │              │
          │              │       ┌──────┼──────┐
          │              │       ▼      ▼      ▼
          │              │    Improve Compose Create
```

The full reasoning path is:

```text
Disagreement / execution evidence
        ↓
Experience
        ↓
Meta-Learning
        ↓
Brain / Cognitive reasoning
        ↓
SPS Growth Decision
        ↓
reuse | adapt | improve | compose | create | defer
```

Creation happens only when evidence and governance justify a genuine capability gap.

## The ten layers

| Layer | Responsibility |
|---|---|
| L1 Software DNA | Contracts, invariants, capability shape, system identity |
| L2 Governance | Risk, authorization, policy, approval and rollback gates |
| L3 Cognitive | Reasoning, intent interpretation, planning and Brain integration |
| L4 Knowledge | Project facts, code context, snapshots and validation knowledge |
| L5 Experience | Execution outcomes, disagreements, traces and feedback evidence |
| L6 Meta-Learning | Capability evaluation, strategy selection and learning from evidence |
| L7 Adaptation | Environment-specific adaptation and controlled behavioral adjustment |
| L8 Evolution | Growth decision, capability evolution and governed self-programming |
| L9 Verification | Validation, testing, sandbox checks and evidence quality |
| L10 Execution | Authorized file changes, execution adapters and final delivery |

## Capability model

The repository has one canonical registry at `capabilities/registry.json`. Canonical capabilities are intent-oriented and are executed through `capabilities/canonical_runtime.py`.

The ten canonical capability IDs are:

`CAP-001` Code Generation, `CAP-002` Code Modification, `CAP-003` Code Explanation & Analysis, `CAP-004` Bug Detection & Diagnosis, `CAP-005` Bug Fixing, `CAP-006` Refactoring & Optimization, `CAP-007` Test Generation, `CAP-008` Documentation Generation, `CAP-009` Code Validation & Review, and `CAP-010` Project/File Operations.

Retired legacy implementations that remain useful for historical compatibility use semantic folder names rather than colliding numeric capability prefixes. Retired metadata is ignored by seed discovery.

Generated capabilities belong under `capabilities/generated/` and are registered only through the capability registry after verification and governance checks.

## Runtime lifecycle

```text
1. Receive prompt + optional code/file
2. Detect language and classify intent
3. Load Software DNA and governance constraints
4. Reason over request, project context and available capabilities
5. Select the safest viable capability strategy
6. Execute through the authorized execution path
7. Verify the result
8. Record outcome, trace and evidence
9. Reuse successful capability knowledge later
10. Escalate persistent gaps to SPS Growth Decision when justified
```

## Repository structure

```text
SPS_CA/
├── brain/                     # Separate reasoning/model boundary
├── capabilities/              # Canonical registry, runtime, seeds and generated capabilities
├── core/                      # Canonical pipeline and shared orchestration
├── layers/                    # The ten SPS layers
├── memory/                    # Persistent memory interfaces
├── models/                    # Model/provider configuration
├── governance/                # Governance support
├── experience/                # Experience and evidence handling
├── evaluation/                # Scenario data and evaluation assets
├── sandbox/                   # Controlled validation/execution boundary
├── runtime/                   # Runtime integration
├── ui/                        # Web/interaction layer
├── testing/                   # End-to-end and scenario tests
├── scripts/                   # Descriptive maintenance/evaluation utilities
├── notebooks/                 # Optional Colab/Jupyter entry points
└── docs/                      # Canonical project documentation
```

## Running SPS-CA

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Run the test suite:

```bash
pytest -q
```

Run the web UI using the repository's configured launcher:

```bash
python -m ui.web_app
```

The Brain provider is configured under `models/`. Ollama is the default provider; model selection is replaceable without changing the ten-layer architecture.

## Evidence and evaluation

The growth evaluation assets exercise capability routing and autonomous evolution strategies. The scenario count is a benchmark parameter, not an architectural layer or lifecycle phase. The current benchmark contains 490 routing cases, 500 evolution-strategy cases and 10 lifecycle proof cases.

Use:

```bash
python scripts/generate_growth_scenarios.py
python scripts/evaluate_growth_scenarios.py
```

The Colab notebook is `notebooks/sps_ca_evolution_benchmark.ipynb`.

## Documentation map

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — ten-layer architecture and Brain boundary
- [`docs/PIPELINE.md`](docs/PIPELINE.md) — canonical runtime sequencing and growth decision
- [`docs/CAPABILITIES.md`](docs/CAPABILITIES.md) — capability registry, lifecycle and naming rules
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — setup, testing and repository conventions
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) — common local/Colab runtime issues

## Design rules

SPS-CA is maintained as one coherent implementation. The repository does not use staged architecture plans, duplicate capability IDs, or historical planning documents as part of the product surface. Documentation describes the current system, not abandoned implementation timelines.
