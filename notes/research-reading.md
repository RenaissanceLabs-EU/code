# Research notes: reading list (checked 2026-11-25)

Output: data/reading.json, 70 entries, in reading order. Two fields beyond the requested schema: `section` (1 to 7, the seven reading-order groups in the task; the `stages` tags are separate) and entry order itself. Section sizes: 1 foundations 7, 2 pretraining data 8, 3 open model families 10, 4 SFT and instruction data 11, 5 preference and RL 12, 6 evaluation and its failures 12, 7 systems and tooling 10.

Stage tag counts (an entry can carry several): pretrain 29, rl 29, sft 22, eval 21, tooling 8, preference 5.
Types: paper 50, blog 11, technical-report 4, code-walkthrough 2, course 1, talk 1, book 1. About 77% papers and reports, 23% other, so the "rest" share is lower than the 40% asked for; I did not pad it with pages I had not read.

## What was verified and how
- 54 arXiv entries: title, authors, first-version date and full abstract fetched from the export.arxiv.org API. A script checked that every `key_result` for these entries is a verbatim substring of the abstract (after removing LaTeX markup), that the year equals the first-version year, and that the first author matches.
- Web items (Qwen3-Coder blog, Open-R1 update 3, DeepCoder model card, DeepSWE blog, OpenAI SWE-bench Verified and its retirement note, Aider polyglot, Weng, TRL docs, verl docs, GKE blog, CS336, Smol Training Playbook, Karpathy video, Raschka, RLHF book): each page was fetched and read on 2026-11-25; dates, counts and names in `teaches` come from those pages. For these entries `key_result` is the page's own description or a close paraphrase of a stated result, not an abstract quote.
- All 87 URLs (primary and extra links) returned HTTP 200 with curl following redirects.
- `teaches` for arXiv entries is built from the abstract only. I did not read full texts, so those sentences describe what the abstract says the paper contains (ablations, datasets, negative results), not details found only in the body. Each entry's `evidence` field says "Abstract only; full text not read."
- Catalog ids in `catalog_ids` were checked against docs/data/resources.json (all exist). Most paper-kind catalog ids (`paper-*`) are reused on purpose, since the reading list is about those papers; no entry is new to the catalog.

## Searched for
Codex, AlphaCode, InCoder, FIM, CodeGen, Code Llama, phi-1; The Stack, SantaCoder, StarCoder 1 and 2, Arctic-SnowCoder, SmolLM2, Chinchilla, Kaplan, data-constrained scaling, code in pretraining, code scaling laws; DeepSeek-Coder (1, V2), Qwen2.5-Coder, Qwen3-Coder (blog), Qwen3-Coder-Next (report), OpenCoder, Seed-Coder, Granite, CodeGemma, Devstral and Codestral posts, Kimi-Dev, CWM, Kimi K2, GLM-4.5, Llama 3, Qwen3; Self-Instruct, Code Alpaca, WizardCoder, WaveCoder, Magicoder, OctoPack, SelfCodeAlign, LIMA, OpenCodeInstruct, OpenCodeReasoning, OpenThoughts, Open-R1, SWE-smith, SWE-Gym, SWE-agent; CodeRL, PPOCoder, RLTF, StepCoder, PRM for code, PLUM, CodeDPO, DPO, DeepSeekMath, DeepSeek-R1, DAPO, Dr. GRPO, GSPO, ProRL, AceReason, AceCoder, CodeRM, DeepCoder, SWE-RL, DeepSWE, R2E-Gym, Kimi k1.5, Tulu 3, OpenAI o-series programming paper, reward-hacking papers; MBPP, EvalPlus, LiveCodeBench, CRUXEval, SWE-bench, SWE-bench Verified and its retirement note, SWE-bench Pro, BigCodeBench, rephrased-sample contamination, SWE-Bench Illusion, "Are Solved Issues Really Solved", Aider polyglot, Terminal-Bench; TRL, verl, HybridFlow, OpenRLHF, SkyRL, sandbox blogs, CS336, Karpathy lectures, Smol Training Playbook, Ultra-Scale Playbook, evaluation guidebook, RLHF book, Raschka, Weng.

