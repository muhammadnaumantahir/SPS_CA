from ui.web_app import build_persisted_turn_data


def test_persisted_turn_data_does_not_reference_parent_payload():
    payload = {
        "intent": "code_modification",
        "conversation": [{"role": "assistant", "content": "ok"}],
        "session": {"id": "abc"},
    }
    metadata = build_persisted_turn_data(payload)
    metadata["status"] = "recorded"

    assert "conversation" not in metadata
    assert "session" not in metadata
    assert payload["conversation"] == [{"role": "assistant", "content": "ok"}]

    persisted = [{"role": "assistant", "content": "ok", "turnData": metadata}]
    payload["conversation"] = persisted
    import json
    json.dumps(payload)
