from layers.layer_08_evolution import EvolutionExecutionAuthority


def test_execution_authority_defaults_to_deny(monkeypatch):
    monkeypatch.delenv("SPS_CA_AUTO_EVOLVE", raising=False)
    monkeypatch.delenv("SPS_CA_AUTO_EVOLVE_MAX_ACTIONS", raising=False)
    authority = EvolutionExecutionAuthority.from_environment()
    allowed, reason = authority.authorize(1)
    assert authority.enabled is False
    assert allowed is False
    assert "disabled" in reason


def test_execution_authority_allows_one_explicit_action(monkeypatch):
    monkeypatch.setenv("SPS_CA_AUTO_EVOLVE", "true")
    monkeypatch.setenv("SPS_CA_AUTO_EVOLVE_MAX_ACTIONS", "1")
    authority = EvolutionExecutionAuthority.from_environment()
    allowed, reason = authority.authorize(1)
    assert authority.enabled is True
    assert authority.max_actions_per_cycle == 1
    assert allowed is True
    assert "authorized" in reason


def test_execution_authority_caps_action_count(monkeypatch):
    monkeypatch.setenv("SPS_CA_AUTO_EVOLVE", "1")
    monkeypatch.setenv("SPS_CA_AUTO_EVOLVE_MAX_ACTIONS", "2")
    authority = EvolutionExecutionAuthority.from_environment()
    allowed, _ = authority.authorize(3)
    assert allowed is False
