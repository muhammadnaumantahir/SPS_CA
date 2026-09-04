# Persistent Execution Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist every Web UI/CLI/scenario execution as Layer 5 Experience and use that history plus explicit scenario evidence in the real Layer 8 growth decision path.

**Architecture:** Extend the existing Layer 5 Experience model/log and add an execution-memory sub-component. Integrate it at the shared execution boundary and pass evidence into Layer 8 without creating a new layer or changing any existing layer name. Scenario expected strategies remain assertions; scenario context becomes actual evidence input.

**Tech Stack:** Python, dataclasses, JSON persistence, pytest, existing SPS Layer 5/Layer 8 components.

**Spec:** `docs/superpowers/specs/2026-09-04-persistent-execution-experience-design.md`

## Global Constraints

- Do not rename, add, remove, or reorder the canonical ten SPS layers.
- The Brain remains outside the ten-layer count.
- New execution-memory code is a Layer 5 sub-component.
- Scenario and Web UI execution must share the same recording contract.
- Disagreement is evidence, not an automatic capability-creation command.
- Generated capabilities may be registered only after an explicit Layer 8 CREATE decision.

---

### Task 1: Lock the Layer 5 memory contract with tests

**Files:**
- Modify: `layers/layer_05_experience_core/models.py`
- Test: `layers/layer_05_experience_core/tests/test_experience_memory.py`

**Interfaces:**
- `Task` gains backward-compatible execution provenance fields.
- Tests define the persisted record contract and reload behavior.

- [ ] Step 1: Add failing tests for source/scenario/run/feedback provenance.
- [ ] Step 2: Run the focused Layer 5 tests and confirm the new tests fail for the missing fields/behavior.
- [ ] Step 3: Extend `Task` minimally and keep old constructors valid.
- [ ] Step 4: Run the focused tests and confirm green.
- [ ] Step 5: Commit the Layer 5 model change.

### Task 2: Add the persistent Layer 5 execution-memory sub-component

**Files:**
- Create: `layers/layer_05_experience_core/execution_memory.py`
- Modify: `layers/layer_05_experience_core/experience_log.py`
- Test: `layers/layer_05_experience_core/tests/test_experience_memory.py`

**Interfaces:**
- `ExecutionExperienceStore.record_execution(...) -> Task`
- `ExecutionExperienceStore.load() -> ExperienceLog`
- `ExecutionExperienceStore.find_relevant(...) -> list[Task]`

- [ ] Step 1: Add failing tests for record, persistence, and relevant-history retrieval.
- [ ] Step 2: Run focused tests and verify red.
- [ ] Step 3: Implement the smallest append-only store using existing `ExperienceLog` persistence.
- [ ] Step 4: Run focused tests and verify green.
- [ ] Step 5: Commit the Layer 5 memory sub-component.

### Task 3: Feed persistent experience into Layer 8 reasoning and protect CREATE

**Files:**
- Modify: `layers/layer_08_evolution_core/evolution_evidence.py`
- Modify: `layers/layer_08_evolution_core/growth_decision.py` only where evidence/default handling requires it
- Test: `layers/layer_08_evolution_core/tests/test_evolution_evidence.py`

**Interfaces:**
- `record_disagreement(...)` accepts optional scored evidence.
- `analyze(...)` uses explicit evidence and historical observations without forcing CREATE by count alone.
- `record_creation(analysis)` raises when `analysis["decision"] != "create"`.

- [ ] Step 1: Add a failing test proving non-CREATE analyses cannot register capabilities.
- [ ] Step 2: Add a failing test for a genuine evidence-backed CREATE decision.
- [ ] Step 3: Run focused Layer 8 tests and verify red.
- [ ] Step 4: Add the explicit CREATE gate and evidence plumbing.
- [ ] Step 5: Run focused tests and verify green.
- [ ] Step 6: Commit Layer 8 changes.

### Task 4: Unify Web UI/CLI/scenario execution memory

**Files:**
- Modify: `ui/sps_execution.py`
- Modify: `ui/sps_service.py` only where historical experience must enter analysis
- Modify: `ui/web_app.py` where feedback is recorded
- Modify: `evaluation/scenario_runner.py`
- Test: existing relevant UI/evaluation tests plus focused new tests

**Interfaces:**
- Both sources call `ExecutionExperienceStore.record_execution(...)`.
- Scenario runner passes `context.evidence` and expected strategy evidence into the same evolution analysis path.
- Web feedback updates the same durable Experience history.

- [ ] Step 1: Add failing integration tests for Web-style execution and scenario execution persistence.
- [ ] Step 2: Add failing test proving a repeated historical failure lowers reuse fitness / raises gap evidence.
- [ ] Step 3: Run focused tests and verify red.
- [ ] Step 4: Wire the common store into execution boundaries.
- [ ] Step 5: Wire scenario evidence into Layer 8 without treating expected strategy as a command.
- [ ] Step 6: Run focused tests and verify green.
- [ ] Step 7: Commit the integration.

### Task 5: Make the 1000-scenario benchmark prove memory + genuine evolution

**Files:**
- Modify: `evaluation/scenarios/growth.json` only if evidence fields need schema completion
- Modify: `testing/test_sps_scenarios.py`
- Modify: `scripts/generate_growth_scenarios.py` if generator output must carry executable evidence
- Modify: `notebooks/sps_ca_evolution_benchmark.ipynb` only for concise proof/inspection cells

**Interfaces:**
- 490 routing cases remain routing cases.
- 500 autonomous-evolution cases become executable evidence cases.
- 10 lifecycle proof cases assert explicit CREATE provenance and reuse.

- [ ] Step 1: Add failing assertions that scenario execution actually records experience and can reach its expected strategy when evidence warrants it.
- [ ] Step 2: Run the targeted scenario test and verify red.
- [ ] Step 3: Wire real evidence into scenario execution.
- [ ] Step 4: Run the targeted scenario tests and verify green.
- [ ] Step 5: Run the complete 1000-case suite and inspect generated-capability counts and experience counts.
- [ ] Step 6: Update the Colab proof cell to show memory history + growth lineage.
- [ ] Step 7: Commit benchmark/notebook updates.

### Task 6: Verification and repository consistency

**Files:**
- Relevant changed files only

- [ ] Step 1: Run focused Layer 5, Layer 8, UI and scenario tests in CI.
- [ ] Step 2: Run the full repository test workflow.
- [ ] Step 3: Verify no canonical layer names changed.
- [ ] Step 4: Verify `growth.json` remains exactly 1000 cases.
- [ ] Step 5: Verify false-positive `record_creation()` is impossible.
- [ ] Step 6: Verify execution experience survives a fresh process/load.
- [ ] Step 7: Verify main contains the final green commits.
