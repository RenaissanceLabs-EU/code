"""LoRA supervised fine-tuning of Qwen2.5-Coder-1.5B-Instruct on the filtered OpenCodeInstruct subset.

Verified against TRL 1.18.2, PEFT 0.22.0, transformers 5.24.1 (API names read from source on 2026-11-25).
Not executed by the authors of this recipe: treat the first run as a smoke test (--max-steps 5).

  python train_sft.py                                  # primary: 1.5B model, ~250 optimizer steps
  python train_sft.py --model Qwen/Qwen2.5-Coder-0.5B-Instruct --rank 16 --batch 2 --accum 16   # fallback
"""
import argparse

import torch
from datasets import load_dataset
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    ap.add_argument("--data", default="data/oci-sft-4k")
    ap.add_argument("--out", default="out/sft-lora")
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--epochs", type=float, default=2.0)
    ap.add_argument("--rank", type=int, default=32)
    ap.add_argument("--batch", type=int, default=4, help="per-device micro batch size")
    ap.add_argument("--accum", type=int, default=8, help="gradient accumulation steps")
    ap.add_argument("--max-length", type=int, default=2048)
    ap.add_argument("--max-steps", type=int, default=-1, help="set 5 for a smoke test")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--eos-token", default=None, help="for BASE models with a chat template, use <|im_end|>")
    a = ap.parse_args()

    # bf16 only where the hardware supports it; CPU and Apple silicon run in float32 (slower, more memory).
    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    dtype = torch.bfloat16 if use_bf16 else torch.float32

    # Rows are conversational prompt-completion: {"prompt": [user msg], "completion": [assistant msg]}.
    data = load_dataset("json", data_files={"train": f"{a.data}/train.jsonl",
                                            "validation": f"{a.data}/validation.jsonl"})

    peft_config = LoraConfig(
        r=a.rank,
        lora_alpha=2 * a.rank,        # alpha = 2r, Biderman et al. 2024, Sec. 4.7
        lora_dropout=0.05,            # QLoRA appendix A.1: useful for small models
        target_modules="all-linear",  # QLoRA Sec. 4 and Biderman Fig. 7: attention-only underperforms
        task_type="CAUSAL_LM",
    )

    args = SFTConfig(
        output_dir=a.out,
        num_train_epochs=a.epochs,
        max_steps=a.max_steps,
        per_device_train_batch_size=a.batch,
        per_device_eval_batch_size=a.batch,
        gradient_accumulation_steps=a.accum,
        learning_rate=a.lr,
        lr_scheduler_type="cosine",
        warmup_steps=0.05,            # transformers 5.x: a float below 1 is a ratio of total steps
        weight_decay=0.0,
        max_grad_norm=1.0,
        eos_token=a.eos_token,        # None keeps the tokenizer eos (<|im_end|> for the Instruct models)
        max_length=a.max_length,      # SFTConfig name for the sequence limit (default 1024)
        packing=False,                # bfd packing needs flash-attention padding-free mode
        completion_only_loss=True,    # loss on the assistant answer only (default for prompt-completion)
        bf16=use_bf16,
        fp16=False,
        # gradient checkpointing is on by default in SFTConfig; leave it, memory matters more than speed
        model_init_kwargs={"dtype": dtype},
        eval_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=50,
        save_total_limit=2,
        logging_steps=10,
        seed=a.seed,
        data_seed=a.seed,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=a.model,
        args=args,
        train_dataset=data["train"],
        eval_dataset=data["validation"],
        peft_config=peft_config,
    )
    trainer.train()
    trainer.save_model(a.out)  # saves the adapter only; merge with merge_push.py


if __name__ == "__main__":
    main()
