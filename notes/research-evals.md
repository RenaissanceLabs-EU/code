# Research notes: evaluation (checked 2026-11-24)

Output: data/resources/evals.json, 67 entries (55 benchmark, 12 tool). All entry URLs returned HTTP 200 on 2026-11-24.

## Dropped or not included, and why
- SWE-bench Verified is kept but flagged. Not dropped.
- CodeFuse CR-Bench and other code-review evals: GitHub repo name I tried returned 404 and I found no verified primary source. No code-review eval is in the file. Gap.
- DevBench: only the SDLC paper (arXiv 2403.08604, which calls itself DevEval) was verified; included as a paper-only entry with an explicit naming warning. HF ids called "devbench" were anonymous or unrelated, not used.
- ProjectEval: only the paper verified; included paper-only (no repo or HF found with my queries).
- HLE-code, SWE-Lancer data, PaperBench data: no verified code-specific HLE subset; SWE-Lancer and PaperBench are paper-only because their original repo is archived (SWE-Lancer) or unchecked.
- EditEval: no primary source found; CanItEdit covers editing.
- Terminal-Bench 1 has no separate entry (repo harbor-framework/terminal-bench-1 exists, 2,625 stars, Apache-2.0); mentioned inside TB 2/3 entries.
- Metric claims from search summaries that I could not confirm in a primary source were omitted or marked "per search summary" (Epoch review rating, LiveOIBench GPT-5 percentile, Harbor CLI shape).
- Load snippets only given for datasets whose id and split I saw in the HF API. LiveCodeBench has none: its HF dataset uses a loading script that the card says is unsupported by current datasets.
- Many unauthenticated HF and GitHub API calls hit 401/429 rate limits; I retried with the gh CLI and throttling. A 401 from the HF API for a dataset path means the id is wrong, not private.

## Practical insights
- Smoke test: HumanEval+, MBPP+ (seconds-minutes), CRUXEval, CanItEdit, CWEval. These are saturated or near it and public since 2021-2024; they catch breakage, not progress.
- Contamination-aware gate for algorithmic coding: LiveCodeBench filtered to dates after the training cutoff; LiveCodeBench Pro and CodeElo for harder, fresh problems.
- Agentic gate: pair at least one SWE-style set (Verified for continuity, plus SWE-bench-Live or SWE-rebench monthly splits, plus Multilingual) with Terminal-Bench 2.x (via Harbor). Add Aider Polyglot as a cheap multilingual edit check.
- Pair execution evals with one security eval (CWEval or SecCodePLT) and one test-generation eval (SWT-bench or TestGenEval) if the RL reward uses tests.
- SQL: BIRD Mini-Dev as cheap regression, Spider 2.0 as the hard gate; Spider is saturated.
- Lean: miniF2F is saturated; PutnamBench is the harder one.

## Known benchmark problems (with sources)
- SWE-bench Verified: OpenAI post dated 2026-02-23 (openai.com/index/why-we-no-longer-evaluate-swe-bench-verified): 59.4% of 138 audited hard problems had flawed tests or specs (35.5% too narrow, 18.8% too wide); all tested frontier models could reproduce gold patches or verbatim details for some tasks. OpenAI stopped reporting it.
- SWE-Bench Pro: OpenAI first recommended it, then on 2026-07-08 retracted that (openai.com/index/separating-signal-from-noise-coding-evaluations): about 30% of tasks broken (200 tasks, 27.4%, automated; 249, 34.1%, human). So neither "contamination-resistant" nor "private split" is a guarantee of validity. Only 731 of 1,865 problems are public.
- HumanEval/MBPP: EvalPlus showed weak tests (HumanEval+ has 80x tests, MBPP+ 35x and drops 21 broken tasks, 399 to 378). Public since 2021, so assume leakage.
- Terminal-Bench: version 2.1 exists because 26 tasks needed fixes for bugs, timeouts and reward-hacking vulnerabilities, so verifier quality is an active issue.
- BigCodeBench repo is archived (2026-11-24); SWE-Lancer and METR public-tasks repos are archived; LiveCodeBench repo last pushed 2025-07-16.
- Scores vary across scaffolds; the SWE-rebench leaderboard uses a standardized scaffold so it will not match vendor numbers.

## Surprises
- Terminal-Bench 3.0 (74 tasks) is already on HF (updated 2026-08-21); release notes not found.
- The Terminal-Bench 2.0 task count conflicts across sources (89 in paper vs 66 plus a CPU-only set in a Snorkel post); I used the paper.
- SWE-bench Multimodal counts changed between HF copies (princeton-nlp 510 test vs SWE-bench org 480).
- inspect_evals already ports SWE-Lancer, PaperBench, MLE-bench, LiveCodeBench Pro and CyberSecEval 2-4, making it the most convenient single agentic harness.
- Aider Polyglot top score listed was 88.0% (gpt-5 high, run 2025-08-23, leaderboard updated 2025-11-20), so it is near saturation.
