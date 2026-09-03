# Canonical Ten-Capability Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the vague Stage 0 capability set with ten explicit, single-purpose canonical capabilities and harden Brain routing so code-generation requests cannot enter test generation.

**Architecture:** The ten canonical capabilities are the stable baseline (`CAP-001` through `CAP-010`). The Brain classifies the request before selecting capabilities and filters candidates by intent; test generation is eligible only for explicit test-generation intents. Existing historical seed implementations are migrated into the new capability directories, while generated/evolved capabilities move above the canonical ID range so the baseline remains stable.

**Tech Stack:** Python 3.11, pytest, existing SPS-CA Brain/LLM abstraction, existing capability registry and web/CLI orchestration.

**Spec:** `docs/superpowers/specs/2026-09-03-chat-ui-evolution-design.md` plus the approved canonical capability architecture in the user conversation.

## Global Constraints

- Brain remains separate from executable capabilities.
- The Brain infers programming language from prompt/code/filename; users do not manually select it.
- Capability selection must preserve the smallest set of capabilities that satisfies the user request.
- `CAP-007` Test Generation must never be selected for plain code creation/modification/explanation requests.
- Canonical capability IDs `CAP-001` through `CAP-010` are reserved for the initial baseline.
- Generated/evolved capabilities must use IDs above `CAP-010` and retain provenance/lineage.
- Runtime session/evolution state remains ignored and is not committed.

---

### Task 1: Add failing intent-routing regression tests

**Files:**
- Create: `core/tests/test_capability_intent_routing.py`
- Modify: `brain/tests/test_brain.py` only if shared Brain test helpers are required

**Interfaces:**
- Consumes: `Brain.plan(...)`, canonical capability catalog dictionaries, and the existing fake LLM provider pattern.
- Produces: Regression tests proving code-generation, modification, diagnosis, fixing, testing, explanation, refactoring, documentation and validation intents map to the intended capability IDs.

- [ ] **Step 1: Write the failing tests**

Add tests with a deterministic fake planner response and assert eligibility/selection semantics:

```python

def test_plain_code_creation_selects_code_generation_not_tests():
    plan = planner.plan(request="Write Python code to add, subtract, multiply and divide numbers.", code="", language="python", file_path="main.py")
    assert [step["capability_id"] for step in plan.steps] == ["CAP-001"]


def test_explicit_test_request_selects_test_generation():
    plan = planner.plan(request="Generate pytest tests for this function.", code="def add(a, b): return a + b", language="python", file_path="main.py")
    assert [step["capability_id"] for step in plan.steps] == ["CAP-007"]


def test_plain_code_creation_can_never_contain_cap_007():
    plan = planner.plan(request="Create a Python calculator program.", code="", language="python", file_path="main.py")
    assert "CAP-007" not in {step["capability_id"] for step in plan.steps}
```

Include equivalent assertions for explicit modification, explanation, bug diagnosis, bug fixing, refactoring/optimization, documentation generation, validation/review, and file/project operations.

- [ ] **Step 2: Run the focused tests and verify they fail for the missing canonical routing**

Run:

```bash
pytest core/tests/test_capability_intent_routing.py -q
```

Expected: FAIL because the current registry still uses the vague capability names/IDs and the Brain has no canonical intent eligibility layer.

- [ ] **Step 3: Commit the red tests**

```bash
git add core/tests/test_capability_intent_routing.py
git commit -m "test: define canonical capability routing"
```

---

### Task 2: Introduce the canonical capability model and registry contract

**Files:**
- Create: `capabilities/canonical.py`
- Modify: `capabilities/registry.json`
- Modify: `capabilities/seed_registry.py`
- Modify: `layers/capability_registry/models.py`
- Modify: `layers/capability_registry/registry.py`
- Test: `core/tests/test_capability_registry.py`

**Interfaces:**
- Consumes: existing capability metadata model and registry loader.
- Produces: canonical capability metadata with explicit `intent_class`, `allowed_intents`, `forbidden_intents`, `risk_level`, and `side_effects` fields; generated IDs start at `CAP-011` or later.

- [ ] **Step 1: Add failing registry tests**

```python

def test_registry_exposes_exactly_ten_canonical_capabilities():
    ids = [cap.id for cap in registry.list_all_capabilities() if cap.canonical]
    assert ids == [f"CAP-{i:03d}" for i in range(1, 11)]


def test_generated_capabilities_are_outside_reserved_baseline_range():
    generated = [cap for cap in registry.list_all_capabilities() if cap.generated]
    assert all(int(cap.id.split("-")[-1]) > 10 for cap in generated)
```

- [ ] **Step 2: Run tests and verify they fail**

```bash
pytest core/tests/test_capability_registry.py -q
```

Expected: FAIL because the current metadata has historical CAP IDs and no canonical marker.

- [ ] **Step 3: Implement canonical metadata contract**

Add a stable data structure that defines exactly these baseline capabilities:

