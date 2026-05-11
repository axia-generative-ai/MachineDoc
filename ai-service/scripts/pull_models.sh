#!/usr/bin/env bash
# Pull the Ollama models required by the MachineDoc AI service.
#
# Defaults track app/config.py:
#   - LLM:       qwen2.5:3b (smaller / faster than the original qwen3.5:9b;
#                see project_session_progress / config.py for context).
#   - Embedding: nomic-embed-text (768d). bge-m3 was deprecated after a
#                reproducible Ollama NaN failure on plain English input.
#
# Override either via environment:
#   OLLAMA_MODEL=qwen3.5:9b EMBEDDING_MODEL=bge-m3 bash scripts/pull_models.sh
#
# Usage:
#   bash scripts/pull_models.sh

set -euo pipefail

LLM_MODEL="${OLLAMA_MODEL:-qwen2.5:3b}"
EMBED_MODEL="${EMBEDDING_MODEL:-nomic-embed-text}"

if ! command -v ollama >/dev/null 2>&1; then
    echo "ERROR: ollama CLI not found on PATH." >&2
    echo "Install Ollama from https://ollama.com/download and retry." >&2
    exit 1
fi

echo ">>> Pulling LLM: ${LLM_MODEL}"
ollama pull "${LLM_MODEL}"

echo ">>> Pulling embedding model: ${EMBED_MODEL}"
ollama pull "${EMBED_MODEL}"

echo ">>> Installed models:"
ollama list
