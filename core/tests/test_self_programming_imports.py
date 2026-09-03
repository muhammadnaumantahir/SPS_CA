def test_self_programming_import_contract():
    from layers.layer_08_evolution import FailureDiagnosis, SelfProgrammingEngine, SelfRepairResult
    from layers.layer_10_execution import Change, FileEdit

    assert FailureDiagnosis is not None
    assert SelfRepairResult is not None
    assert SelfProgrammingEngine is not None
    assert Change is not None
    assert FileEdit is not None
