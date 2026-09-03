import json
from pathlib import Path

import pytest

from evaluation.live_self_programming import main, run_live


def test_live_runner_requires_explicit_confirmation(monkeypatch):
    monkeypatch.setattr("sys.argv", ["live_self_programming"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2


def test_live_runner_cleans_disposable_workspace(tmp_path, monkeypatch):
    marker = tmp_path / "README.md"
    marker.write_text("test", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    result = run_live(
        repo_root=tmp_path,
        task="add input validation capability",
        language="python",
        keep_workspace=False,
    )

    assert result["workspace"] is None
    assert not Path(result["temporary_workspace"]).exists()


def test_live_runner_reports_cycle_and_authority(monkeypatch, tmp_path):
    class FakeService:
        def __init__(self, **kwargs):
            pass

        def assess_after_task(self, capability_ids):
            from layers.layer_06_meta_learning import OptimizationCyclePlan
            return OptimizationCyclePlan(
                cycle_id="OPT-LIVE-TEST",
                triggered=False,
                created_at="2026-01-01T00:00:00+00:00",
            )

    monkeypatch.setattr("evaluation.live_self_programming.OptimizationCycleService", FakeService)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "README.md").write_text("test", encoding="utf-8")
    result = run_live(
        repo_root=tmp_path,
        task="add logging capability",
        language="python",
        keep_workspace=False,
    )
    assert result["cycle"]["cycle_id"] == "OPT-LIVE-TEST"
    assert result["execution"] == []