```text
CAP-001 Code Generation
CAP-002 Code Modification
CAP-003 Code Explanation & Analysis
CAP-004 Bug Detection & Diagnosis
CAP-005 Bug Fixing
CAP-006 Refactoring & Optimization
CAP-007 Test Generation
CAP-008 Documentation Generation
CAP-009 Code Validation & Review
CAP-010 Project/File Operations
```

Give each capability a single purpose, supported languages, allowed intents, forbidden intents, input/output contract, risk level, and side-effect declaration.

- [ ] **Step 4: Update registry loading and generated-ID allocation**

Keep canonical metadata in one machine-readable source. Ensure generated/evolved capabilities cannot claim IDs 001–010, while old generated artifacts with historical CAP-010 are migrated to the next available ID and their provenance keeps the original historical reference.

- [ ] **Step 5: Run focused registry tests**

```bash
pytest core/tests/test_capability_registry.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit registry changes**

```bash
git add capabilities/canonical.py capabilities/registry.json capabilities/seed_registry.py layers/capability_registry/models.py layers/capability_registry/registry.py core/tests/test_capability_registry.py
git commit -m "feat: define canonical ten-capability baseline"
```

---

### Task 3: Replace the vague seed folders with ten focused implementations

**Files:**
- Create: `capabilities/seeds/cap_001_code_generation/`
- Create: `capabilities/seeds/cap_002_code_modification/`
- Create: `capabilities/seeds/cap_003_code_analysis/`
- Create: `capabilities/seeds/cap_004_bug_diagnosis/`
- Create: `capabilities/seeds/cap_005_bug_fixing/`
- Create: `capabilities/seeds/cap_006_refactoring/`
- Create: `capabilities/seeds/cap_007_test_generation/`
- Create: `capabilities/seeds/cap_008_documentation/`
- Create: `capabilities/seeds/cap_009_validation/`
- Create: `capabilities/seeds/cap_010_project_operations/`
- Modify: existing seed implementation files as needed to reuse safe logic
- Test: `core/tests/test_canonical_capabilities.py`

**Interfaces:**
- Consumes: `CapabilityContext` and existing LLM/provider abstraction.
- Produces: one executable `run(context) -> CapabilityResult` per canonical capability, each with a narrow behavior contract.

- [ ] **Step 1: Add failing capability-contract tests**

```python

def test_code_generation_creates_source_from_empty_working_code():
    result = run_capability("CAP-001", request="Create a Python calculator.", code="", language="python")
    assert result.success
    assert result.modified_code


def test_test_generation_requires_explicit_test_intent():
    result = run_capability("CAP-007", request="Create a Python calculator.", code="", language="python")
    assert not result.success
    assert "test" in (result.error or "").lower()
```

Add narrow contract checks for all ten capabilities.

- [ ] **Step 2: Run tests and verify failure**

```bash
pytest core/tests/test_canonical_capabilities.py -q
```

Expected: FAIL because the new canonical folders/contracts do not yet exist.

- [ ] **Step 3: Implement CAP-001 through CAP-010**

Use the existing implementations where behavior is already safe, but move them under the new focused folders. `CAP-001` must own source creation; `CAP-002` must own source modification; `CAP-007` must be test-only; `CAP-010` must own file/project structure operations rather than language reasoning.

- [ ] **Step 4: Run focused capability tests**

```bash
pytest core/tests/test_canonical_capabilities.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit capability implementations**

```bash
git add capabilities/seeds core/tests/test_canonical_capabilities.py
 git commit -m "feat: implement focused canonical capabilities"
```

---

### Task 4: Add intent classification and capability eligibility to Brain planning

**Files:**
- Modify: `brain/brain.py`
- Test: `brain/tests/test_capability_planning.py`

**Interfaces:**
- Consumes: canonical capability metadata and the existing language-inference result.
- Produces: Brain plan JSON containing `intent_class`, `language`, `language_confidence`, and a capability plan restricted by intent eligibility.

- [ ] **Step 1: Add failing Brain routing tests**

```python

def test_code_generation_prompt_routes_to_cap_001(fake_provider):
    brain = Brain(provider=fake_provider)
    plan = brain.plan(request="Write a Python program that asks how many numbers and then performs arithmetic.", code="", language="python", file_path="main.py", capability_catalog=canonical_catalog())
    assert plan.intent_class == "code_generation"
    assert [x["capability_id"] for x in plan.steps] == ["CAP-001"]


def test_test_generation_is_ineligible_for_generation_prompt(fake_provider):
    brain = Brain(provider=fake_provider)
    plan = brain.plan(request="Write Python code for a calculator.", code="", language="python", file_path="main.py", capability_catalog=canonical_catalog())
    assert "CAP-007" not in [x["capability_id"] for x in plan.steps]
```

- [ ] **Step 2: Run and watch the tests fail**

```bash
pytest brain/tests/test_capability_planning.py -q
```

Expected: FAIL because `BrainPlan` has no `intent_class` and the candidate set is not intent-filtered.

- [ ] **Step 3: Implement minimal intent classification/eligibility**

Add deterministic pre-filtering around the model plan:

