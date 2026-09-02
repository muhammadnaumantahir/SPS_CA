# SPS SPS-CA Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect SPS-CA-facing prompt+code scenarios to SPS task analysis and capability selection while preserving the existing ten-layer framework and preparing the path for generated capabilities.

**Architecture:** Keep the existing ten layers and their names unchanged. Layer 3 remains Experience and persists scenario history; Layer 2 remains Cognitive Core and owns task/code analysis and candidate selection; Layer 8 remains Evolution and owns capability-gap planning/generation; Layer 9 remains Capability Registry and owns discovery/reuse; Layers 6/7/10 continue validation, governance, and execution.

**Tech Stack:** Python 3.11+, existing SPS-CA modules, pytest, JSON persistence, existing provider-neutral model interface with Ollama/Qwen for later model-backed analysis.

**Spec:** SPS-CA requirements: chat prompt + code/file input, analyze prompt+code, modify code, use existing capabilities, develop a missing capability, store WHY/WHAT/WHEN/HOW/evolution trace in JSON, and defer web UI.

## Global Constraints

- Preserve exactly 10 SPS layers and all existing layer names.
- Do not replace the existing Layer 8 Evolution Engine or Layer 9 Capability Registry; extend them.
- Keep web UI deferred until the core SPS-CA loop is demonstrated.
- Keep runtime/research artifacts outside source-control-sensitive user data unless explicitly intended as research fixtures.
- Every production behavior change must be covered by a failing test first, then implementation.

---

### Task 1: Connect submitted scenarios to Cognitive Core analysis

**Files:**
- Modify: `ui/cli_interface.py`
- Test: `ui/tests/test_cli_interface.py`

**Interfaces:**
- Consumes: `SPS_CA_Interface.submit_submission(user_request, code, language, file_path="")`
- Produces: a scenario trace populated with an `analysis` section containing task intent, language, code presence, and target information before capability selection.

- [ ] **Step 1: Write the failing test**

```python

def test_submission_runs_task_and_code_analysis(tmp_path):
    ui = SPS_CA_Interface(
        history_path=tmp_path / "history.json",
        trace_history_path=tmp_path / "evolution_history.json",
        trace_stage_path=tmp_path / "stage.json",
    )

    response = ui.submit_submission(
        "Add input validation before calculation",
        "def calculate(age):\n    return age + 10\n",
        "python",
        file_path="example.py",
    )

    assert "SC-001" in response
    record = ui.trace_store.list_records()[0]
    assert record["analysis"]["user_intent"] == "Add input validation before calculation"
    assert record["analysis"]["language"] == "python"
    assert record["analysis"]["code_present"] is True
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
python -m pytest ui/tests/test_cli_interface.py::test_submission_runs_task_and_code_analysis -q
```
Expected: FAIL because `submit_submission()` currently only records intake and does not populate `analysis`.

- [ ] **Step 3: Write minimal implementation**

Update `submit_submission()` so that after `start_scenario()` it calls the existing Cognitive Core request/task decomposition interfaces, then completes the scenario's `analysis` section with deterministic fields:

```python
analysis = {
    "user_intent": user_request,
    "language": language,
    "code_present": bool(code.strip()),
    "file_path": file_path,
}
self.trace_store.complete_scenario(
    scenario["scenario_id"],
    status="analyzed",
    analysis=analysis,
)
```

Keep this deterministic in Step 1; model-backed semantic analysis is introduced only after the trace contract is proven.

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
python -m pytest ui/tests/test_cli_interface.py::test_submission_runs_task_and_code_analysis -q
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add ui/tests/test_cli_interface.py ui/cli_interface.py
git commit -m "feat: analyze submitted SPS scenario"
```

---

### Task 2: Search Layer 9 capabilities from the submitted scenario

**Files:**
- Modify: `ui/cli_interface.py`
- Test: `ui/tests/test_cli_interface.py`

**Interfaces:**
- Consumes: analyzed scenario + `CapabilityRegistryManager.search_capabilities()` / existing Cognitive Core candidate selection.
- Produces: `capability_search` trace with requested behavior, candidate ids, selected capability, and whether a suitable capability was found.

- [ ] **Step 1: Write the failing test**

```python

