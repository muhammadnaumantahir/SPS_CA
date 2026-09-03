from pathlib import Path


def test_dashboard_snapshot_has_metrics_architecture_analytics_and_activity(monkeypatch):
    import ui.web_app as web_app

    class FakeSessions:
        def list(self):
            return [
                {"id": "s2", "title": "Newer", "updated_at": "2026-09-03T12:00:00+00:00"},
                {"id": "s1", "title": "Older", "updated_at": "2026-09-03T11:00:00+00:00"},
            ]

    class FakeEvolution:
        def list_events(self, limit=200):
            return [
                {"event_type": "disagreement", "timestamp": "2026-09-03T12:01:00+00:00", "reasoning": "pattern found"},
                {"event_type": "capability_created", "timestamp": "2026-09-03T12:02:00+00:00", "created_capability_id": "CAP-011"},
            ]

    monkeypatch.setattr(web_app, "sessions", FakeSessions())
    monkeypatch.setattr(web_app, "evolution", FakeEvolution())
    monkeypatch.setattr(
        web_app,
        "capability_directory",
        lambda: [
            {"id": "CAP-001", "name": "Code Generation", "generated": False, "usable": True, "reuse_count": 4},
            {"id": "CAP-011", "name": "Special Fix", "generated": True, "usable": False, "reuse_count": 2},
        ],
    )

    snapshot = web_app.dashboard_data()

    assert snapshot["metrics"] == {
        "layers": 10,
        "core_capabilities": 2,
        "active_capabilities": 1,
        "conversations": 2,
        "evolution_events": 2,
    }
    assert len(snapshot["architecture"]["layers"]) == 10
    assert {c["id"] for c in snapshot["capabilities"]} == {"CAP-001", "CAP-011"}
    assert snapshot["evolution"][0]["event_type"] == "capability_created"
    assert snapshot["activity"][0]["type"] == "evolution"


def test_dashboard_empty_runtime_state_is_valid(monkeypatch):
    import ui.web_app as web_app

    class EmptySessions:
        def list(self):
            return []

    class EmptyEvolution:
        def list_events(self, limit=200):
            return []

    monkeypatch.setattr(web_app, "sessions", EmptySessions())
    monkeypatch.setattr(web_app, "evolution", EmptyEvolution())
    monkeypatch.setattr(web_app, "capability_directory", lambda: [])

    snapshot = web_app.dashboard_data()

    assert snapshot["metrics"]["conversations"] == 0
    assert snapshot["metrics"]["evolution_events"] == 0
    assert snapshot["capabilities"] == []
    assert snapshot["evolution"] == []
    assert snapshot["activity"] == []
    assert len(snapshot["architecture"]["layers"]) == 10


def test_delete_endpoint_contract_and_ui_confirmation_guard():
    web_app_source = Path("ui/web_app.py").read_text(encoding="utf-8")
    app_source = Path("ui/web/app.js").read_text(encoding="utf-8")
    html_source = Path("ui/web/index.html").read_text(encoding="utf-8")

    assert 'if not path.startswith("/api/sessions/")' in web_app_source
    assert 'sessions.delete(path.rsplit("/",1)[-1])' in web_app_source
    assert 'window.confirm(`Delete' in app_source
    assert "event.stopPropagation()" in app_source
    assert "const wasActive=state.sessionId===id" in app_source
    assert "await newChat()" in app_source
    assert "class=\"session-delete\"" in html_source


def test_dashboard_ui_contains_required_control_center_sections():
    html = Path("ui/web/index.html").read_text(encoding="utf-8")
    js = Path("ui/web/app.js").read_text(encoding="utf-8")

    for label in ("SPS Overview", "Architecture graph", "Capability analytics", "Evolution activity", "Live activity"):
        assert label in html
    for marker in ("User", "BRAIN", "CAPABILITY REGISTRY", "EXECUTION", "renderMetricCards", "renderBars", "renderEvolutionFlow"):
        assert marker in js


def test_chat_insights_and_dashboard_navigation_are_wired():
    js = Path("ui/web/app.js").read_text(encoding="utf-8")
    assert "renderChatInsights()" in js
    assert "loadDashboard()" in js
    assert "if(view==='overview') loadDashboard()" in js
    assert "language" in js and "capabilities" in js and "Evolution" in js
