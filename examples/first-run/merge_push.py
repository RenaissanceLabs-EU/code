"""Merge a LoRA adapter into its base model, save the merged weights, optionally push to the Hub.

  python merge_push.py --adapter out/sft-lora --out out/merged
  python merge_push.py --adapter out/sft-lora --out out/merged --push your-name/qwen2.5-coder-1.5b-oci-lora
"""
import argparse

import torch
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--push", default=None, help="Hub repo id, for example user/model-name")
    a = ap.parse_args()

    # Loads the base model named in adapter_config.json and attaches the adapter.
    model = AutoPeftModelForCausalLM.from_pretrained(a.adapter, dtype=torch.bfloat16)
    # merge_and_unload is not in place: use the returned model (PEFT docs). safe_merge checks for NaN.
    merged = model.merge_and_unload(safe_merge=True)
    base_name = model.peft_config["default"].base_model_name_or_path
    try:
        tok = AutoTokenizer.from_pretrained(a.adapter)
    except Exception:  # adapter folder has no tokenizer files: use the base model's
        tok = AutoTokenizer.from_pretrained(base_name)
    merged.save_pretrained(a.out, safe_serialization=True)
    tok.save_pretrained(a.out)
    print("saved merged model to", a.out)
    if a.push:
        # Needs `hf auth login` or HF_TOKEN. Write README.md (the model card) into the repo as well.
        merged.push_to_hub(a.push)
        tok.push_to_hub(a.push)
        print("pushed to https://huggingface.co/" + a.push)


if __name__ == "__main__":
    main()