def test_submission_records_capability_search(tmp_path):
    ui = SPS_CA_Interface(
        history_path=tmp_path / "history.json",
        trace_history_path=tmp_path / "evolution_history.json",
        trace_stage_path=tmp_path / "stage.json",
    )

    ui.submit_submission(
        "Add exception handling",
        "def divide(a, b):\n    return a / b\n",
        "python",
    )

    record = ui.trace_store.list_records()[0]
    assert "capability_ids" in record["capability_search"]
    assert "selected" in record["capability_search"]
    assert isinstance(record["capability_search"]["found"], bool)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
python -m pytest ui/tests/test_cli_interface.py::test_submission_records_capability_search -q
```
Expected: FAIL because capability lookup is not yet attached to the submission trace.

- [ ] **Step 3: Write minimal implementation**

Use the existing Cognitive Core candidate selection already used by `process_request()`, and record the decision without yet modifying user code:

```python
analysis_obj = self.core.analyze_target_project_from_code(code, language) if hasattr(...) else None
candidate_ids = [cap.id for cap in self.registry.search_capabilities(user_request)]
selected = candidate_ids[0] if candidate_ids else None
search_data = {
    "query": user_request,
    "capability_ids": candidate_ids,
    "selected": selected,
    "found": selected is not None,
}
```

Use only existing repository interfaces that are verified in the implementation; do not add a speculative method. If the current Core requires a project path, keep Step 2 scoped to registry search and record the limitation explicitly in `analysis`.

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
python -m pytest ui/tests/test_cli_interface.py::test_submission_records_capability_search -q
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add ui/tests/test_cli_interface.py ui/cli_interface.py
git commit -m "feat: trace SPS capability selection"
```

---

### Task 3: Integrate capability-gap planning from Layer 8

**Files:**
- Modify: `ui/cli_interface.py`
- Modify: `layers/layer_08_evolution/gap_planner.py`
- Test: `testing/test_missing_capability_evolution.py`

**Interfaces:**
- Consumes: capability search result with no suitable match.
- Produces: `CapabilityPlan` with research provenance and a populated `capability_generation` trace section.

- [ ] **Step 1: Write the failing test**

```python

def test_missing_capability_is_planned_from_submission_gap(tmp_path):
    ui = SPS_CA_Interface(
        history_path=tmp_path / "history.json",
        trace_history_path=tmp_path / "evolution_history.json",
        trace_stage_path=tmp_path / "stage.json",
    )

    ui.submit_submission(
        "Parameterize SQL queries",
        "cursor.execute(f\"select * from users where id={user_id}\")",
        "python",
    )

    record = ui.trace_store.list_records()[0]
    assert record["capability_generation"]["required"] is True
    assert record["capability_generation"]["provenance"]["trigger"] == "capability_gap"
    assert record["capability_generation"]["provenance"]["why"]
    assert record["capability_generation"]["capability_id"].startswith("CAP-")
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
python -m pytest testing/test_missing_capability_evolution.py::test_missing_capability_is_planned_from_submission_gap -q
```
Expected: FAIL because the submission path does not yet invoke Layer 8 for an immediate capability gap.

- [ ] **Step 3: Write minimal implementation**

Instantiate the existing `CapabilityGapPlanner` from Layer 8 and only plan, not yet generate executable code:

```python
planner = CapabilityGapPlanner()
plan = planner.plan(
    task_description=user_request,
    language=language,
    reason="No suitable registered capability was found for this request.",
    task_id=scenario["scenario_id"],
)
self.trace_store.complete_scenario(
    scenario["scenario_id"],
    status="capability_planned",
    capability_generation={
        "required": True,
        "capability_id": plan.capability_id,
        "provenance": plan.provenance,
    },
)
```

