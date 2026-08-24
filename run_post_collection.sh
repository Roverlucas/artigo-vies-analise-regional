#!/bin/bash
# Post-collection chain: waits for Phase B + gemini collections to finish, then
# runs the full judging + reliability + analysis sequence. No API contention:
# the panel judges (DeepSeek, Cohere) only start AFTER collection frees those APIs.
set +e
cd ~/artigo-vies-analise-regional

echo "[chain] waiting for collections (run_confirmatory) to finish..."
while pgrep -f "code.benchmark.run_confirmatory" >/dev/null 2>&1; do sleep 60; done
echo "[chain] collections done at $(date). Starting judging."

# 1. Judge the 10 new countries with the primary judge (gpt5_mini / OpenAI)
echo "[chain] === primary judge on new countries ==="
python3 -u -m code.analysis.run_judge_confirmatory 2>&1 | grep -vE "MLX"

# 2. Panel judges on the stratified reliability sample (seed 42 -> same items)
echo "[chain] === panel judge: deepseek_v3 (DeepSeek) ==="
python3 -u -m code.analysis.validate_judge_agreement --judge-model deepseek_v3 --sample-size 800 --seed 42 2>&1 | grep -vE "MLX"
echo "[chain] === panel judge: command_rp (Cohere) ==="
python3 -u -m code.analysis.validate_judge_agreement --judge-model command_rp --sample-size 800 --seed 42 2>&1 | grep -vE "MLX"

# 3. Recompute 5-judge reliability + corpus mechanism
echo "[chain] === 5-judge panel reliability ==="
python3 -u -m code.analysis.krippendorff_3judges 2>&1 | grep -vE "MLX"
echo "[chain] === H4 corpus mechanism (updated data) ==="
python3 -u -m code.analysis.h4_corpus_mechanism 2>&1 | grep -vE "MLX"

echo "[chain] DONE at $(date)."
