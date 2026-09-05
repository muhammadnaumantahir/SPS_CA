from pathlib import Path

import pytest

from layers.layer_01_software_dna import SoftwareDNA
from layers.layer_02_governance import GovernanceGate
from layers.layer_08_evolution.self_programming import SelfProgrammingEngine


class StubLLM:
    def __init__(self, response):
        self.response = response

    def query(self, **kwargs):
        return self.response


class StubExecution:
    pass


def test_diagnosis_classifies_routing_failure(tmp_path):
    engine = SelfProgrammingEngine(repo_root=tmp_path, dna=SoftwareDNA(rules=[]), governance=GovernanceGate(), llm=StubLLM("{}"), execution=StubExecution())
    diagnosis = engine.diagnose_failure(
        symptom="Brain selected test_generation for a modification request",
        component="intent routing",
        affected_files=["brain/brain.py"],
        failure_id="FAIL-ROUTE",
    )
    assert diagnosis.category == "ROUTING_FAILURE"
    assert diagnosis.severity == "high"
    assert diagnosis.failure_id == "FAIL-ROUTE"


def test_candidate_cannot_modify_protected_surfaces(tmp_path):
    engine = SelfProgrammingEngine(repo_root=tmp_path, dna=SoftwareDNA(rules=[]), governance=GovernanceGate(), llm=StubLLM("{}"), execution=StubExecution())
    diagnosis = engine.diagnose_failure(
        symptom="broken routing",
        component="brain",
        affected_files=["brain/brain.py"],
    )
    with pytest.raises(Exception):
        engine._validate_candidate(
            diagnosis,
            {
                "edits": [
                    {"file_path": "governance/dna_rules.json", "new_content": "{}"}
                ]
            },
        )


def test_candidate_cannot_escape_repo(tmp_path):
    engine = SelfProgrammingEngine(repo_root=tmp_path, dna=SoftwareDNA(rules=[]), governance=GovernanceGate(), llm=StubLLM("{}"), execution=StubExecution())
    diagnosis = engine.diagnose_failure(
        symptom="broken routing",
        component="brain",
        affected_files=["brain/brain.py"],
    )
    with pytest.raises(Exception):
        engine._validate_candidate(
            diagnosis,
            {
                "edits": [
                    {"file_path": "../brain/brain.py", "new_content": "x = 1\n"}
                ]
            },
        )


def test_candidate_must_stay_within_diagnosed_scope(tmp_path):
    engine = SelfProgrammingEngine(repo_root=tmp_path, dna=SoftwareDNA(rules=[]), governance=GovernanceGate(), llm=StubLLM("{}"), execution=StubExecution())
    diagnosis = engine.diagnose_failure(
        symptom="trace failure",
        component="trace",
        affected_files=["ui/web/app.js"],
    )
    with pytest.raises(Exception):
        engine._validate_candidate(
            diagnosis,
            {
                "edits": [
                    {"file_path": "ui/web_app.py", "new_content": "x = 1\n"}
                ]
            },
        )


def test_regression_case_is_persisted_without_source(tmp_path):
    engine = SelfProgrammingEngine(repo_root=tmp_path, dna=SoftwareDNA(rules=[]), governance=GovernanceGate(), llm=StubLLM("{}"), execution=StubExecution())
    diagnosis = engine.diagnose_failure(
        symptom="execution failed",
        component="execution",
        affected_files=["layers/layer_10_execution/execution_engine.py"],
    )
    case_id = engine.record_regression_case(diagnosis, ["python -m pytest -q layers/layer_10_execution/tests"])
    records = engine._load_regressions()
    assert records[-1]["case_id"] == case_id
    assert "source" not in records[-1]


def test_read_context_skips_protected_files(tmp_path):
    protected = tmp_path / "governance" / "dna_rules.json"
    protected.parent.mkdir(parents=True)
    protected.write_text('{"dna_rules": []}', encoding="utf-8")
    engine = SelfProgrammingEngine(repo_root=tmp_path, dna=SoftwareDNA(rules=[]), governance=GovernanceGate(), llm=StubLLM("{}"), execution=StubExecution())
    assert engine._read_context(["governance/dna_rules.json"]) == ""
