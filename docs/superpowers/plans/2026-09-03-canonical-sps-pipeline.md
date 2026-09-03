# Canonical SPS Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the UI and model-backed scenario runner use the same canonical SPS execution path and expose the same ten-layer architecture and component trace.

**Architecture:** `SPSExecutionService.run_submission()` is the canonical execution entry point. `SPSScenarioService` supplies Cognitive/Brain analysis, Knowledge, Experience/Meta-Learning context, Adaptation, and Evolution/capability selection; `SPSExecutionService` performs controlled validation, governance, final Software DNA and Layer-10 execution. The UI consumes the canonical architecture manifest, and `scenario_runner.py` invokes the same service.

**Tech Stack:** Python, Gradio, pytest, JSON traces, Ollama-backed Brain, existing SPS layer services.

**Spec:** `docs/superpowers/specs/2026-09-03-canonical-sps-pipeline-design.md`

## Global Constraints

- Keep exactly ten SPS layers.
- Brain remains a replaceable supporting service, not a layer or capability.
- Do not auto-create a capability for a single disagreement; creation remains governed by Layer-8 evidence policy.
- Keep `main` unchanged; all work is on `fix/intent-mixed-growth-routing`.
- Preserve capability lineage and existing registry IDs.

---

### Task 1: Unify the scenario runner with the UI execution path

**Files:**
- Modify: `evaluation/scenario_runner.py`
- Test: `testing/test_sps_scenarios.py`

**Interfaces:**
- `run_suite(...) -> dict` continues to return run metrics and scenario records.
- Each scenario execution calls `SPSExecutionService.run_submission(...)`.

- [ ] **Step 1: Add a regression assertion for the canonical service path**

Verify the runner source imports `SPSExecutionService` and no longer constructs `SpsAssistantService` for the scenario execution loop.

- [ ] **Step 2: Run the scenario contract suite before the runner change**

Run: `pytest -q testing/test_sps_scenarios.py`

Expected: existing baseline result is recorded; this suite remains the deterministic 500-case contract.

- [ ] **Step 3: Replace the runner's service construction**

Use:

```python
service = SPSExecutionService(registry_path=REGISTRY_PATH)
turn = service.run_submission(
    user_request=request,
    code=str(scenario.get("code", "")),
    language=str(scenario.get("language", "python")),
    file_path=str(scenario.get("filename", "main.py")),
)
```

Map `turn["success"]`, `turn["capability_id"]`, `turn["modified_code"]`, and `turn["scenario_id"]` into the existing runner result shape.

- [ ] **Step 4: Keep feedback evaluation in the runner**

After the actual service result, run `_match_expected(...)`. Persist the scenario's declared `agree`/`disagree`; for `disagree`, call `EvolutionEvidenceStore.record_disagreement()` and then `analyze()`, and call `record_creation()` only when the decision is `create`.

- [ ] **Step 5: Run the runner smoke test**

Run: `python -m evaluation.scenario_runner --file evaluation/scenarios/growth_500.json --model qwen2.5-coder:7b --live-evolve --max-scenarios 1`

Expected: one scenario executes through the same service used by the UI and any failure prints a full traceback.

### Task 2: Make the canonical architecture manifest the only UI layer vocabulary

**Files:**
- Modify: `ui/web_ui.py`
- Test: `brain/tests/test_intent_routing.py`

**Interfaces:**
- UI layer display derives from `layers.architecture.architecture_manifest()`.

- [ ] **Step 1: Add a canonical UI layer helper**

Replace the hand-maintained `LAYERS` list with:

```python
from layers.architecture import architecture_manifest

LAYERS = architecture_manifest()["layers"]
```

- [ ] **Step 2: Update `_layer_html()`**

Render `number`, `name`, and `sub_components` from the canonical manifest.

- [ ] **Step 3: Run the focused UI import test**

Run: `python -c "from ui.web_ui import LAYERS; assert len(LAYERS) == 10"`

Expected: exit code 0.

### Task 3: Expose the actual SPS component trace in analysis results

**Files:**
- Modify: `ui/sps_service.py`
- Modify: `ui/sps_execution.py`
- Test: add `ui/tests/test_sps_pipeline.py`

**Interfaces:**
- `SPSAnalysisResult` gains `pipeline: dict[str, Any]`.
- `SPSExecutionService.run_submission()` returns `pipeline` and `brain` metadata.

- [ ] **Step 1: Write the failing pipeline trace test**

```python
from ui.sps_service import SPSAnalysisResult

def test_analysis_result_has_ten_layer_pipeline():
    result = SPSAnalysisResult(
        scenario_id="SC-TEST",
        stage=0,
        analysis={},
        capability_search={},
        capability_generation={},
        pipeline={"layers": [{"number": i} for i in range(1, 11)]},
    )
    assert len(result.pipeline["layers"]) == 10
```

- [ ] **Step 2: Extend `SPSAnalysisResult`**

Add `pipeline: Dict[str, Any]` and populate the canonical manifest plus a per-layer status/component summary.

- [ ] **Step 3: Populate real component evidence**

Use actual objects already involved in the path: `SoftwareDNA`, `GovernanceGate`, `CognitiveCore`, `KnowledgeCore`, `ExperienceLog`, `MetaLearner`, `Adaptation`, `EvolutionEngine`, `Validator`, and `ExecutionEngine`. Do not label a layer `completed` unless the corresponding operation actually ran; use `ready`, `in_progress`, `completed`, `blocked`, or `not_reached`.

- [ ] **Step 4: Attach Brain metadata to the Cognitive layer**

Expose provider/model/replaceable status from the Brain boundary. Keep Brain outside the ten-layer list.

- [ ] **Step 5: Run the pipeline test**

Run: `pytest -q ui/tests/test_sps_pipeline.py`

Expected: PASS.

### Task 4: Document the canonical user lifecycle

**Files:**
- Modify: `README.md`
- Modify: `docs/ARCHITECTURE.md`

- [ ] **Step 1: Add the canonical user-to-execution diagram**

Document prompt/code input, Brain reasoning, capability reuse/generation, validation, governance, DNA, execution, experience, and evolution evidence.

- [ ] **Step 2: Document the UI contract**

Explain exactly what the user sees: Brain model, selected/generated capability, ten-layer trace, validation/governance/DNA/execution state, modified code, and why/what/when/how trace.

- [ ] **Step 3: Document test semantics**

Clarify that the 500-case pytest suite is deterministic routing coverage, while `scenario_runner --live-evolve` is the model-backed ten-layer execution/evolution experiment.

### Task 5: Full verification

**Files:**
- No additional production files unless verification exposes a regression.

- [ ] **Step 1: Run focused tests**

Run: `pytest -q brain/tests/test_intent_routing.py brain/tests/test_multi_capability_routing.py ui/tests/test_sps_pipeline.py`

- [ ] **Step 2: Run the exact 500-case contract**

Run: `pytest -q testing/test_sps_scenarios.py`

Expected: 501 collected tests including the suite-size assertion.

- [ ] **Step 3: Run a one-scenario live-evolution smoke test with Ollama**

Run: `python -m evaluation.scenario_runner --file evaluation/scenarios/growth_500.json --model qwen2.5-coder:7b --live-evolve --max-scenarios 1`

- [ ] **Step 4: Commit the implementation**

```bash
git add evaluation/scenario_runner.py ui/web_ui.py ui/sps_service.py ui/sps_execution.py ui/tests/test_sps_pipeline.py README.md docs/ARCHITECTURE.md docs/superpowers/specs docs/superpowers/plans
git commit -m "feat: unify canonical SPS execution pipeline"
```