Do not modify layer names or move this responsibility outside Layer 8.

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
python -m pytest testing/test_missing_capability_evolution.py::test_missing_capability_is_planned_from_submission_gap -q
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add ui/cli_interface.py layers/layer_08_evolution/gap_planner.py testing/test_missing_capability_evolution.py
git commit -m "feat: route capability gaps into layer 8 evolution"
```

---

### Task 4: Run the SPS-CA-loop integration test

**Files:**
- Test: `testing/test_SPS-CA_loop.py`

**Interfaces:**
- Consumes: CLI submission, Layer 2 analysis, Layer 8 gap planning, trace store.
- Produces: one end-to-end research record showing Stage 0 intake → analysis → capability search → gap decision/planning.

- [ ] **Step 1: Write the failing test**

```python

def test_SPS-CA_loop_records_stage_zero_to_capability_decision(tmp_path):
    ui = SPS_CA_Interface(
        history_path=tmp_path / "history.json",
        trace_history_path=tmp_path / "evolution_history.json",
        trace_stage_path=tmp_path / "stage.json",
    )

    ui.submit_submission(
        "Add input validation to this function",
        "def calculate(age):\n    return age + 10\n",
        "python",
        file_path="app.py",
    )

    record = ui.trace_store.list_records()[0]
    assert record["stage_before"] == 0
    assert record["user_request"] == "Add input validation to this function"
    assert record["analysis"]
    assert record["capability_search"]
    assert "required" in record["capability_generation"]
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
python -m pytest testing/test_SPS-CA_loop.py::test_SPS-CA_loop_records_stage_zero_to_capability_decision -q
```
Expected: FAIL until Tasks 1–3 are integrated.

- [ ] **Step 3: Write minimal integration implementation**

Reuse the Task 1–3 functions. Do not introduce a duplicate orchestration layer outside the existing Layer 2/Layer 8 boundaries.

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
python -m pytest testing/test_SPS-CA_loop.py::test_SPS-CA_loop_records_stage_zero_to_capability_decision -q
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add testing/test_SPS-CA_loop.py

git commit -m "test: verify SPS-CA-driven SPS loop"
```

---

### Task 5: Verify CI and update the PR status

**Files:**
- Modify: none unless CI exposes a defect

**Interfaces:**
- Consumes: branch commits from Tasks 1–4.
- Produces: verified branch and updated PR description/status.

- [ ] **Step 1: Run targeted local-equivalent checks available in CI**

Run:
```bash
python -m pytest ui/tests/test_cli_interface.py testing/test_missing_capability_evolution.py testing/test_SPS-CA_loop.py -q
```
Expected: all targeted tests PASS.

- [ ] **Step 2: Run broader suite**

Run:
```bash
python -m pytest -q
```
Expected: no new failures relative to the repository baseline.

- [ ] **Step 3: Check GitHub Actions**

Verify the branch workflows complete successfully. Do not claim success until the workflow conclusion is `success`.

- [ ] **Step 4: Commit any verified CI-only fixes**

Use a focused commit message such as:
```bash
git commit -m "test: stabilize SPS-CA loop verification"
```

---

## Requirement Coverage After This Plan

SPS-CA requirements addressed by this plan:

- User prompt + code/file intake: existing Step 1 foundation plus this plan's analysis connection.
- Prompt + code analysis: Task 1.
- Capability selection/use decision: Task 2.
- Missing-capability detection and Layer 8 planning: Task 3.
- Stage/evolution trace with WHY/WHAT/WHEN/HOW provenance: existing trace foundation plus Tasks 2–3.
- Actual capability generation, validation, registration, execution, and code modification: next implementation cycle after Tasks 1–5; these are intentionally not faked by this plan.
- Web UI: deferred.
