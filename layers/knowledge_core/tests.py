from .knowledge_core import KnowledgeCore


def test_knowledge_snapshot_is_structured_and_valid():
    core = KnowledgeCore()
    snapshot = core.build_snapshot(
        language="python",
        file_path="main.py",
        symbols=["add"],
        capabilities=[{"id": "CAP-001", "name": "Bug Detection", "tags": ["analysis"]}],
        facts={"source_chars": 20},
    )
    assert core.validate(snapshot)
    assert snapshot.language == "python"
    assert snapshot.symbols == ("add",)


def test_knowledge_rejects_missing_identity():
    core = KnowledgeCore()
    snapshot = core.build_snapshot(language="", file_path="main.py")
    assert not core.validate(snapshot)
