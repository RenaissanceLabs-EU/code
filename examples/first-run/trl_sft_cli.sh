#!/usr/bin/env bash
# Same recipe as train_sft.py through the TRL command line (flag names read from trl/scripts/sft.py,
# SFTConfig and ModelConfig of TRL 1.18.2 on 2026-11-25). Not executed by the authors.
# Note: the CLI default for --dtype is float32, so pass bfloat16 explicitly on a GPU.
set -euo pipefail
trl sft \
  --model_name_or_path Qwen/Qwen2.5-Coder-1.5B-Instruct \
  --dataset_name data/oci-sft-4k \
  --dataset_train_split train \
  --dataset_test_split validation \
  --dtype bfloat16 \
  --use_peft --lora_r 32 --lora_alpha 64 --lora_dropout 0.05 --lora_target_modules all-linear \
  --learning_rate 1e-4 --num_train_epochs 2 \
  --per_device_train_batch_size 4 --gradient_accumulation_steps 8 \
  --lr_scheduler_type cosine --warmup_steps 0.05 --weight_decay 0.0 \
  --max_length 2048 \
  --eval_strategy steps --eval_steps 50 --save_steps 50 --save_total_limit 2 \
  --seed 42 --output_dir out/sft-lora
# Equivalent YAML: put the same keys (without the leading dashes) in sft_config.yaml and run
#   trl sft --config sft_config.yaml
