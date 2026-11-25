---
license: apache-2.0
base_model: Qwen/Qwen2.5-Coder-1.5B-Instruct
datasets:
  - nvidia/OpenCodeInstruct
library_name: transformers
pipeline_tag: text-generation
tags:
  - code
  - lora
  - sft
  - trl
  - peft
model-index:
  - name: YOUR-MODEL-NAME
    results:
      - task: {type: text-generation}
        dataset: {name: HumanEval+ (EvalPlus), type: evalplus/humanevalplus}
        metrics: [{type: pass@1, value: FILL_FROM_YOUR_RUN, name: "greedy, EvalPlus 0.3.1"}]
      - task: {type: text-generation}
        dataset: {name: MBPP+ (EvalPlus), type: evalplus/mbppplus}
        metrics: [{type: pass@1, value: FILL_FROM_YOUR_RUN, name: "greedy, EvalPlus 0.3.1"}]
---
# YOUR-MODEL-NAME

LoRA fine-tune of Qwen/Qwen2.5-Coder-1.5B-Instruct on about 4,000 execution-checked examples from
nvidia/OpenCodeInstruct (CC BY 4.0, NVIDIA). The adapter is merged into the weights.

## Intended use
Research and learning: a small, reproducible example of supervised fine-tuning for code. Not evaluated for safety.

## Training data
- Source: nvidia/OpenCodeInstruct, revision 8f3ba5bafe4d6e8db46082cf7ae6741bc370604d.
- Filter: all 10 generated unit tests pass, LLM judge 5 of 5 on all criteria, python block present,
  no network or file access, at most 6000 characters, no 10-word overlap with HumanEval or MBPP.
- Counts: FILL (train / validation / held-out). Split by hash of row id, seed 42.
- Generators named by the dataset authors: Qwen2.5-Coder-32B-Instruct and Qwen2.5-32B-Instruct (both Apache-2.0).

## Training
TRL 1.18.2, PEFT 0.22.0, transformers 5.24.1. LoRA r=32, alpha=64, dropout 0.05, all linear layers.
Learning rate 1e-4, cosine, 5 percent warmup, 2 epochs, effective batch 32, max length 2048, seed 42.
Hardware, wall-clock time and peak memory: FILL (measured).

## Evaluation (greedy, same backend for both rows)
| Model | HumanEval | HumanEval+ | MBPP | MBPP+ | Held-out slice (strict pass@1) | Sanity prompts |
|---|---|---|---|---|---|---|
| Base | FILL | FILL | FILL | FILL | FILL | FILL |
| This model | FILL | FILL | FILL | FILL | FILL | FILL |
Paired McNemar p-values and the run logs: FILL. Differences under about 4 points on HumanEval+ are within noise.

## Limitations
Small training set; synthetic data written by a larger model; tests were also model-written and can be wrong;
benchmark scores can move with decoding settings and backend.

## Attribution
Data: NVIDIA, OpenCodeInstruct, CC BY 4.0 (https://huggingface.co/datasets/nvidia/OpenCodeInstruct).
Base model: Qwen/Qwen2.5-Coder-1.5B-Instruct, Apache-2.0.
