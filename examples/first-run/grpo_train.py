"""EXPERIMENTAL stretch recipe: GRPO with an execution reward on a small, filtered task pool.

Config names read from TRL 1.18.2 source (trl/trainer/grpo_config.py) on 2026-11-25. Not executed.
Prerequisite: a pool of prompts with `reward_tests` (drive the reward) and `holdout_tests` (never used in
training, check them after training to detect reward hacking). prepare_data.py --rl-pool 3000 builds it;
then keep only prompts the starting model solves sometimes but not always (pass rate strictly between 0 and 1
over 8 samples), which you measure with the starting model first.
"""
from datasets import load_dataset
from peft import LoraConfig
from trl import GRPOConfig, GRPOTrainer

from reward_fn import unit_test_reward

ds = load_dataset("json", data_files="data/oci-rl-pool/pool_filtered.jsonl", split="train")
ds = ds.remove_columns([c for c in ds.column_names if c not in ("prompt", "reward_tests")])

args = GRPOConfig(
    output_dir="out/grpo-lora",
    num_generations=8,                 # completions per prompt (group size); default 8
    per_device_train_batch_size=8,     # num_processes * this * accumulation must divide by num_generations
    gradient_accumulation_steps=2,     # 16 completions per optimizer step = 2 prompts
    max_completion_length=768,         # default 512; code answers with an explanation need more
    temperature=1.0,                   # default 1.0: sampling diversity is the learning signal
    learning_rate=1e-5,                # LoRA; the TRL default of 1e-6 is for full fine-tuning. Untested guess.
    beta=0.0,                          # default: no KL term, no reference model
    loss_type="dapo",                  # default in 1.18.2
    scale_rewards="group",             # default
    mask_truncated_completions=True,   # exclude answers cut off at max_completion_length from the loss
    num_train_epochs=1,
    logging_steps=1,
    save_steps=50,
    log_completions=True,              # print sample completions: read them to catch reward hacking
    use_vllm=False,                    # True with vllm_mode="colocate" is faster on an 80 GB GPU
    bf16=True,
    seed=42,
    report_to="none",
    model_init_kwargs={"dtype": "bfloat16"},
)

trainer = GRPOTrainer(
    model="out/merged",                # start from the SFT model, or Qwen/Qwen2.5-Coder-1.5B-Instruct
    reward_funcs=unit_test_reward,
    args=args,
    train_dataset=ds,
    peft_config=LoraConfig(r=32, lora_alpha=64, lora_dropout=0.0, target_modules="all-linear",
                           task_type="CAUSAL_LM"),
)
trainer.train()
trainer.save_model(args.output_dir)
