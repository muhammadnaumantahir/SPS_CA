#!/usr/bin/env bash
set -euo pipefail

# SPS-CA Google Colab bootstrap.
# Safe to run after every `git pull`.
# Usage: bash scripts/colab_setup.sh [MODEL]

MODEL="${1:-${SPS_CA_MODEL:-qwen2.5-coder:7b}}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "== SPS-CA Colab setup =="
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if ! command -v ollama >/dev/null 2>&1; then
  echo "Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
fi

echo "Ollama: $(ollama --version)"

# Start Ollama in the background if it is not already responding.
if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  nohup ollama serve > /tmp/ollama.log 2>&1 &
  for i in {1..30}; do
    if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
fi

if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "ERROR: Ollama API did not start. Log: /tmp/ollama.log"
  exit 1
fi

echo "Pulling model: $MODEL"
ollama pull "$MODEL"

echo "Installed models:"
ollama list

echo "== SPS-CA setup complete =="
echo "Ollama API: http://127.0.0.1:11434"
echo "Model: $MODEL"