```text
request + code + filename
        ↓
intent_class inference
        ↓
eligible canonical capabilities
        ↓
LLM chooses only from eligible IDs
        ↓
post-validate that every step is eligible
```

Use explicit request semantics first; only use the LLM to choose among capabilities eligible for the classified intent. Do not rely on keyword patches inside CAP-007 for global routing.

- [ ] **Step 4: Run Brain tests**

```bash
pytest brain/tests/test_capability_planning.py brain/tests/test_language_detection.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit Brain routing**

```bash
git add brain/brain.py brain/tests/test_capability_planning.py
 git commit -m "fix: enforce intent-aware capability planning"
```

---

### Task 5: Migrate evolution metadata and documentation

**Files:**
- Modify: `capabilities/registry.json`
- Modify: `core/assistant_service.py`
- Modify: `ui/web_app.py`
- Modify: `ui/web/app.js`
- Modify: `README.md`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/master.md`
- Modify: `docs/PIPELINE.md`
- Modify: `docs/scenarios.md`
- Create: `docs/capabilities/CANONICAL_CAPABILITIES.md`
- Create: one `README.md` and `metadata.json` under each canonical capability directory
- Test: `core/tests/test_evolution_capability_ids.py`

**Interfaces:**
- Consumes: canonical capability registry and existing provenance/evolution records.
- Produces: UI/API data that distinguishes canonical baseline capabilities from evolved capabilities and documents all ten contracts.

- [ ] **Step 1: Add failing migration/documentation tests**

```python

def test_registry_has_no_generated_capability_in_reserved_ids():
    for cap in registry.list_all_capabilities():
        if cap.generated:
            assert int(cap.id.split("-")[-1]) > 10


def test_docs_name_all_ten_canonical_capabilities():
    text = Path("docs/capabilities/CANONICAL_CAPABILITIES.md").read_text()
    for number in range(1, 11):
        assert f"CAP-{number:03d}" in text
```

- [ ] **Step 2: Run and verify failure**

```bash
pytest core/tests/test_evolution_capability_ids.py -q
```

Expected: FAIL until metadata/docs are migrated.

- [ ] **Step 3: Migrate generated historical capability references**

Move the existing generated SQL/parse examples above the reserved baseline range without deleting provenance. Add `canonical=false`, `generated=true`, `parent_capability_id`, `historical_id` and the existing trigger information to migrated metadata.

- [ ] **Step 4: Update service/UI labels**

Make the capability view display `Canonical` vs `Generated`, the ten baseline names, and provenance for generated extensions. Ensure the chat trace reports `intent_class` and the selected canonical capability.

- [ ] **Step 5: Update all listed docs**

Replace the old vague Stage 0 capability list with the ten canonical capabilities. Document the routing rule that separates generation, modification, analysis, diagnosis, fixing, refactoring, tests, documentation, validation and project operations.

- [ ] **Step 6: Run documentation/evolution tests**

```bash
pytest core/tests/test_evolution_capability_ids.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit migration and docs**

```bash
git add capabilities/registry.json core/assistant_service.py ui/web_app.py ui/web/app.js README.md docs/ARCHITECTURE.md docs/master.md docs/PIPELINE.md docs/scenarios.md docs/capabilities
 git commit -m "docs: document canonical capability contracts"
```

---

### Task 6: Validate the complete system and merge to main

**Files:**
- Modify: `tests` only if a discovered regression requires a focused test

**Interfaces:**
- Consumes: all canonical capability, Brain, registry, evolution and UI changes.
- Produces: green CI for the main branch and a merged implementation.

- [ ] **Step 1: Run focused regression suite**

```bash
pytest brain/tests core/tests -q
```

Expected: all focused tests pass, with any unrelated pre-existing live-Ollama failures clearly identified.

- [ ] **Step 2: Run full suite**

```bash
pytest -q
```

Expected: no new failures attributable to canonical capability migration.

- [ ] **Step 3: Verify repository status and diff**

```bash
git status --short
git log --oneline -8
```

Expected: clean worktree and commits limited to the requested architecture/routing/docs/tests.

- [ ] **Step 4: Open/update PR from `feature/canonical-capabilities` to `main`**

PR title:

```text
feat: establish canonical ten-capability baseline
```

PR body must summarize the routing fix, capability migration, generated-ID reservation, documentation updates, and tests.

- [ ] **Step 5: Wait for CI and verify it**

Use the GitHub Actions status for the PR and the merge commit. Do not claim completion until the relevant workflow result is known.

- [ ] **Step 6: Merge to `main`**

Use the repository merge workflow only after CI is acceptable. Record the resulting merge SHA.

- [ ] **Step 7: Verify `main`**

Confirm `main` contains:

- `CAP-001` through `CAP-010` exactly once as canonical capabilities.
- `CAP-007` only for explicit test-generation intent.
- the ten capability directories and documentation.
- migrated generated IDs above `CAP-010`.
- updated README/architecture/pipeline docs.

Then report the exact merge SHA and CI status.