## Verified but not on the list (cap of 12 per section or total of 70)
These all opened and the arXiv ones were confirmed, so they can be added by the main session if wanted:
- 2503.20783 Dr. GRPO, 2505.24864 ProRL, 2507.18071 GSPO, 2505.16400 AceReason-Nemotron, 2505.22312 Skywork-OR1, 2502.01718 AceCoder, 2501.01054 CodeRM, 2402.01391 StepCoder, 2410.17621 process-supervision PPO for code, 2410.05605 CodeDPO, 2305.18290 DPO, 2501.12599 Kimi k1.5, 2507.20534 Kimi K2, 2502.06807 OpenAI competitive programming, 2508.03501 long-context multi-turn SWE RL, 2511.16108 SkyRL-Agent.
- 2511.21654 EvilGenie and 2611.10404 Coding or Cheating (reward hacking); 2506.12286 SWE-Bench Illusion; 2503.15223 Are Solved Issues Really Solved; 2509.16941 SWE-Bench Pro; 2401.03065 CRUXEval.
- 2107.06499 Deduplicating Training Data; 2305.16264 Scaling Data-Constrained LMs; 2001.08361 Kaplan scaling laws; 2404.07965 Rho-1; 2402.12813 Scaling Laws Behind Code Understanding Model.
- 2506.04178 OpenThoughts; 2312.14187 WaveCoder; 2305.11206 LIMA; 2406.11409 CodeGemma; 2510.02387 CWM; 2505.09388 Qwen3 report; 2508.06471 GLM-4.5; 2407.21783 Llama 3; 2405.11143 OpenRLHF; 2508.14444 Nemotron Nano 2; 2504.03624 Nemotron-H; 2511.18538 code intelligence survey.
- Pages: mistral.ai/news/devstral (May 21, 2025; 46.8% on SWE-Bench Verified, Apache 2.0, but no training detail beyond "trained on real GitHub issues"), mistral.ai/news/codestral, HF blog open-r1 and update-2, Ultra-Scale Playbook, LLM Evaluation Guidebook, SkyRL project page, Karpathy Zero to Hero and build-nanoGPT, HF TRL vLLM co-location blog.

## Rejected and why
- Code Alpaca (github.com/sahil280114/codealpaca): page opens but I read only the title; no verified content, so dropped.
- Devstral and Codestral posts: opened, but marketing-level; they state a score and a license and nothing about how the model was trained. Devstral is noted above in case a model-family pointer is wanted.
- Nemotron code pretraining: no dedicated arXiv report on the code data exists in what I found. The data lives in the dataset cards (Nemotron-Pretraining-Code-v1/v2 are in the catalog as datasets). I read the v2 card (adds metadata for 377M more filtered and deduplicated GitHub files, about 340B tokens; five synthetic techniques: question answering, code review, student teacher, rewriting, transpilation; creation date 12/15/2025; governed by the NVIDIA Data Access Agreement for Model Training, gated). A dataset card is not a reading item, so it is left to the catalog.
- Modal "best sandboxes for code RL" guide: vendor marketing; not read in full.
- Anthropic reward-hacking URL guessed from memory returned 404; dropped. Nothing from Anthropic is on the list.
- A code-specific scaling-law paper from 2024 ("Scaling Laws Behind Code Understanding Model") is about code understanding (BERT-style encoder, 1.5B CoLSBERT), not code generation, so I used the 2025 multilingual paper instead.
- No code-specific DPO paper is in the list for the preference stage beyond PLUM; CodeDPO (2410.05605) was verified and cut for the cap. General DPO is also cut.

## Notes for the main session
- `year` is null for the TRL and verl docs (living documentation pages show no date). Render as "docs, read 2026-11".
- DeepCoder: the model card is the primary link; its Notion blog post is in `extra_links` (returns 200 but the page is script-rendered, so I could not read it). Year 2025 comes from the card citation and the catalog, not from a dated page.
- R2E-Gym: the abstract names the environment "AgentGym". The title, the entry and the catalog use R2E-Gym. The `key_result` quotes the abstract as written.
- SWE-RL `key_result` quotes the abstract including its "--" aside.
- Titles keep arXiv punctuation, including the ASCII "--" in DeepSeek-Coder and SmolLM2 (not dashes used as punctuation by us).
- GKE blog is vendor-authored and benchmarks against its own baseline; the entry says so.
- Karpathy video is not code-specific; the entry says so. CS336 uses math, not code, as its RL domain; the entry says so.
- OpenAI Verified post: first published August 13, 2024, updated February 24, 2025; `year` is 2024. The retirement post is February 23, 2026.

## Not verified
- Full texts of all arXiv papers (only abstracts read), so numbers in `teaches` that are not in an abstract are not present; every number used is in an abstract or on a page I read.
- Venues. I set `venue` to "arXiv" for all arXiv entries. Conference acceptances (for example NeurIPS, ACL 2026 Findings for the multilingual code scaling-law paper, NeurIPS 2025 D&B for SWE-smith) were seen only in search snippets or a repo title, not on the paper pages, so they are not stated.
- A search snippet said OpenAI later retracted its SWE-bench Pro recommendation (a second post, possibly July 2026). I could not open that post; the retirement page I read carries no update banner and still recommends SWE-bench Pro. The list does not claim anything about Pro's status.
- Qwen3-Coder-Next headline benchmark numbers (70.6% on SWE-Bench Verified appeared only in a news article); not used.
- CS336 lecture videos and later offerings; only the Spring 2025 archived page was read.
- Karpathy video content beyond the description and chapter list.
- Aider polyglot post author name (not on the fetched text); `authors` is the project name "aider".
- Whether any listed URL will stay reachable (checked once, 2026-11-25).
