"""Unit tests for Layer 8 EvolutionEngine."""
from pathlib import Path

import pytest

from layers.layer_03_experience import ExperienceLog, Task
from layers.layer_08_evolution import EvolutionEngine, EvolutionError
from models.base import LLMProvider, LLMRequest, LLMResponse


class FakeProvider(LLMProvider):
    name = "fake"

    def __init__(self, response: str):
        self.response = response

    def is_available(self) -> bool:
        return True

    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(self.response, request.model or "fake-model", self.name)


def make_log(*categories: str) -> ExperienceLog:
    return ExperienceLog(
        [
            Task(
                id=f"task_{index}",
                user_request=f"request {index}",
                status="failure",
                failure_category=category,
                selected_capability="CAP-001",
                target_language="python",
            )
            for index, category in enumerate(categories, 1)
        ]
    )


def valid_response() -> str:
    return (
        '{"capability_py": "from capabilities.base import CapabilityResult\\n\\n'
        'def run(context):\\n    return CapabilityResult.ok(\\\"ok\\\")\\n", '
        '"tests_py": "def test_generated():\\n    assert True\\n", '
        '"readme_md": "# Generated capability\\n"}'
    )


def test_should_evolve_when_threshold_reached():
    engine = EvolutionEngine(min_occurrences=3)
    assert engine.should_evolve(make_log("Parse error", "Parse error", "Parse error"))


def test_should_not_evolve_before_threshold():
    engine = EvolutionEngine(min_occurrences=3)
    assert not engine.should_evolve(make_log("Parse error", "Parse error"))


def test_custom_threshold():
    engine = EvolutionEngine(min_occurrences=3)
    assert engine.should_evolve(make_log("x", "x"), min_occurrences=2)


def test_invalid_threshold_rejected():
    with pytest.raises(ValueError):
        EvolutionEngine(min_occurrences=0)


def test_repeated_patterns_sorted():
    engine = EvolutionEngine(min_occurrences=2)
    patterns = engine.repeated_failure_patterns(make_log("b", "a", "b", "a", "a"))
    assert list(patterns) == ["a", "b"]
    assert patterns == {"a": 3, "b": 2}


def test_plan_uses_parent_capability_and_language():
    log = make_log("Parser", "Parser", "Parser")
    plan = EvolutionEngine().plan_new_capability("Parser", log, capability_id="CAP-009")
    assert plan.capability_id == "CAP-009"
    assert plan.trigger_pattern == "Parser"
    assert plan.parent_capabilities == ["CAP-001"]
    assert "python" in plan.supported_languages
    assert plan.test_cases


def test_plan_requires_pattern():
    with pytest.raises(ValueError):
        EvolutionEngine().plan_new_capability("   ")


def test_next_id_ignores_non_capability_directories(tmp_path: Path):
    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "CAP-003").mkdir()
    (generated / "notes").mkdir()
    pending = tmp_path / "pending"
    pending.mkdir()
    (pending / "CAP-007").mkdir()
    engine = EvolutionEngine(generated_root=str(generated), pending_root=str(pending))
    assert engine.plan_new_capability("x").capability_id == "CAP-008"


def test_generation_requires_provider(tmp_path: Path):
    engine = EvolutionEngine(generated_root=str(tmp_path / "g"))
    with pytest.raises(EvolutionError, match="LLMProvider"):
        engine.generate_capability_code(engine.plan_new_capability("parser"))


def test_generation_parses_provider_json(tmp_path: Path):
    engine = EvolutionEngine(
        provider=FakeProvider(valid_response()),
        generated_root=str(tmp_path / "g"),
        pending_root=str(tmp_path / "p"),
    )
    generated = engine.generate_capability_code(engine.plan_new_capability("parser"))
    assert set(generated.files) == {"capability.py", "tests.py", "metadata.json", "README.md"}
    assert generated.metadata["model_provider"] == "fake"


def test_generation_accepts_fenced_json(tmp_path: Path):
    provider = FakeProvider("```json\n" + valid_response() + "\n```")
    engine = EvolutionEngine(provider=provider, generated_root=str(tmp_path / "g"))
    generated = engine.generate_capability_code(engine.plan_new_capability("parser"))
    assert generated.files["README.md"].startswith("#")


