import os
import sys


def ollama_test(model: str) -> str:
    import requests

    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={"model": model, "prompt": "Say: SPS-CA model connection OK", "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"]


def openai_test(model: str) -> str:
    from openai import OpenAI

    response = OpenAI().responses.create(
        model=model,
        input="Say: SPS-CA model connection OK",
    )
    return response.output_text


def anthropic_test(model: str) -> str:
    from anthropic import Anthropic

    response = Anthropic().messages.create(
        model=model,
        max_tokens=64,
        messages=[{"role": "user", "content": "Say: SPS-CA model connection OK"}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


mode = os.getenv("SPS_CA_MODEL_MODE", "ollama").lower()
model = os.getenv("SPS_CA_MODEL", "qwen2.5-coder:7b")

if mode == "ollama":
    result = ollama_test(model)
elif mode == "openai":
    result = openai_test(model)
elif mode in {"anthropic", "claude"}:
    result = anthropic_test(model)
else:
    raise SystemExit(f"Unsupported SPS_CA_MODEL_MODE: {mode}")

print(result)
