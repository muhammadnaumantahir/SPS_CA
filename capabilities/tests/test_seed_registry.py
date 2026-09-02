from capabilities.base import CapabilityContext
from capabilities.seed_registry import list_seed_metadata_paths, load_entry_point, load_seed_capabilities


class TestSeedRegistry:
    def test_discovers_all_seeds(self):
        assert len(list_seed_metadata_paths()) == 9

    def test_loads_capability_templates_in_pipeline_number_order(self):
        ids = [c.id for c in load_seed_capabilities()]
        assert ids == [f"CAP-{i:03d}" for i in range(1, 10)]

    def test_all_seeds_are_active_origin_seed(self):
        for cap in load_seed_capabilities():
            assert cap.origin == "seed"
            assert cap.status == "active"
            assert cap.parent_capability_id is None

    def test_all_entry_points_resolve_and_are_callable(self):
        for cap in load_seed_capabilities():
            assert callable(load_entry_point(cap))

    def test_non_brain_non_llm_seeds_run_on_trivial_python(self):
        code = "def f(x):\n    return x\n"
        for cap in load_seed_capabilities():
            if cap.id in {"CAP-001", "CAP-009"}:
                continue
            result = load_entry_point(cap)(CapabilityContext(code=code, language="python", file_path="f.py"))
            assert result.success is True

    def test_unsupported_language_does_not_raise_for_non_llm_seeds(self):
        for cap in load_seed_capabilities():
            if cap.id in {"CAP-001", "CAP-009"}:
                continue
            result = load_entry_point(cap)(CapabilityContext(code="x", language="cobol", file_path="f.cob"))
            assert result.success is True
