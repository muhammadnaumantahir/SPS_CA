# SPS-CA Phase 1 — Controlled Self-Programming

Phase 1 turns Layer 08 (Evolution) into a bounded self-repair mechanism while keeping the existing ten SPS layer names and responsibilities unchanged.

## The ten layers remain

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

The Brain remains a separate intelligence service.

## Closed-loop self-programming

```text
Failure observed
    ↓
Failure diagnosis
    ↓
Regression case recorded
    ↓
Minimal repair candidate generated
    ↓
Software DNA safety proof
    ↓
Governance decision
    ↓
Verification & Validation through test command
    ↓
Execution snapshot
    ↓
Apply candidate
    ↓
PASS → promote / keep change
FAIL → rollback
    ↓
Regression evidence updated
```

## What Phase 1 can repair

The repair engine may target explicitly diagnosed text/code files such as Python, Markdown, JSON, YAML, TOML, CSS, JavaScript, or TypeScript. The diagnosis supplies the allowed file scope; a candidate that changes any other file is rejected.

## Protected surfaces

Autonomous self-repair cannot edit:

- `governance/`
- `layers/layer_01_software_dna/`
- `layers/layer_02_governance/`
- `experience/logs/`
- `experience/traces/`
- `runtime/`

These surfaces remain outside the self-repair mutation boundary so the rules, governance decisions, historical evidence, and runtime state cannot be rewritten by the repair candidate itself.

## Mutation limits

- Maximum repair attempts per failure: 3
- Maximum files per candidate: 5
- Candidate files must remain inside the repository
- Python candidates must compile before execution
- Markdown changes must preserve the documented Software DNA / ten-layer architecture
- Layer 10 owns snapshots and rollback
- Failed execution is never promoted

## Regression memory

Each failure receives a `REG-*` case in `experience/regressions/self_programming_regressions.json`. The record stores the failure category, affected files, hypotheses, tests, and attempt outcomes. Raw source is not copied into this ledger.

A repaired failure changes from `open` to `resolved`. A rollback failure marks the case `blocked` so future work cannot silently treat it as fixed.

## Controlled governance

A self-repair is not allowed to jump directly from model output to source mutation. The candidate must pass Layer 1's mechanical DNA proof and Layer 2 Governance before Layer 10 is allowed to execute it. Medium/high-risk changes can therefore stop at human review.

## Scope of Phase 1

Phase 1 provides the self-programming transaction and safety boundary. Later phases can add stronger diagnosis, autonomous regression-test synthesis, behavioral scoring, version competition, capability retirement, and continuous optimization without changing the ten layer names.
