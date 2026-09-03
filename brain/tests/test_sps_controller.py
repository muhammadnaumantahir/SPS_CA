from brain.sps_controller import SPSBrainController, SPSDecision


def test_controller_parses_strategy():
    controller = SPSBrainController()
    data = controller._parse('{"strategy":"create","reason":"capability gap","task_instruction":"add a parser","success_criteria":["works"]}')
    decision = controller._decision(data)
    assert isinstance(decision, SPSDecision)
    assert decision.strategy == "create"
    assert decision.task_instruction == "add a parser"
    assert decision.success_criteria == ("works",)


def test_controller_rejects_unknown_strategy_to_replan():
    controller = SPSBrainController()
    decision = controller._decision({"strategy":"invent_new_strategy","reason":"x"})
    assert decision.strategy == "replan"
