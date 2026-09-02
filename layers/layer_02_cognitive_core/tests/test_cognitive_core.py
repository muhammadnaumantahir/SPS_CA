import pytest

from layers.layer_01_software_dna import CapabilityTemplate
from layers.layer_02_cognitive_core.cognitive_core import CognitiveCore
from layers.layer_02_cognitive_core.models import ProjectAnalysis


def fake_capabilities():
    return [
        CapabilityTemplate(
            id="CAP-001",
            name="Simple Bug Detection",
            version="0.1.0",
            description="",
            entry_point="capabilities.seeds.cap_001_bug_detection.capability.run",
            target_languages=["python"],
            tags=["bug-detection"],
        ),
        CapabilityTemplate(
            id="CAP-003",
            name="Unit Test Generation",
            version="0.1.0",
            description="",
            entry_point="capabilities.seeds.cap_003_unit_test_generation.capability.run",
            target_languages=["python"],
            tags=["testing"],
        ),
        CapabilityTemplate(
            id="CAP-010",
            name="Go Only Capability",
            version="0.1.0",
            description="",
            entry_point="capabilities.generated.cap_010.capability.run",
            target_languages=["go"],
            tags=["bug-detection"],
        ),
    ]


class TestReceiveRequest:
    def test_wraps_request_fields(self):
        cc = CognitiveCore()
        req = cc.receive_request("Fix the bug", code_context="x = 1", target_project="projects/a", target_language="python")
        assert req.user_request == "Fix the bug"
        assert req.code_context == "x = 1"
        assert req.target_project == "projects/a"
        assert req.target_language == "python"

    def test_strips_whitespace(self):
        assert CognitiveCore().receive_request("   Fix the bug   ").user_request == "Fix the bug"

    def test_rejects_empty_request(self):
        with pytest.raises(ValueError):
            CognitiveCore().receive_request("   ")


class TestAnalyzeTargetProject:
    def test_analyzes_files_on_disk(self, tmp_path):
        (tmp_path / "a.py").write_text("def foo():\n    pass\n")
        (tmp_path / "b.py").write_text("def bar():\n    pass\n")
        (tmp_path / "README.md").write_text("# not code")
        analysis = CognitiveCore().analyze_target_project(str(tmp_path))
        assert len(analysis.files) == 2
        assert analysis.total_functions == 2

    def test_missing_project_path_returns_empty_analysis(self, tmp_path):
        assert CognitiveCore().analyze_target_project(str(tmp_path / "does_not_exist")).files == []

    def test_analyze_single_file(self):
        analysis = CognitiveCore().analyze_single_file("a.py", "def foo():\n    pass\n")
        assert analysis.languages_detected == ["python"]
        assert analysis.total_functions == 1


class TestDecomposeTask:
    def test_single_task_not_split(self):
        assert len(CognitiveCore().decompose_task("Fix the bug in routes.py")) == 1

    def test_splits_on_and_then(self):
        subtasks = CognitiveCore().decompose_task("Fix the bug and then add tests")
        assert len(subtasks) == 2
        assert subtasks[0].description == "Fix the bug"
        assert subtasks[1].description == "add tests"
        assert subtasks[1].depends_on == [subtasks[0].id]

    def test_splits_on_commas(self):
        assert len(CognitiveCore().decompose_task("Fix bug, add tests, update docs")) == 3

    def test_empty_task_returns_empty_list(self):
        assert CognitiveCore().decompose_task("   ") == []

    def test_subtask_ids_are_sequential(self):
        assert [s.id for s in CognitiveCore().decompose_task("A and B and C")] == ["subtask_001", "subtask_002", "subtask_003"]


class TestSelectCandidateCapabilities:
    def test_filters_by_language(self):
        analysis = ProjectAnalysis(project_path="p", files=[], languages_detected=["python"])
        ids = {c.id for c in CognitiveCore(capability_loader=fake_capabilities).select_candidate_capabilities(analysis)}
        assert ids == {"CAP-001", "CAP-003"}

    def test_keyword_hint_narrows_selection(self):
        analysis = ProjectAnalysis(project_path="p", files=[], languages_detected=["python"])
        ids = {c.id for c in CognitiveCore(capability_loader=fake_capabilities).select_candidate_capabilities(analysis, user_request="please fix this bug")}
        assert ids == {"CAP-001"}

    def test_no_keyword_match_falls_back_to_all_eligible(self):
        analysis = ProjectAnalysis(project_path="p", files=[], languages_detected=["python"])
        ids = {c.id for c in CognitiveCore(capability_loader=fake_capabilities).select_candidate_capabilities(analysis, user_request="do something vague")}
        assert ids == {"CAP-001", "CAP-003"}

    def test_language_with_no_matches_returns_empty(self):
        analysis = ProjectAnalysis(project_path="p", files=[], languages_detected=["csharp"])
        assert CognitiveCore(capability_loader=fake_capabilities).select_candidate_capabilities(analysis) == []


class TestPlanModificationStrategy:
    def test_builds_plan_with_default_subtask(self):
        analysis = ProjectAnalysis(project_path="proj", files=[], languages_detected=["python"])
        plan = CognitiveCore(capability_loader=fake_capabilities).plan_modification_strategy(analysis, fake_capabilities()[:2])
        assert plan.selected_capability_ids == ["CAP-001", "CAP-003"]
        assert len(plan.subtasks) == 1
        assert "proj" in plan.subtasks[0].description

    def test_uses_provided_subtasks(self):
        cc = CognitiveCore(capability_loader=fake_capabilities)
        analysis = ProjectAnalysis(project_path="proj", files=[], languages_detected=["python"])
        subtasks = cc.decompose_task("Fix bug and add tests")
        assert cc.plan_modification_strategy(analysis, fake_capabilities()[:2], subtasks=subtasks).subtasks == subtasks


class TestCognitiveCoreEndToEnd:
    def test_full_flow_on_real_seed_capabilities(self):
        cc = CognitiveCore()
        req = cc.receive_request("Fix the bug and then add tests")
        analysis = cc.analyze_single_file("routes.py", "def f(x):\n    return x == None\n")
        subtasks = cc.decompose_task(req.user_request)
        caps = cc.select_candidate_capabilities(analysis, user_request=req.user_request)
        plan = cc.plan_modification_strategy(analysis, caps, subtasks)
        assert len(subtasks) == 2
        assert "CAP-001" in plan.selected_capability_ids
        assert plan.subtasks == subtasks
