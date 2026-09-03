from layers.layer_05_experience.experience_log import ExperienceLog
from layers.layer_05_experience.long_term_learning import LongTermLearningStore
from layers.layer_05_experience.models import Task


def test_rebuild_accepts_experience_log(tmp_path):
    log = ExperienceLog()
    log.add_task(
        Task(
            id="task_001",
            user_request="Add logging",
            target_project="chat",
            target_language="python",
            status="success",
            selected_capability="CAP-002",
            outcome="updated source",
        )
    )

    store = LongTermLearningStore(tmp_path / "long_term_learning.json")
    result = store.rebuild(log)

    assert result["total_tasks"] == 1
    assert result["capabilities"]["CAP-002"]["uses"] == 1
    assert result["capabilities"]["CAP-002"]["success_rate"] == 1.0
