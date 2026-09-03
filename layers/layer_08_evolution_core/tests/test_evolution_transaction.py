from layers.layer_08_evolution.evolution_transaction import EvolutionTransaction


def test_transaction_rolls_back_file_and_directory(tmp_path):
    source = tmp_path / "source.py"
    source.write_text("original", encoding="utf-8")
    generated = tmp_path / "capabilities" / "generated" / "cap_x"
    generated.mkdir(parents=True)
    (generated / "capability.py").write_text("old", encoding="utf-8")

    tx = EvolutionTransaction(tmp_path, transaction_id="tx-test")
    tx.begin(["source.py", "capabilities/generated/cap_x"])
    source.write_text("changed", encoding="utf-8")
    (generated / "capability.py").write_text("changed", encoding="utf-8")
    tx.rollback()

    assert source.read_text(encoding="utf-8") == "original"
    assert (generated / "capability.py").read_text(encoding="utf-8") == "old"


def test_transaction_rejects_escape(tmp_path):
    tx = EvolutionTransaction(tmp_path, transaction_id="tx-safe")
    try:
        tx.begin(["../escape.txt"])
    except Exception as exc:
        assert "unsafe transaction path" in str(exc)
    else:
        raise AssertionError("path escape was not rejected")
