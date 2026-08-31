import pytest

from capabilities.base import CapabilityContext
from capabilities.seed_registry import (
    list_seed_metadata_paths,
    load_entry_point,
    load_seed_capabilities,
)


class TestSeedRegistry:
    def test_discovers_all_eight_seeds(self):
        paths = list_seed_metadata_paths()
        assert len(paths) == 8

    def test_loads_capability_templates(self):
        caps = load_seed_capabilities()
        ids = sorted(c.id for c in caps)
        assert ids == [f"CAP-{i:03d}" for i in range(1, 9)]

    def test_all_seeds_are_active_origin_seed(self):
        for cap in load_seed_capabilities():
            assert cap.origin == "seed"
            assert cap.status == "active"
            assert cap.parent_capability_id is None

    def test_all_entry_points_resolve_and_are_callable(self):
        for cap in load_seed_capabilities():
            fn = load_entry_point(cap)
            assert callable(fn)

    def test_all_seed_entry_points_run_on_trivial_python(self):
        code = "def f(x):\n    return x\n"
        for cap in load_seed_capabilities():
            fn = load_entry_point(cap)
            ctx = CapabilityContext(code=code, language="python", file_path="f.py")
            result = fn(ctx)
            assert result.success is True

    def test_unsupported_language_does_not_raise(self):
        code = "x"
        for cap in load_seed_capabilities():
            fn = load_entry_point(cap)
            ctx = CapabilityContext(code=code, language="cobol", file_path="f.cob")
            result = fn(ctx)
            # Seeds are Python-only for Phase 1; unsupported languages must
            # degrade gracefully (success with a note), never raise.
            assert result.success is True
