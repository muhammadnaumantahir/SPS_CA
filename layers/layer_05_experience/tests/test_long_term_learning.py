from layers.layer_05_experience.long_term_learning import LongTermLearningStore
from layers.layer_05_experience.models import Task


def test_long_term_store_rebuilds_and_persists(tmp_path):
    path = tmp_path / "learning.json"
    store = LongTermLearningStore(path)
    tasks = [
        Task(id="1", user_request="a", target_language="python", selected_capability="CAP-002", status="success"),
        Task(id="2", user_request="b", target_language="python", selected_capability="CAP-002", status="failure", failure_category="routing"),
        Task(id="3", user_request="c", target_language="javascript", selected_capability="CAP-001", status="success"),
    ]
    data = store.rebuild(tasks)
    assert data["total_tasks"] == 3
    assert data["capabilities"]["CAP-002"]["uses"] == 2
    assert data["failure_patterns"]["routing"] == 1
    assert store.context()["total_tasks"] == 3
