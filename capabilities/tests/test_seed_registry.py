from capabilities.seed_registry import list_seed_metadata_paths, load_entry_point, load_seed_capabilities


def test_discovers_all_seed_metadata_files_including_retired_legacy():
    assert len(list_seed_metadata_paths()) >= 19


def test_loads_only_the_ten_active_canonical_capabilities():
    ids = [c.id for c in load_seed_capabilities()]
    assert ids == [f"CAP-{i:03d}" for i in range(1, 11)]


def test_all_active_seeds_are_canonical_origin_seed():
    for cap in load_seed_capabilities():
        assert cap.origin == "seed"
        assert cap.status == "active"


def test_all_active_entry_points_resolve():
    for cap in load_seed_capabilities():
        assert callable(load_entry_point(cap))
