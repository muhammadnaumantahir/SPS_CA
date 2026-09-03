import json

import pytest

from layers.layer_08_evolution.controlled_evolution import ControlledEvolutionEngine


class FakeLLM:
    def query(self, **kwargs):
        return (
            "from capabilities.base import CapabilityContext, CapabilityResult\n\n"
            "SUPPORTED_LANGUAGES = ['python']\n"
            "TRIGGER_PATTERN = 'example_gap'\n\n"
            "def run(context: CapabilityContext) -> CapabilityResult:\n"
            "    if context.language not in SUPPORTED_LANGUAGES:\n"
            "        return CapabilityResult.ok(summary='unsupported')\n"
            "    if not context.code.strip():\n"
            "        return CapabilityResult.fail(error='empty input')\n"
            "    return CapabilityResult.ok(summary='candidate', modified_code=context.code + '\\n# improved')\n"
        )


def test_generated_ids_start_at_cap011(tmp_path):
    seeds = tmp_path / 'seeds'
    generated = tmp_path / 'generated'
    (seeds / 'cap_010_project_operations').mkdir(parents=True)
    (seeds / 'cap_010_project_operations' / 'metadata.json').write_text(
        json.dumps({'id': 'CAP-010'}), encoding='utf-8'
    )
    engine = ControlledEvolutionEngine(
        seeds_dir=str(seeds), generated_dir=str(generated), registry_path=str(tmp_path / 'registry.json'), llm=FakeLLM()
    )
    assert engine.next_capability_id() == 'CAP-011'


def test_candidate_contract_rejects_execution_primitives():
    with pytest.raises(ValueError):
        ControlledEvolutionEngine._validate_candidate_source(
            "import subprocess\n"
            "SUPPORTED_LANGUAGES=['python']\nTRIGGER_PATTERN='x'\n"
            "def run(context):\n    return None\n"
        )


def test_candidate_contract_requires_run():
    with pytest.raises(ValueError):
        ControlledEvolutionEngine._validate_candidate_source(
            "SUPPORTED_LANGUAGES=['python']\nTRIGGER_PATTERN='x'\n"
        )
