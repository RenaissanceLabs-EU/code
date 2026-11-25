# Starter datasets: research notes (2026-11-25)

Output: data/starter-datasets.json (51 entries). Validated with python3 json.load; every `id` except `code-search-net` exists in docs/data/resources.json; every `used_by` id exists in data/model-recipes.json.

## Counts

By spread group (the groups in the task): pretraining and mid-training 13 (12 catalog entries plus CodeSearchNet), SFT and instruction 14, preference or reward 4, interactive environments and task sets 8, evaluation 12.

By `purpose` field: evaluation 12, instruction-sft 11, raw-code-pretraining 9, issue-patch 6, docs-and-text 4, execution-tasks 3, preference 3, reasoning-traces 2, agent-trajectories 1.
By `kind`: dataset 33, benchmark 12, environment 6. The two DeepCoder and Codeforces task sets are `dataset` kind, not `environment`, because they ship tests but no containers.

Differences between group and `purpose`: AceCode-87K sits in the reward group but has purpose execution-tasks (rows carry tests and pass rates). Two SFT-group sets are reasoning traces, one is agent trajectories.

## Why these were picked

- Pretraining: the Stack v1 and v2, StarCoderData and Common Pile Stack v2 cover raw code at different licensing strictness. Stack-Edu and RefineCode metadata show quality filtering. Nemotron Pretraining Code v1 and Nemotron-CC-Code show synthetic and web-recovered code. StarCoder2 data extras (documentation, Stack Overflow, issues) and the OpenCoder FineWeb code corpus are the documentation and Q&A sources. CommitPack and GitHub Code are the older baselines. CodeSearchNet was added (not in the catalog) as the standard docstring and code pair set.
- SFT: a spread of how instruction data is made: seeded from real code (OSS-Instruct, SelfCodeAlign), evolved (Evol-CodeAlpaca, Magicoder Evol), execution-filtered with tests (KodCode, OpenCodeInstruct, OpenCodeReasoning), real commits (CommitPackFT), multi-turn feedback (Code-Feedback), a general mixture (Tulu 3), competitive reasoning traces (CodeForces-CoTs), and agent trajectories (SWE-smith).
- Preference and reward: CodeUltraFeedback (judge labels), AceCode-87K and AceCodePair-300K (test-derived), Ling-Coder-DPO (pass rate, perplexity, reward model).
- Environments: SWE-Gym, SWE-smith, R2E-Gym, SWE-rebench v1 and v2, Multi-SWE-RL for repository-level execution feedback; DeepCoder and open-r1 Codeforces for verifiable single-file tests.
- Evaluation: HumanEval and MBPP with their EvalPlus variants, BigCodeBench, LiveCodeBench, CRUXEval, MultiPL-E, SWE-bench Verified and Multilingual, Aider polyglot, Terminal-Bench 2.0.

## Dropped or not included

- The Stack v2 dedup, train-smol-ids and Stack v3 (variants or successors of entries already present). Nemotron Pretraining Code v2 and v3 (successors; v1 is listed).
- Evol-Instruct-Code-80k (CC-BY-NC-SA), Code-Alpaca 20K (small), Glaive code assistant v3 and Ling-Coder-SFT (not read in enough detail), xP3x (OctoPack's multilingual mix is not a coding set, so only CommitPackFT is listed).
- OpenCodeReasoning-2, Nemotron post-training sets, OpenThoughts3 (larger or later versions of the same idea; the catalog keeps them).
- SWE-bench Lite, SWE-bench Pro, Terminal-Bench 3.0, HumanEval-X, HumanEvalPack (catalog entries, left out to stay within the target size).
- Software Heritage is represented through Stack v2, Stack-Edu and RefineCode metadata; the catalog entry software-heritage-graph is a graph archive, not a training set.

## Judgment calls

- `maturity` follows release date and documented uses in data/model-recipes.json: established is 2023 or earlier or a long-stable reference; emerging is 2025 to 2026 with at least one recipe or clear adoption; experimental is new with no recipe use and low independent counts. I applied it by hand, and the evidence field of each entry gives the release date and use.
- `used_by` lists recipes whose entry text names the dataset. For benchmarks it lists recipes whose text reports a result on it (HumanEval, MBPP, LiveCodeBench, SWE-bench Verified); this is evaluation use, not training.
- Popularity numbers are the `downloads` (30 days) and `likes` fields from the HF API on 2026-11-25. For LiveCodeBench the HF numbers are for livecodebench/code_generation_lite. Aider polyglot is GitHub only (230 stars). GitHub stars are included where the entry links a repository I queried.

## Not verified

- Nemotron-Pretraining-Code-v1 column names (gated, viewer blocked; the card does not list columns).
- Field names for Multi-SWE-RL, The Stack v1, StarCoderData, CommitPack, GitHub Code, Terminal-Bench 2.0 and LiveCodeBench rows were read from cards or file lists, not from sample rows (viewer unavailable). Multi-SWE-RL record fields and instance counts were not read.
- OpenCodeReasoning language and teacher, KodCode, OpenCodeInstruct, AceCode and DeepCoder languages ("Python") follow the catalog entries, not a fresh card read.
- Per-subset teacher models of opc-sft-stage2, and whether its evol_instruct config overlaps Magicoder-Evol-Instruct-110K (the row counts match at 111,183; content not compared).
- OpenCoder recipe counts (110K Educational, 110K Package) differ from the released config sizes (118,278 and 170,943); I did not resolve this.
- Granite's "Self-OSS-Instruct-SC2" was matched to bigcode/self-oss-instruct-sc2-exec-filter-50k by name only.
- MultiPL-E language count: the catalog says 18 additional languages, the HF configs list 24 language codes. The entry follows the configs.
- GitHub Code language count: the card says 32 in one place and 30 in another.
- The OpenAI post on SWE-bench Verified was read on 2026-11-24 for the catalog, not re-fetched today. The aider leaderboard figure (gpt-5 high, 88.0%) is the catalog's 2026-11-24 reading. The aider blog post URL is named in the README and was not fetched.
- Several limitation sentences use the catalog's caveat text (itself checked on 2026-11-24 against cards and papers) rather than a fresh quote; entries say where a sentence is structural rather than a card statement (CodeForces-CoTs decontamination, DeepCoder, Ling-Coder-DPO, StarCoderData cutoff).
- Whether 30-day download counts include automated pulls (notably SWE-rebench V2 at 101,465) is unknown.
