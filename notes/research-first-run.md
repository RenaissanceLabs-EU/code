# Research pass: first training recipe (2026-11-25)

Feeds page 6 (reproducible training recipes) and parts of pages 4 and 7. Output: `data/first-run.json` (full scripts under `files`, hyperparameters with sources, hardware tiers, evaluation plan, stretch recipe). This note explains the decisions and lists what could not be verified.

Rules followed: nothing installed, no model or dataset downloaded, no training run. Versions, API names and commands were read from PyPI JSON, GitHub source at pinned tags, the Hugging Face API and the papers on 2026-11-25. Every compute, memory, time and outcome number is an estimate with its basis stated. Only stdlib-only helpers were run (reward self-test, sandbox runner, dataset filter on 500 real rows from the datasets server).

## The recipe in one paragraph

LoRA supervised fine-tuning with TRL `SFTTrainer` of **Qwen/Qwen2.5-Coder-1.5B-Instruct** (fallback **Qwen2.5-Coder-0.5B-Instruct**) on about 4,000 rows streamed and filtered from **nvidia/OpenCodeInstruct** (CC-BY-4.0). Rows are kept when all 10 generated unit tests pass and the LLM judge gave 5 of 5. Evaluate base and tuned model with EvalPlus (HumanEval, HumanEval+, MBPP, MBPP+, greedy), a 300-row held-out slice of the same dataset run in a Docker sandbox, a paired McNemar test, and 12 sanity prompts. Merge with PEFT `merge_and_unload`, publish with a model card.

## Versions (PyPI JSON, 2026-11-25)

