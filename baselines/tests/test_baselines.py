from baselines.baseline_a_naive_llm import BaselineA_NaiveLLM
from baselines.baseline_b_coding_agent import BaselineB_CodingAgent
from baselines.runner import ResultStore

class FakeLLM:
    def __init__(self):
        self.prompts = []

    def __call__(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return "FAKE_RESPONSE"

def test_baseline_a_uses_same_interface_and_no_tools(tmp_path):
    llm = FakeLLM()
    store = ResultStore(tmp_path / "a.jsonl")
    agent = BaselineA_NaiveLLM(llm, store=store)
    result = agent.process_request("fix bug", "def broken(): pass", "project_a")

    assert result.baseline_id == "baseline_a_naive_llm"
    assert result.model == "qwen2.5-coder:7b"
    assert result.tool_calls == []
    assert result.response == "FAKE_RESPONSE"
    assert "fix bug" in llm.prompts[0]
    assert (tmp_path / "a.jsonl").read_text(encoding="utf-8").count("FAKE_RESPONSE") == 1

def test_baseline_b_uses_tools_and_same_interface(tmp_path):
    llm = FakeLLM()
    store = ResultStore(tmp_path / "b.jsonl")
    agent = BaselineB_CodingAgent(llm, store=store)
    result = agent.process_request("fix bug", "line one\nline two", "project_b")

    assert result.baseline_id == "baseline_b_coding_agent"
    assert result.model == "qwen2.5-coder:7b"
    assert result.tool_calls == ["analyze_code", "syntax_check", "run_tests"]
    assert result.response == "FAKE_RESPONSE"
    assert "TOOL FINDINGS" in llm.prompts[0]

def test_both_baselines_accept_same_callable_and_model():
    llm = FakeLLM()
    a = BaselineA_NaiveLLM(llm)
    b = BaselineB_CodingAgent(llm)
    assert a.model == b.model == "qwen2.5-coder:7b"
    assert a.process_request("x", "y", "p").project == "p"
    assert b.process_request("x", "y", "p").project == "p"
