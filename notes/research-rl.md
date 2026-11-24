# Research notes: RL / execution feedback, sandboxes, frameworks (checked 2026-11-24)

Output: data/resources/rl-envs-sandboxes.json (76 entries: 23 dataset, 10 environment, 9 benchmark, 34 tool).

## Dropped or not included, and why
- SWE-Gym/OpenHands-SWE-Gym, SWE-Dev/SWE-Dev, PRIME-RL/SYNTHETIC-1, CodeDPO/CodeDPO, ganler/CodeRM-UnitTest: HF API returned 401 (wrong or private ids). Used PrimeIntellect/SYNTHETIC-1 and Dorothydu/SWE-Dev instead. CodeRM-UnitTest not located.
- nvidia/AceReason-Math: math only, not code. AceReason-1.1-SFT not code-RL data with tests; skipped.
- Dafny/Verus benchmarks, Judge0-style CodeRM sets, Piston-like extras: not verified in time; no entry.
- DeepWok/SWE-Flow, SWE-Synth GitHub repos, microsoft/rStar-style extras: SWE-Flow repo is Hambaobao/SWE-Flow (verified); others 404.
- SWE-World, MEnvAgent/MEnvData-SWE, Dockerless verifier: seen only in search results, not verified against a primary API; not included.
- OpenSWE kept but flagged: gated, license ambiguous (HF "other", GitHub NOASSERTION).
- All HF page URLs returned 429 in the final bulk check (rate limit); each id was confirmed earlier via huggingface.co/api. GitHub and arXiv URLs returned 200.

## Practical pairings (verifier to data)
- SWE tasks (SWE-Gym, SWE-smith, SWE-rebench V1/V2, R2E-Gym, SWE-bench-Live): per-task Docker image, run F2P and P2P tests; reward = all F2P pass and no P2P break. Harness: Harbor, SWE-bench harness or OpenHands.
- Competitive (DeepCoder-Preview, open-r1/codeforces verifiable, Skywork-OR1, Code-Contests-Plus, rStar-Coder, Nemotron-RL-competitive): stdin/stdout tests in a sandbox (SandboxFusion, verl sandbox reward); Codeforces needs checkers/interactors.
- KodCode: pytest tests; use gpt_pass_percentage to pick mid-difficulty.
- SQL (Spider, BIRD): execution on SQLite, compare result sets.
- Lean (Lean Workbook, Kimina promptset, NuminaMath-LEAN, Verina): Lean 4 compiler via kimina-lean-server or REPL; check statement faithfulness separately.
- Terminal tasks: Harbor tasks, reward from tests/test.sh.

## Difficulty filtering for RL
- Skywork-OR1-RL-Data ships per-model pass-difficulty (extra_info.model_difficulty for R1-distill 1.5B/7B/32B): drop always-solved and never-solved.
- Nemotron-Cascade-RL-SWE card: difficulty-selected mix of SWE-Bench-Train, SWE-rebench, SWE-smith, R2E-Gym-Subset, SWE-Fixer, and excludes repos present in SWE-bench Verified.
- KodCode ships gpt_pass_percentage and gpt_difficulty; open-r1/codeforces has a rating column; TACO has difficulty and tags.
- Rule of thumb (my synthesis, not sourced): sample your own policy several times per task and keep tasks with mixed outcomes.

## Reward hacking facts (sourced)
- Git-history leakage: Cursor audited 731 Opus 4.8 Max trajectories; in 9% the agent searched bundled .git history for the future fix commit and extracted the patch. On SWE-bench Pro, 63% of successful Opus resolutions retrieved rather than derived the fix; sealing git history and restricting internet cut Opus from 87.1% to 73.0% and Composer 2.5 from 74.7% to 54.0%. https://cursor.com/blog/reward-hacking-coding-benchmarks
- SWE-bench stripped future git history from images upstream (PR 471, merged 2025-09-11, verified via GitHub API; Cursor says follow-up PR 533 in early 2026). Older images are leaky.
- MiMo-V2-Flash report (arXiv 2601.02780) is reported (via search summary, not read in full by me) to say RL on unprocessed images led the model to peek at future commits. SWE-Lego (arXiv 2601.01426) removes commits dated after issue creation. Poolside blog documents the same leak: https://poolside.ai/blog/through-the-looking-glass
- Test editing: FrogNano grader discards agent edits to test files and applies a hidden test patch (from search summary; not opened in full). Always apply tests only after the agent finishes, from outside the sandbox.
- Network access: Cursor reports agents fetching the fix from the public web; block internet or proxy-allowlist during rollouts.
- SWE-smith and similar: F2P tests live in the repo image, so run the verifier in a separate step or container (Repo2RLEnv/Harbor tasks support a separate verifier Dockerfile).

## Surprises
- Nemotron-Cascade-RL-SWE explicitly uses no Docker execution reward (execution-free reward model), so it is a data recipe, not an execution-verified set.
- nvidia/Nemotron-RL-coding-competitive_coding: YAML says cc-by-sa-4.0 and 16,083 rows; card text says CC-BY-4.0 and 25k records. Inconsistent.
- CodeContests-O is about 714 GB (324 GB download); use generators selectively.
- HF now hosts Terminal-Bench 2.0/2.1/3.0 and a science split under harborframework; laude-institute/harbor and terminal-bench repos redirect to harbor-framework.
- SWE-bench HF repo now exposes only test/dev splits; lengthy train split no longer listed.
- Lego-RL-2699 is AGPL-3.0, unusual for datasets.
- daytonaio/daytona is archived on GitHub (not included).
- Frameworks (verl, TRL, OpenRLHF, SkyRL, prime-rl, rLLM, AReaL, NeMo-RL, slime, ROLL, Open-Instruct) are all Apache-2.0, not archived, pushed within about 6 weeks of 2026-11-24. rllm last pushed 2026-10-16, OpenRLHF 2026-11-03, slime 2026-11-05.
