# Research notes: models, recipes, papers (checked 2026-11-24)

Output: data/resources/models-recipes.json (87 entries: 33 models, 38 papers, 7 recipes, 9 tools). Every license, size and context figure was read from the HF API, config.json, model README, LICENSE file, GitHub API, or arXiv API on the check date. HF returned HTTP 429 (rate limit) for 12 page-URL HEAD checks; those models were all confirmed earlier through the HF API.

## Dropped or not included, and why
- AlphaCode 2: only a Google tech report PDF, no arXiv abstract page I could verify.
- Qwen3.8-27B-Base, Qwen3.8-Flash, Qwen3.7-27B, DeepSeek-V4.1-Pro, Kimi-K3.1 (non-Pro): HF API returned 401 (id not found), so not listed. Qwen3.8-27B is included as post-trained only.
- Nemotron-3 Super/Nano, GLM-5/5.1/5.2, Kimi K2.5/K2.6, MiniMax M2.5/M3, Qwen3.5/3.6: exist on HF with licenses seen, but left out to avoid listing every sibling; add if needed.
- OLMo-Coder: no such model found; Olmo 3 is general-purpose.
- Qwen3-Coder GitHub repo license is null in the API (the HF models are Apache-2.0); only the HF models are listed as models, repo appears as a link.
- Third-party fine-tunes with huge download counts on HF (e.g. "Tiel-Coder", "Qwen3.8-...-Heretic") were not listed: unknown provenance, benchmark claims unverified.
- UnitTenv, a "Less is more for code" paper, a Meta/Qwen3-Coder technical report: not found or not verified; skipped.
- Web-search ranking sites (Kimi K3 93.4%, "Ornith-1.5", DeepSeek V4 Pro 80.6%) were inconsistent low-quality aggregators; no scores from them were used.
- Qwen2.5-Coder sizes 0.5B to 3B and 14B: license not verified (rate limited), so the family entry claims Apache-2.0 only for 32B and 7B.

## What the evidence says (for improving a model at coding)
1. RL with verifiable reward (tests pass) works for code: DeepSeek-R1 (https://arxiv.org/abs/2501.12948), DeepCoder (https://huggingface.co/agentica-org/DeepCoder-14B-Preview: 53.0 to 60.6% LiveCodeBench v5, card numbers), Skywork-OR1 (https://arxiv.org/abs/2505.22312).
2. Start RL from a strong distilled or instruct base. DeepCoder, AceReason and Skywork all start from R1-Distill models (see model cards and https://arxiv.org/abs/2505.16400).
3. Stage math RL then code RL: math-only RL helped code in AceReason (https://arxiv.org/abs/2505.16400).
4. GRPO needs fixes: Dr. GRPO removes length bias (https://arxiv.org/abs/2503.20783); DAPO adds clip-high, dynamic sampling, overlong handling (https://arxiv.org/abs/2503.14476); GSPO helps MoE stability (https://arxiv.org/abs/2507.18071).
5. Filter overlong and truncated samples and filter problem difficulty offline: stated in the DeepCoder card (https://huggingface.co/agentica-org/DeepCoder-14B-Preview).
6. Distillation SFT can match or beat RL for small models on competitive coding: OpenCodeReasoning abstract reports 61.8% LiveCodeBench SFT-only (https://arxiv.org/abs/2504.01943), though AceReason argues large RL can surpass distillation (https://arxiv.org/abs/2505.16400).
7. Reward quality is the bottleneck. More generated unit tests give better reward signal (https://arxiv.org/abs/2501.01054); auto-synthesized tests help RL (https://arxiv.org/abs/2502.01718).
8. Tests are hackable. 22.4% of a 49-task SWE-bench Verified sample accepted a patch that differs from gold (https://arxiv.org/abs/2606.16062); models mine git history and the filesystem for answers (https://arxiv.org/abs/2611.10404); LLM judges detect obvious hacks better than held-out tests (https://arxiv.org/abs/2511.21654). Sandbox git objects, hide tests, and monitor rollouts.
9. For SWE agents, environments scale via synthesis: SWE-smith 50k instances from 128 repos (https://arxiv.org/abs/2504.21798), R2E-Gym 8.7K tasks (https://arxiv.org/abs/2504.07164), SWE-Gym 2,438 real tasks (https://arxiv.org/abs/2412.21139).
10. Filter RL tasks by repository to avoid benchmark leakage, as DeepSWE did (https://huggingface.co/agentica-org/DeepSWE-Preview).
11. Single-turn verifiable steps (localize, edit, reflect) are a good prior for agent SFT with only about 5k trajectories (https://arxiv.org/abs/2509.23045).
12. Cheap non-execution rewards (patch similarity) can work at scale for SWE (https://arxiv.org/abs/2502.18449), but are proxies.
13. SFT data: execution-validated self-generated data avoids teacher dependence (https://arxiv.org/abs/2410.24198); OSS-Instruct seeds diversity (https://arxiv.org/abs/2312.02120); commits are a natural instruction source (https://arxiv.org/abs/2308.07124).
14. Pretraining: quality filtering beats raw volume for small models (https://arxiv.org/abs/2306.11644, https://arxiv.org/abs/2502.02737); LLM-based filtering can replace hand rules (https://arxiv.org/abs/2506.03524); OpenCoder is the most transparent end-to-end recipe (https://arxiv.org/abs/2411.04905).
15. Contamination: rephrased samples evade n-gram decontamination (https://arxiv.org/abs/2311.04850); use time-windowed LiveCodeBench (https://arxiv.org/abs/2403.07974); Qwen2.5 bases may carry pretraining bias toward reasoning (https://arxiv.org/abs/2503.20783).

## Surprises
- The open-weight frontier moved to 1M-context MoEs from Chinese labs with custom licenses (Kimi K3.1 Pro 2.78T params, GLM-5.3 753B, DeepSeek V4 line 0.3 to 1.6T). Licenses are MIT-like with revenue-based conditions (Kimi: USD 20M MaaS threshold; GLM-5.3: USD 10B revenue security review). Read them before distilling.
- Qwen3-Coder-Next (80B, 3B active, hybrid linear attention) is the practical single-node coder, and a Base checkpoint exists.
- Qwen3.8-27B (dense, Apache-2.0) is a general vision-language model, not a "Coder" variant; Qwen no longer seems to need separate coder lines at 27B.
- Several repos moved orgs (verl to verl-project, torchtune to meta-pytorch, SkyRL, rLLM, SWE-smith to SWE-bench, openhands-lm to OpenHands); old links redirect.
- OpenCoder and Agentless repos are stale (last push Dec 2024) but remain the reference for their ideas.
- facebookresearch/swe-rl and MoonshotAI/Kimi-Dev have license NOASSERTION in the GitHub API: check before reuse.
- devstral Small (Apache-2.0) vs Codestral (MNPL, non-production) vs Devstral 2 123B (modified MIT) show Mistral licenses vary within one family.
