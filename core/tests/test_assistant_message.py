from core.assistant_service import SpsAssistantService


def test_assistant_message_keeps_resulting_source_out_of_chat_bubble():
    message = SpsAssistantService._assistant_message(
        "code_modification",
        "validation was preserved",
        [{"status": "completed", "name": "Code Modification"}],
        True,
        "print('this belongs in the working-code panel')\n",
        "python",
    )

    assert "```" not in message
    assert "print('this belongs in the working-code panel')" not in message
    assert "Done. I applied code modification to the code." in message
