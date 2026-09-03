from ui.session_store import SessionStore


def test_session_create_save_reload(tmp_path):
    store = SessionStore(tmp_path / "sessions.json")
    created = store.create()
    assert created["title"] == "New chat"
    saved = store.save(created["id"], [{"role": "user", "content": "hello"}], "print('x')", "main.py", "python", 0.98, "qwen")
    assert saved["conversation"][0]["content"] == "hello"
    assert store.get(created["id"])["code"] == "print('x')"
    assert store.list()[0]["id"] == created["id"]


def test_corrupt_store_recovers(tmp_path):
    path = tmp_path / "sessions.json"
    path.write_text("not-json", encoding="utf-8")
    store = SessionStore(path)
    assert store.list() == []
    assert store.create()["id"]
