from brain import Brain


def test_detect_python_by_syntax():
    lang, confidence, evidence = Brain.detect_language("def add(a, b):\n    return a + b", "fix it", "main.py")
    assert lang == "python"
    assert confidence >= 0.9
    assert "filename" in evidence


def test_detect_typescript_from_syntax():
    lang, confidence, _ = Brain.detect_language("const add = (a: number, b: number): number => a + b", "fix it", "snippet.txt")
    assert lang == "typescript"
    assert confidence > 0.6


def test_unknown_when_no_code_signal():
    lang, confidence, _ = Brain.detect_language("hello world", "do something", "snippet.txt")
    assert lang == "unknown"
    assert confidence <= 0.25
