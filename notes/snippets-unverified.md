# Snippets not fully confirmed (2026-11-24)

Snippet file: code/data/snippets.json (17 snippets). Everything below was either left out or is flagged in the snippet notes.

## Omitted
- `trl sft` CLI with a code dataset: the docs only show `--model_name_or_path` and `--dataset_name` with non-code datasets (imdb, etc.), and I did not confirm a code dataset with the needed prompt/completion columns. Python SFTTrainer snippet is included instead.
- Axolotl config: not covered (LLaMA-Factory chosen).
- `trl grpo` CLI: not needed, Python trainer shown.
- LLaMA-Factory `dataset_info.json` entry format for a custom code dataset: not fetched.

## Included but partly unconfirmed
- Inspect: the `--model vllm/...` provider line was not confirmed against Inspect docs. Task names and flags were confirmed.
- lm-evaluation-harness: `--apply_chat_template` mentioned in notes only, not confirmed in this pass.
- bigcode-evaluation-harness: README shows mbpp in examples; humaneval confirmed in the task registry source only. Version not confirmed (no tag checked).
- evalplus Docker samples path follows the README example naming.
- Terminal-Bench legacy `tb` model name (claude-3-7-latest) is stale; copied from README.

## Not executed (reason)
- TRL, datatrove, SWE-bench, LiveCodeBench, inspect_evals, Harbor, verl, LLaMA-Factory: need Python >=3.10/3.11 (local is 3.9.6), GPUs, API keys, or large Docker images. Flags were checked against README, docs, or source only.
- Ran locally: Docker hardened sandbox (Docker 29.1.3, python:3.12-slim), pass@k check, subprocess reward (pass, fail, timeout, syntax error), datasets streaming (datasets 4.5.0).
- Subprocess reward: Linux-only rlimits (RLIMIT_AS, NPROC) were not exercised on macOS.
