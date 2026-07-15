#!/bin/bash
# Tier-2 LLM pilot runner — follows PREREGISTRATION_llm.md exactly.
# Prereq (once):  brew install ollama && ollama serve &  && ollama pull llama3.1:8b
set -e
cd "$(dirname "$0")"
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-http://localhost:11434/v1}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-ollama}"
MODEL="${MODEL:-llama3.1:8b}"
ITEMS="items_amazon_google.jsonl"

case "${1:-}" in
  smoke)   # 20 calls, parse-rate check only (results discarded per prereg)
    python3 llm_respondent_harness.py --items "$ITEMS" --model "$MODEL" --temperature 0.7 --n-per-pair 5 ;;
  stage1)  # interim look: T=0.7, n=100/pair (400 calls, ~15-30 min on M4)
    python3 llm_respondent_harness.py --items "$ITEMS" --model "$MODEL" --temperature 0.7 --n-per-pair 100 --seed 42 ;;
  stage2)  # full grid: T in {0.3,0.7,1.0}, n=400/pair (4,800 calls, ~2-4 h)
    for T in 0.3 0.7 1.0; do
      python3 llm_respondent_harness.py --items "$ITEMS" --model "$MODEL" --temperature "$T" --n-per-pair 400 --seed 4242
    done ;;
  analyse) shift; python3 llm_respondent_harness.py --analyse "${@:-runs/log_*.jsonl}" ;;
  *) echo "usage: ./run_pilot.sh {smoke|stage1|stage2|analyse [logs...]}"; exit 1 ;;
esac
