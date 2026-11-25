#!/usr/bin/env bash
# Evaluation before and after. Use a separate virtual environment from training.
# Commands follow the EvalPlus README (read 2026-11-25) and eval_heldout.py. Not executed by the authors.
set -euo pipefail

BASE=Qwen/Qwen2.5-Coder-1.5B-Instruct
TUNED=./out/merged          # output of merge_push.py
BACKEND=${BACKEND:-vllm}    # vllm needs a GPU; use hf on CPU. Use the SAME backend for both models.

# --- 0. environment (evaluation) ---
# python3.12 -m venv .venv-eval && source .venv-eval/bin/activate
# pip install "evalplus[vllm]==0.3.1"      # for --backend vllm
# pip install "evalplus==0.3.1"            # for --backend hf (runs on CUDA if present, else CPU)
# pip freeze > runs/eval-requirements.txt  # record what pip resolved

# --- 1. EvalPlus, README one-liners (generate and execute locally) ---
# evalplus.evaluate --model "$BASE" --dataset humaneval --backend "$BACKEND" --greedy
# evalplus.evaluate --model "$BASE" --dataset mbpp      --backend "$BACKEND" --greedy

# --- 1b. EvalPlus, safer: generate locally, execute inside the official Docker image (README). The README uses :latest; the v0.3.1 tag exists on Docker Hub (checked 2026-11-25) and is pinned here. ---
sample_id() {  # mirrors evalplus/codegen.py: model.strip("./").replace("/", "--") + _{backend}_temp_0.0
  local m; m=$(echo "$1" | sed -e 's#^[./]*##' -e 's#[./]*$##' -e 's#/#--#g')
  echo "${m}_${BACKEND}_temp_0.0"
}
for MODEL in "$BASE" "$TUNED"; do
  for DATASET in humaneval mbpp; do
    evalplus.codegen --model "$MODEL" --dataset "$DATASET" --backend "$BACKEND" --greedy
    docker run --rm -v "$(pwd)/evalplus_results:/app" ganler/evalplus:v0.3.1 \
      evalplus.evaluate --dataset "$DATASET" \
      --samples "/app/${DATASET}/$(sample_id "$MODEL").jsonl"
  done
done
# The evaluate output prints two pass@1 lines per dataset: the base tests ("humaneval", "mbpp") and
# base plus extra tests ("humaneval+", "mbpp+"). The base-test line is the regression check.

# --- 2. held-out slice of the training dataset, executed in Docker (python:3.12-slim) ---
mkdir -p runs
python eval_heldout.py reference --data data/oci-heldout/heldout.jsonl --out runs/ref_gen.jsonl
python eval_heldout.py score --gen runs/ref_gen.jsonl --data data/oci-heldout/heldout.jsonl --out runs/ref_score.jsonl
#   -> the reference solutions must pass (about 100 percent). Drop any row that fails in your sandbox.
python eval_heldout.py generate --model "$BASE"  --data data/oci-heldout/heldout.jsonl --out runs/base_gen.jsonl
python eval_heldout.py generate --model "$TUNED" --data data/oci-heldout/heldout.jsonl --out runs/tuned_gen.jsonl
python eval_heldout.py score --gen runs/base_gen.jsonl  --data data/oci-heldout/heldout.jsonl --out runs/base_score.jsonl
python eval_heldout.py score --gen runs/tuned_gen.jsonl --data data/oci-heldout/heldout.jsonl --out runs/tuned_score.jsonl
python eval_heldout.py compare --a runs/base_score.jsonl --b runs/tuned_score.jsonl

# --- 3. general sanity prompts (12 prompts, greedy, regex checks, also flags answers that never stop) ---
python eval_heldout.py sanity --model "$BASE"  --out runs/base_sanity.json
python eval_heldout.py sanity --model "$TUNED" --out runs/tuned_sanity.json
