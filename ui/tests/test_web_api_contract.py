from pathlib import Path


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
    assert 'class="session-delete"' in html_source


def test_navigation_removes_overview_and_keeps_core_views():
    html = Path("ui/web/index.html").read_text(encoding="utf-8")

    assert 'data-view="overview"' not in html
    assert 'id="view-overview"' not in html
    for view in ("chat", "architecture", "capabilities", "evolution"):
        assert f'data-view="{view}"' in html
        assert f'id="view-{view}"' in html


def test_capability_analysis_is_embedded_in_capabilities_view():
    html = Path("ui/web/index.html").read_text(encoding="utf-8")

    capabilities_start = html.index('id="view-capabilities"')
    evolution_start = html.index('id="view-evolution"')
    capabilities_view = html[capabilities_start:evolution_start]

    assert 'Capability analysis' in capabilities_view
    assert 'Seed vs generated population' in capabilities_view
    assert 'id="capabilityAnalytics"' in capabilities_view
    assert '/api/capabilities' in html
    assert 'showCapability' in html
    assert '/api/dashboard' not in html


def test_architecture_is_the_single_architecture_navigation_surface():
    html = Path("ui/web/index.html").read_text(encoding="utf-8")

    assert html.count('data-view="architecture"') == 1
    assert html.count('id="view-architecture"') == 1
    assert 'Architecture graph' not in html
    assert '10-LAYER SPS PIPELINE' not in html


def test_overview_dashboard_api_is_removed():
    source = Path("ui/web_app.py").read_text(encoding="utf-8")
    assert "def dashboard_data" not in source
    assert 'path=="/api/dashboard"' not in source


def test_capabilities_api_contract_remains_available():
    source = Path("ui/web_app.py").read_text(encoding="utf-8")
    assert 'path == "/api/capabilities"' in source
    assert 'capability_directory()' in source


def test_chat_insights_and_core_navigation_are_wired():
    js = Path("ui/web/app.js").read_text(encoding="utf-8")
    assert "renderChatInsights()" in js
    assert "if(view==='architecture') loadArchitecture()" in js
    assert "if(view==='capabilities') loadCapabilities()" in js
    assert "if(view==='evolution') refreshEvolution()" in js
    assert "language" in js and "capabilities" in js and "Evolution" in js


def test_explicit_target_language_aliases_are_detected():
    import sys
    sys.path.insert(0, str(Path(".").resolve()))
    from ui.web_app import requested_target_language

    assert requested_target_language("generate code in JS") == "javascript"
    assert requested_target_language("write this in JavaScript") == "javascript"
    assert requested_target_language("create a Python program") == "python"
    assert requested_target_language("convert this to Java") == "java"
    assert requested_target_language("explain Python") == ""


def test_historical_capability_provenance_is_exposed():
    source = Path("ui/web_app.py").read_text(encoding="utf-8")
    metadata = Path("capabilities/generated/cap_011_parse_error_handler/metadata.json").read_text(encoding="utf-8")
    html = Path("ui/web/index.html").read_text(encoding="utf-8")

    assert "generated_metadata" in source
    assert "historical_migration" in source
    assert "historical_migration" in metadata
    assert "source_commit" in metadata
    assert "not created by a current-user disagreement event" in html
