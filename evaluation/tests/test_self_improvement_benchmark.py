from layers.layer_05_experience import ExperienceLog, Task
from evaluation.self_improvement_benchmark import SelfImprovementBenchmark


def _log(statuses):
    return ExperienceLog([
        Task(
            id=f"t{i}",
            user_request="benchmark",
            target_project="sps-ca",
            target_language="python",
            status=status,
            selected_capability="CAP-011",
            time_taken_seconds=1.0,
        )
        for i, status in enumerate(statuses)
    ])


def test_benchmark_requires_meaningful_improvement():
    benchmark = SelfImprovementBenchmark(minimum_score_delta=0.05)
    result = benchmark.measure(
        capability_id="CAP-011",
        baseline_experience=_log(["failure"] * 5),
        post_evolution_experience=_log(["success"] * 5),
        evolution_result={"promoted": True, "registered": True},
    )
    assert result.promotion_succeeded is True
    assert result.score_delta > 0.05
    assert result.improved is True


def test_benchmark_rejects_improvement_without_promotion():
    benchmark = SelfImprovementBenchmark(minimum_score_delta=0.01)
    result = benchmark.measure(
        capability_id="CAP-011",
        baseline_experience=_log(["failure"] * 5),
        post_evolution_experience=_log(["success"] * 5),
        evolution_result={"promoted": False, "registered": False},
    )
    assert result.promotion_succeeded is False
    assert result.improved is False


def test_benchmark_run_uses_governed_result_and_post_evidence():
    benchmark = SelfImprovementBenchmark(minimum_score_delta=0.05)
    called = []

    def evolve():
        called.append(True)
        return {"capability_id": "CAP-011", "promoted": True}

    result = benchmark.run(
        capability_id="CAP-011",
        baseline_experience=_log(["failure"] * 5),
        evolution=evolve,
        post_evolution_experience_factory=lambda _: _log(["success"] * 5),
    )
    assert called == [True]
    assert result.improved is True