def test_generation_rejects_missing_key(tmp_path: Path):
    provider = FakeProvider('{"capability_py":"def run(context): pass", "tests_py":"def test_x(): pass"}')
    engine = EvolutionEngine(provider=provider, generated_root=str(tmp_path / "g"))
    with pytest.raises(EvolutionError, match="missing keys"):
        engine.generate_capability_code(engine.plan_new_capability("parser"))


def test_generation_rejects_invalid_python(tmp_path: Path):
    provider = FakeProvider('{"capability_py":"def run(:", "tests_py":"def test_x(): pass", "readme_md":"# x"}')
    engine = EvolutionEngine(provider=provider, generated_root=str(tmp_path / "g"))
    with pytest.raises(EvolutionError, match="invalid Python"):
        engine.generate_capability_code(engine.plan_new_capability("parser"))


def test_generation_rejects_dangerous_import(tmp_path: Path):
    provider = FakeProvider(
        '{"capability_py":"import subprocess\\ndef run(context): pass", "tests_py":"def test_x(): pass", "readme_md":"# x"}'
    )
    engine = EvolutionEngine(provider=provider, generated_root=str(tmp_path / "g"))
    with pytest.raises(EvolutionError, match="restricted module"):
        engine.generate_capability_code(engine.plan_new_capability("parser"))


def test_stage_writes_all_files(tmp_path: Path):
    engine = EvolutionEngine(
        provider=FakeProvider(valid_response()),
        generated_root=str(tmp_path / "g"),
        pending_root=str(tmp_path / "p"),
    )
    generated = engine.generate_capability_code(engine.plan_new_capability("parser", capability_id="CAP-009"))
    staged = engine.stage_capability(generated)
    assert staged == tmp_path / "p" / "CAP-009"
    assert all((staged / name).exists() for name in generated.files)


def test_stage_is_not_overwritten(tmp_path: Path):
    engine = EvolutionEngine(
        provider=FakeProvider(valid_response()),
        generated_root=str(tmp_path / "g"),
        pending_root=str(tmp_path / "p"),
    )
    generated = engine.generate_capability_code(engine.plan_new_capability("parser", capability_id="CAP-009"))
    engine.stage_capability(generated)
    with pytest.raises(EvolutionError, match="already exists"):
        engine.stage_capability(generated)


def test_promotion_requires_approval(tmp_path: Path):
    engine = EvolutionEngine(
        provider=FakeProvider(valid_response()),
        generated_root=str(tmp_path / "g"),
        pending_root=str(tmp_path / "p"),
    )
    generated = engine.generate_capability_code(engine.plan_new_capability("parser", capability_id="CAP-009"))
    engine.stage_capability(generated)
    with pytest.raises(EvolutionError, match="approval"):
        engine.promote_capability("CAP-009", approved=False)


def test_promotion_copies_staged_artifacts(tmp_path: Path):
    engine = EvolutionEngine(
        provider=FakeProvider(valid_response()),
        generated_root=str(tmp_path / "g"),
        pending_root=str(tmp_path / "p"),
    )
    generated = engine.generate_capability_code(engine.plan_new_capability("parser", capability_id="CAP-009"))
    engine.stage_capability(generated)
    destination = engine.promote_capability("CAP-009", approved=True)
    assert (destination / "capability.py").exists()
    assert (destination / "metadata.json").exists()


def test_promotion_requires_existing_stage(tmp_path: Path):
    engine = EvolutionEngine(generated_root=str(tmp_path / "g"), pending_root=str(tmp_path / "p"))
    with pytest.raises(EvolutionError, match="does not exist"):
        engine.promote_capability("CAP-999", approved=True)


def test_test_capability_missing_tests(tmp_path: Path):
    engine = EvolutionEngine(pending_root=str(tmp_path / "p"))
    result = engine.test_capability("CAP-001")
    assert not result.passed
    assert "tests.py not found" in result.error


def test_coverage_extraction():
    assert EvolutionEngine._extract_coverage("TOTAL 20 2 90%") == 90.0
    assert EvolutionEngine._extract_coverage("no coverage") is None