| Package | Version | requires_python |
|---|---|---|
| trl | 1.18.2 (2026-11-19) | >=3.11 |
| peft | 0.22.0 (2026-11-19) | >=3.11.0 |
| transformers | 5.24.1 (2026-11-24) | >=3.11.0 |
| datasets | 5.2.0 | >=3.10 |
| accelerate | 1.16.0 | >=3.11 |
| torch | 2.15.0 | >=3.11 |
| evalplus | 0.3.1 (2024-10-20, still latest) | >=3.9 |
| vllm | 0.34.0 (TRL's vllm extra pins <0.34.0) | >=3.11,<3.15 |
| verl (stretch alternative) | 0.9.1 | >=3.10,<3.13 |

Minimum Python is 3.11; 3.12 satisfies every package including verl. The local macOS Python 3.9.6 (and datasets 4.5.0, which TRL 1.18.2 rejects) means a fresh virtual environment. Use a second environment for EvalPlus, which dates from October 2024.

## Base model

| | Primary | Fallback |
|---|---|---|
| id | Qwen/Qwen2.5-Coder-1.5B-Instruct | Qwen/Qwen2.5-Coder-0.5B-Instruct |
| parameters | 1,543,714,304 (HF API, BF16) | 494,032,768 |
| layers, hidden | 28, 1536 | 24, 896 |
| context | 32,768 | 32,768 |
| license | Apache-2.0 | Apache-2.0 |
| reported HumanEval, HE+, MBPP, MBPP+ | 70.7, 66.5, 69.2, 59.4 | 61.6, 57.3, 52.4, 43.7 |

Template: ChatML with a default system prompt ("You are Qwen, created by Alibaba Cloud..."), eos `<|im_end|>`, pad `<|endoftext|>`. The FIM format belongs to the base models: the tokenizer defines `<|fim_prefix|>` (151659), `<|fim_middle|>` (151660), `<|fim_suffix|>` (151661), `<|fim_pad|>`, `<|repo_name|>`, `<|file_sep|>`, and the QwenLM README (written for Qwen3-Coder, same token names) gives prefix, suffix, middle order. The recipe does not use FIM.

Not chosen: Qwen2.5-Coder-3B-Instruct (HF license field is "other"), SmolLM3-3B (Apache-2.0, general purpose, twice the size; its chat template has `{% generation %}` markers, so it makes a good second recipe), SmolLM2 (general purpose, code numbers not checked). Variant B, start from the base model Qwen2.5-Coder-1.5B with `--eos-token '<|im_end|>'` (a TRL docs requirement for Qwen base models), is the closest small-scale copy of the OpenCodeInstruct paper and is where larger gains are plausible.

## Dataset

`nvidia/OpenCodeInstruct`, revision `8f3ba5ba...` (2025-04-28), CC-BY-4.0, 5,000,000 rows, 50 parquet shards (6.86 GB download). Fields: `id, input, output, domain, generation_algorithm, llm_judgement, unit_tests, tests_execution_status, average_test_score` (all strings; `unit_tests` is a JSON list of 10 asserts).

Why this one: rows carry unit tests and execution results, so one dataset serves filtering, training, held-out evaluation and the RL stretch. In the paper (arXiv 2504.04030, Table 4, 7B model, 500k rows) selecting judge score 5 beat random selection (HumanEval+ 80.5 vs 77.8, MBPP+ 71.4 vs 70.1); test-passing rows were only marginally better than random. QLoRA reports data quality beating size (9k OASST1 over 450k FLAN v2).

Rejected: KodCode-V1 and KodCode-Light-RL-10K (CC-BY-NC-4.0 per HF API, not clean), Magicoder-OSS-Instruct-75K (MIT but GPT-3.5 generated, no tests), self-oss-instruct-sc2-exec-filter-50k (ODC-By, no separate test field).

Generator terms (paper, sec. 2): answers, 10 tests per question and judgments by Qwen2.5-Coder-32B-Instruct; seed instructions by Qwen2.5-32B-Instruct from GitHub Python functions plus 25,443 TACO questions. Both Qwen models are Apache-2.0 per the HF API. Open: the model behind the Genetic-Instruct mutation and crossover step is not named in the sections read; seed licenses were not checked.

Selection (`prepare_data.py`): stream, `shuffle(seed=42, buffer_size=20000)` (the datasets docs say the buffer draws from up to 10 shards and the shard order is shuffled), keep rows where `average_test_score == 1`, all statuses pass, at least 5 tests, judge 5/5 on all criteria, a python block without network, file, clock or random calls, at most 6,000 characters. Then drop exact duplicate questions and any row sharing a 10-word gram with HumanEval or MBPP text. Split by `md5(id) mod 10000`: 300 held-out, 200 validation, 4,000 train. Drop held-out and validation rows whose 5-word shingles have Jaccard above 0.5 to a training question.

Findings that shaped the script, from reading real rows through the datasets server:
- The dataset is stored in blocks: rows at offsets 0, 300,000 and 1,000,000 are all `generic`, at 100,000 and 500,000 all `algorithmic`, all `self-instruct`. Taking the first N rows would give one domain. Always shuffle.
- The filter kept 66 of 500 rows (13 percent) on a non-random sample (11 percent on an earlier 600). **Estimate:** reaching 4,500 kept rows takes roughly 35,000 to 45,000 streamed rows and up to about 1.2 GB of transfer.
- Median kept row is 1,311 characters, so about 400 to 450 tokens (assumed 3.5 characters per token), about 1.8M tokens per epoch.

## Method and hyperparameters

TRL 1.18.2 API as verified in source: `SFTConfig(max_length=..., packing=..., completion_only_loss=..., assistant_only_loss=..., model_init_kwargs={"dtype": ...}, eos_token=...)`, `SFTTrainer(model=<str>, args=, train_dataset=, eval_dataset=, peft_config=LoraConfig(...))`. Dataset format: conversational prompt-completion (`prompt: [user]`, `completion: [assistant]`), loss on the completion only by default. `assistant_only_loss` needs `{% generation %}` markers, which the Qwen2.5-Coder template lacks (its only "generation" is `add_generation_prompt`), so it is not used. CLI: `trl sft --use_peft --lora_r 32 ...` (flags from `trl/scripts/sft.py` and `ModelConfig`); the CLI defaults `--dtype` to float32, so pass `bfloat16`.

Two API facts that differ from older tutorials: in transformers 5.24.1 `warmup_ratio` is gone and `warmup_steps` takes a float below 1 as a ratio; `gradient_checkpointing` is a deprecated alias of `activation_checkpointing`, and TRL turns it on by default (its help text says about 20 percent slower), so the script leaves it alone.

| Setting | Value | Reason and source |
|---|---|---|
| LoRA r | 32 | QLoRA: r unrelated to quality when all layers adapted. Biderman et al.: code gains from rank, recommend 256, ranks 16 to 64 may not suffice. 32 is a cheap middle (36.9M trainable, 2.4 percent). |
| alpha | 64 (= 2r) | Biderman et al. sec. 4.7: alpha = 2r matters. PEFT default is 8. |
| dropout | 0.05 | QLoRA appendix: helps 7B and 13B; TRL default 0.05 |
| target modules | all-linear | QLoRA: needed to match full fine-tuning; PEFT default for qwen2 is only q_proj, v_proj |
| learning rate | 1e-4 (sweep 5e-5, 1e-4, 2e-4) | TRL docs: about 1e-4 for adapters; TRL LoRA example 2e-4; Biderman: 5e-5 to 5e-4, one order above full fine-tuning |
| epochs | 2 (1 to 3) | about 125 steps per epoch; more epochs learn and forget more; 1 on a laptop |
| batch | 4 x 8 = 32 effective | about 125 steps per epoch; micro-batch limited by the 151,936-token logits |
| max_length | 2048 | SFTConfig default 1024 truncates; rows are at most 6,000 characters; OpenCodeInstruct used 2048 |
| scheduler, warmup | cosine, 5 percent | Biderman (10 percent) and OpenCodeInstruct (100 steps) both used cosine |
| weight decay, clip | 0.0, 1.0 | Biderman appendix |
| packing | off | bfd packing forces padding-free mode, which needs FlashAttention 2 or 3 |
| precision | bf16 on CUDA, float32 on CPU and Apple silicon | PEFT keeps adapter weights fp32 by default (`autocast_adapter_dtype=True`) |
| seed | 42 | transformers default; GPU kernels are still not bitwise deterministic |

## Hardware tiers (all estimates)

Parameter count x bytes from the HF API and configs; time from FLOPs = 6 x N x D (forward 2ND, activation gradients 2ND, recompute 2ND under checkpointing, no weight-gradient pass for frozen weights) with D about 3.6M tokens (4,000 rows x 2 epochs x about 450 tokens, itself an estimate), divided by an **assumed** sustained throughput. No measured throughput for this setup was found, so every time is a rough guess.

| Tier | Setup | Memory (estimate) | Time (rough guess) |
|---|---|---|---|
| Laptop, CPU or Apple silicon | 0.5B, float32, r=16, 2 x 16, max_length 1024, 1,000 rows, 1 epoch | weights 494M x 4 B = 1.98 GB, LoRA 8.8M x 16 B = 0.14 GB, logits 1,024 x 151,936 x 4 B = 0.62 GB x about 2.5, plus overhead: about 5 to 6 GB | 1 to 4 hours at an assumed 0.1 to 0.5 TFLOP/s (1.3e15 FLOPs) |
| 16 to 24 GB GPU | 1.5B, bf16, r=32, 4 x 8 | 3.09 + 0.59 + 0.35 + 0.5 + logits 6.2 (2.49 fp32 + 1.24 bf16 + 2.49 grad) = 10.7 GB plus 1 to 2 GB overhead: about 12 to 13 GB | 20 to 60 minutes at an assumed 10 to 30 TFLOP/s (3.3e16 FLOPs) |
| 80 GB GPU | 1.5B at micro-batch 8: about 20 to 25 GB. Or 7B (7,615,616,512 params, LoRA r=32 80.7M): about 33 to 40 GB | see JSON for the arithmetic | 5 to 20 minutes (1.5B), 0.5 to 1.5 hours (7B) at an assumed 30 to 100 TFLOP/s |

Two cross-checks from sources, not numbers to reuse: TRL says gradient checkpointing costs about 20 percent more time; Biderman et al. Appendix I measured LoRA about 15 percent slower than full fine-tuning on H100s. The biggest memory term is the logits, not the weights.

## Evaluation

Baseline (read 2026-11-25): the Qwen2.5-Coder technical report, arXiv 2409.12186 v3, EvalPlus table for instruct models: 1.5B Instruct HumanEval 70.7, HumanEval+ 66.5, MBPP 69.2, MBPP+ 59.4; 0.5B Instruct 61.6, 57.3, 52.4, 43.7. The OpenCodeInstruct paper repeats the same numbers (a copy, not a second measurement). The HF model card has no numbers, and the EvalPlus leaderboard data (125 entries, fetched today) has no Qwen2.5-Coder 1.5B or 0.5B entry, only the 32B (92.1, 87.2, 90.5, 77.0). Qwen's decoding settings are not stated, so reproduce the baseline yourself.

Commands (from the EvalPlus README, read today):

```bash
evalplus.evaluate --model "Qwen/Qwen2.5-Coder-1.5B-Instruct" --dataset humaneval --backend vllm --greedy   # or --backend hf
evalplus.evaluate --model "./out/merged" --dataset mbpp --backend vllm --greedy
# safer: generate locally, execute in Docker
evalplus.codegen --model "./out/merged" --dataset humaneval --backend vllm --greedy
docker run --rm -v "$(pwd)/evalplus_results:/app" ganler/evalplus:v0.3.1 \
  evalplus.evaluate --dataset humaneval --samples /app/humaneval/out--merged_vllm_temp_0.0.jsonl
```

The README uses `:latest`; the `v0.3.1` tag exists on Docker Hub (checked), so it is pinned. The sample file name follows `evalplus/codegen.py` (`model.strip("./").replace("/", "--")` plus `_{backend}_temp_0.0`). EvalPlus picks chat or direct-completion prompts from `tokenizer.chat_template`; for base models that carry a template add `--force-base-prompt`.

Things found in the EvalPlus source that affect fairness: the HF backend passes only `do_sample` and `max_new_tokens=768`, so the model's `generation_config.json` (Qwen sets `repetition_penalty` 1.1) is silently part of the evaluation. Keep that file identical in the merged folder. The HF backend uses CUDA if present, else CPU (no MPS path). Use the same backend before and after.

Held-out slice: `eval_heldout.py` generates greedily, extracts the first python block and runs the 10 asserts per question in `python:3.12-slim` with the hardened flags from `data/snippets.json` (no network, read-only, 256 MB, 64 pids, uid 65534). It first runs the reference solutions through your sandbox and drops rows that fail. `compare` runs an exact McNemar test on the paired per-question results.

Regression checks: the base-test lines (HumanEval, MBPP) that EvalPlus prints next to the plus lines; 12 sanity prompts with regex checks that also count answers that never stop.

Noise: standard error sqrt(p(1-p)/n) is 3.7 points for HumanEval+ (n=164), 2.5 for MBPP+ (n=378), 2.9 for the 300-row slice. One HumanEval problem is 0.61 points.

Outcome thresholds (our choices, derived from that noise, not from a source):
- Success: held-out strict pass@1 up at least 3 points with McNemar p below 0.05, and HumanEval+ and MBPP+ each no more than 2 points below baseline, base-test lines no more than 3 below, sanity at least baseline minus 1, no new unfinished outputs.
- No change: all deltas within about one standard error and p of 0.05 or more. Likely, and a valid result.
- Failure: HumanEval+ or MBPP+ down more than 3 points, sanity down 3 or more, new unfinished generations, or eval loss rising while train loss falls.

## Merge and publish

`AutoPeftModelForCausalLM.from_pretrained(adapter, dtype=torch.bfloat16).merge_and_unload(safe_merge=True)`; PEFT's docstring says it is not in place (use the returned model) and `safe_merge` checks for NaN. Then `save_pretrained`, tokenizer, `push_to_hub`. Evaluate the merged folder, since bf16 merging rounds. The adapter is small (36,929,536 fp32 parameters, about 148 MB), so publish it too. Model card fields and a template are in the JSON (`merge_and_publish`, `files["model_card.md"]`); the dataset's CC-BY-4.0 requires attribution to NVIDIA.

## Expected outcomes (estimates)

1. Most likely no detectable change on HumanEval+ and MBPP+ (within about 3 points). The OpenCodeInstruct authors got HumanEval+ 73.8 and MBPP+ 68.3 for Qwen2.5-Coder-1.5B against 66.5 and 59.4 for the Instruct model, but with full fine-tuning from the base model, 3 epochs over 5M rows (about 15M sample-visits). This recipe is 8,000 sample-visits, about 0.05 percent of that, with LoRA, which learns less than full fine-tuning on code (Biderman et al.).
2. A small gain on the held-out slice is plausible (roughly 0 to 5 points), the optimistic measure because instructions are evolved from shared seeds.
3. Small regression risk on base-test and sanity lines (LoRA forgets less than full fine-tuning, but narrow data still shifts habits).
4. Bigger gains need more data, higher rank (Biderman recommends 256 on all modules for code) or the base-model start, not more epochs.

## Stretch recipe: GRPO with an execution reward (experimental)

`reward_fn.py` (stdlib only): extracts the first python block (strings or message lists), runs code plus each assert in a fresh subprocess with a wall-clock timeout, process-group kill and Linux rlimits, returns 1.0 for all-pass else 0.0 (optional partial credit). Self-test passed locally. It is not a security sandbox: run the training job in a container without network (Docker flags in `data/snippets.json`).

Config names verified in `trl/trainer/grpo_config.py` v1.18.2: `num_generations` (default 8; effective batch must divide by it), `max_completion_length` (512), `temperature` (1.0), `learning_rate` (1e-6, a full fine-tuning scale; the script uses 1e-5 for LoRA as an untested guess), `beta` (0.0, which skips loading the reference model), `loss_type` ("dapo"), `scale_rewards` ("group"), `mask_truncated_completions`, `use_vllm` and `vllm_mode` ("colocate"), `log_completions`, `remove_unused_columns` (False, so dataset columns reach the reward). Reward signature from the TRL docs: keyword arguments `prompts, completions, completion_ids, trainer_state, ...` plus every dataset column except `prompt`; return one float per completion; completions are message lists for conversational data.

Task set: `prepare_data.py --rl-pool 3000` writes prompts with 6 `reward_tests` and 4 hidden `holdout_tests`; keep prompts whose pass rate over 8 samples is strictly between 0 and 1. A reward that rises while hidden tests do not is reward hacking. verl 0.9.1 alternative: a reward file with `my_reward_fn(data_source, solution_str, ground_truth, extra_info=None)` selected by `reward.custom_reward_function.path` and `.name`. Expected outcome (estimate): reward rises, hidden-test and EvalPlus gains uncertain and probably a point or two.

## Checked locally (no installs)

`python3 -m py_compile` on `train_sft.py`, `prepare_data.py`, `merge_push.py`, `eval_heldout.py`, `reward_fn.py`, `grpo_train.py` (Python 3.9.6); `bash -n` on `eval.sh` and `trl_sft_cli.sh`. `reward_fn.py` self-test passed; the sandbox runner in non-Docker mode gave correct per-test results on hand-written programs including `sys.exit(0)`, a syntax error and an infinite loop; `keep()` ran on 500 real rows.

## Not verified

- Nothing was trained or evaluated. All memory, time and outcome figures are estimates; the throughput assumptions (TFLOP/s, tokens per second) have no source.
- TRL 1.18.2, PEFT 0.22.0 and transformers 5.24.1 were not installed together (TRL's source has branches for transformers 5.18 and 5.23, the only evidence).
- Whether evalplus 0.3.1 runs under transformers 5.x, and whether its vLLM backend reads `generation_config.json`.
- Decoding settings and EvalPlus versions behind Qwen's published numbers.
- The model behind OpenCodeInstruct's mutation and crossover step, its decontamination benchmark list, and the licenses of the seed functions and problems.
- MPS support for the laptop path; the exact `datasets` 5.2.0 streaming behavior in `prepare_data.py` (written from docs, not run).
- The GRPO learning rate for LoRA.

## Sources

PyPI JSON (trl, peft, transformers, datasets, accelerate, torch, evalplus, vllm, verl). TRL v1.18.2: `trl/trainer/sft_config.py`, `base_config.py`, `model_config.py`, `grpo_config.py`, `trl/scripts/sft.py`, `docs/source/sft_trainer.md`, `grpo_trainer.md`, `clis.md`. PEFT v0.22.0: `tuners/lora/config.py`, `mapping_func.py`, `tuners/tuners_utils.py`. transformers v5.24.1 `training_args.py`. datasets `docs/source/stream.mdx`. EvalPlus README and v0.3.1 `codegen.py`, `provider/hf.py`, `provider/utility.py`, `provider/base.py`; leaderboard `results.json`. Papers: arXiv 2409.12186 (Qwen2.5-Coder), 2504.04030 (OpenCodeInstruct), 2407.21077 (Genetic-Instruct), 2405.09673 (LoRA Learns Less and Forgets Less), 2305.14314 (QLoRA). Hugging Face API for models and the dataset; Docker Hub tags for ganler/evalplus; verl `docs/preparation/reward_function.rst`.
