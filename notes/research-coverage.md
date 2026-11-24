# Language coverage pass (data/coverage.json), checked 2026-11-24

Goal: an explicit, source-checked language list for each catalog resource, using the 44 language ids of the rebuild brief.

## Method

- Fetched for every dataset, benchmark and environment (167 entries): the Hugging Face API record, the raw README, linked GitHub READMEs and arXiv abstracts (export.arxiv.org API). Same for models and recipes (39 entries).
- Where the card was gated or silent, read the paper full text (arxiv.org/html or ar5iv) for: Magicoder, StarCoder, StarCoder2, The Stack, OpenCoder, CodeScope, SAFIM, DevEval, ProjectEval, LiveOIBench, LiveCodeBench Pro, CWEval, CyberSecEval, SWE-Lancer, R2E-Gym.
- Large corpora: language names were parsed from the source list (HF config names, per-language tables, stats JSON, paper appendix) and mapped to the 44 ids by exact name. Mapping: C++ to cpp, C# to csharp, Shell to bash, Coq and "Rocq Prover" to rocq, Lean and "Lean 4" to lean, Verilog and SystemVerilog to verilog, HTML or CSS to html-css, HCL to hcl, TLA to tlaplus, Clojure, Scheme, Racket, Common Lisp and Emacs Lisp to lisp, PLSQL, PLpgSQL and TSQL to sql.
- Entries that already had single-language catalog tags (73) were copied after an automated check that the fetched text names that language and no other. Two were corrected: minif2f (adds isabelle) and putnambench (adds isabelle, rocq).
- Nothing was inferred from a resource name. Entries with no language statement in any source read are in `unresolved`.

## Result

- Resolved: 131 resources (61 datasets, 55 benchmarks, 10 environments, 5 models).
- Unresolved: 41 (all datasets except metr-time-horizon, a benchmark).
- Tools and papers were skipped. Recipes: none states training languages.

## Counts per language (resolved resources)

| language | datasets | benchmarks | environments | models | total |
|---|---|---|---|---|---|
| python | 53 | 37 | 9 | 5 | 104 |
| cpp | 21 | 16 | 3 | 4 | 44 |
| java | 14 | 15 | 3 | 4 | 36 |
| javascript | 12 | 14 | 3 | 4 | 33 |
| rust | 14 | 8 | 3 | 3 | 28 |
| go | 11 | 10 | 3 | 3 | 27 |
| typescript | 12 | 8 | 3 | 3 | 26 |
| c | 11 | 8 | 2 | 4 | 25 |
| csharp | 13 | 6 | 1 | 3 | 23 |
| php | 12 | 4 | 2 | 3 | 21 |
| bash | 14 | 3 | 0 | 4 | 21 |
| sql | 15 | 2 | 0 | 3 | 20 |
| lean | 10 | 6 | 0 | 3 | 19 |
| ruby | 11 | 3 | 0 | 3 | 17 |
| lua | 10 | 1 | 1 | 3 | 15 |
| swift | 9 | 1 | 1 | 3 | 14 |
| scala | 9 | 1 | 1 | 3 | 14 |
| perl | 9 | 2 | 0 | 3 | 14 |
| julia | 9 | 1 | 1 | 3 | 14 |
| kotlin | 8 | 1 | 1 | 3 | 13 |
| r | 8 | 1 | 1 | 3 | 13 |
| haskell | 9 | 1 | 0 | 3 | 13 |
| html-css | 10 | 0 | 0 | 3 | 13 |
| assembly | 9 | 0 | 0 | 3 | 12 |
| lisp | 7 | 1 | 1 | 3 | 12 |
| ocaml | 7 | 1 | 1 | 3 | 12 |
| elixir | 7 | 1 | 1 | 3 | 12 |
| fortran | 9 | 0 | 0 | 3 | 12 |
| powershell | 9 | 0 | 0 | 3 | 12 |
| isabelle | 7 | 2 | 0 | 3 | 12 |
| ada | 7 | 1 | 0 | 3 | 11 |
| verilog | 7 | 0 | 0 | 3 | 10 |
| vhdl | 7 | 0 | 0 | 3 | 10 |
| zig | 7 | 0 | 0 | 3 | 10 |
| erlang | 7 | 0 | 0 | 3 | 10 |
| matlab | 6 | 0 | 0 | 3 | 9 |
| hcl | 6 | 0 | 0 | 3 | 9 |
| solidity | 6 | 0 | 0 | 3 | 9 |
| wasm | 5 | 0 | 0 | 3 | 8 |
| cobol | 5 | 0 | 0 | 3 | 8 |
| prolog | 6 | 0 | 0 | 2 | 8 |
| rocq | 5 | 1 | 0 | 2 | 8 |
| tlaplus | 4 | 0 | 0 | 1 | 5 |
| dafny | 4 | 0 | 0 | 1 | 5 |

Note: the long tail (tlaplus, dafny, wasm, cobol and similar) is carried almost entirely by the whole-GitHub corpora (The Stack v2 and v3, CommitPack, RefineCode) and by three model language lists. No benchmark or environment in the catalog targets them.

## Not verified

### Unresolved (in `unresolved`, no language list found)

- bespoke-stratos-17k (dataset): card silent
- code-alpaca-20k (dataset): card and repo README give no language list
- code-contests-plus (dataset): card gives no solution-language list (derived from CodeContests: Python, C++, Java)
- code-feedback (dataset): card silent; paper shows the language distribution only as a figure
- codecontests-o (dataset): card names C++ only for generators and checkers; solution languages inherited from CodeContests are not stated
- codefeedback-filtered-instruction (dataset): card lists source datasets only
- codeultrafeedback (dataset): paper says it is a 10k subset of Magicoder Evol-Instruct; no language list
- common-pile-stackv2 (dataset): card gives no list (license-filtered subset of The Stack v2)
- common-pile-stackv2-edu (dataset): card gives no list
- cosmopedia (dataset): synthetic textbook text, no programming language stated
- editpackft (dataset): card says only "filtered from CommitPackFT"
- evol-codealpaca-v1 (dataset): card silent
- evol-instruct-code-80k (dataset): card silent
- finemath (dataset): math web text, no programming language stated
- github-code-clean (dataset): card gives no list (cleaned github-code)
- glaive-code-assistant-v3 (dataset): card silent
- ling-coder-dpo (dataset): card says "several popular programming languages" without a list
- ling-coder-sft (dataset): card says "more than 20 programming languages" without a list
- llama-nemotron-post-training (dataset): card silent on programming languages
- magicoder-evol-instruct-110k (dataset): card silent; derived from evol-codealpaca-v1
- magpie-qwen25-coder-pro-300k (dataset): card silent
- metr-time-horizon (benchmark): paper does not enumerate task languages
- nemotron-agentic-v1 (dataset): tool-calling data, no programming language stated
- nemotron-cc-code-v1 (dataset): gated card
- nemotron-post-training-v1 (dataset): card silent on programming languages
- nemotron-pretraining-code-v1 (dataset): gated card
- nemotron-pretraining-code-v2 (dataset): gated card
- nemotron-pretraining-code-v3 (dataset): card has a language column but no list
- opc-annealing-corpus (dataset): card silent
- opc-fineweb-code-corpus (dataset): card silent
- opc-fineweb-math-corpus (dataset): math web text, no programming language stated
- opc-sft-stage1 (dataset): card silent
- open-web-math (dataset): math web text, no programming language stated
- openthoughts-114k (dataset): card lists source datasets only
- openthoughts3-1.2m (dataset): card silent
- rstar-coder (dataset): card and paper text do not state the solution language in prose
- sky-t1-data-17k (dataset): card silent
- smoltalk (dataset): card silent on programming languages
- stack-exchange-preferences (dataset): Q&A text, no programming language stated
- stack-github-issues (dataset): gated card
- vezora-code-preference-pairs (dataset): card silent

### Weak confirmation (catalog tag copied, language not named in the prose that was fetched)

swe-synth, nemotron-cascade-rl-swe, skywork-or1-rl-data, kodcode, livecodebench, formalmath, evalplus-humanevalplus, evalplus-mbppplus, bigcodebench-hard, evalperf, paperbench, opencodeinstruct, nemotron-sft-swe-v2, nemotron-cascade-sft-swe, kodcode-v1-sft-r1, kodcode-light-rl-10k, nebius-swe-agent-trajectories, nebius-swe-rebench-openhands-trajectories, acecode-87k, acecodepair-300k, jupyter-code-text-pairs

### Partial lists (resolved, but the source covers more than is listed)

- the-stack-v1: only the 30 languages of the paper table were read (22 map to our ids). The 358-language list on the gated card was not read.
- codescope: paper says 43 languages; only the 12 named in task descriptions that map to our ids are listed.
- codestral-22b: card says 80+ languages and names six.
- github-code: card says 32 languages and lists 30.
- opc-sft-stage2, tulu-3-sft-mixture, dolma3-dolmino-mix-100b, starcoder2data-extras: only the languages named on the card are listed; other parts are unlisted.
- terminal-bench-2, terminal-bench-3, nemotron-sft-opencode-v1: tagged bash as the interface language; task or target languages are not enumerated by the source.
- nemotron-swe-trajectories: python by derivation from its three source datasets, not from its own card.
- swe-bench-live, swe-smith: non-Python languages come from sibling datasets (MultiLang, SWE-smith-[lang]), not from the dataset at the catalog URL.
- the-stack-v2 and the-stack-v2-dedup: API shows 658 language configs, the paper says 619; 619 is recorded.
- starcoder2-15b: list inherited from The Stack v2 configs. qwen3-coder-next: list is the "supported languages" list of the Qwen3-Coder repo README.

### Models and recipes left out (card does not state training languages plainly)

acereason-nemotron-14b, alignment-handbook, codellama-70b, deepcoder-14b-preview, deepseek-v3-2, deepseek-v4-1-flash, deepseek-v4-pro, deepswe-preview, devstral-2-123b, devstral-small-2, glm-5-3, glm-5-3-flash, gpt-oss-120b, granite-8b-code-base, kimi-dev-72b, kimi-k3-1-pro, nemotron-3-ultra, nemotron-cascade-14b, olmo-3-32b, open-r1, opencoder-8b, opencoder-repo, openhands-lm-32b, qwen2-5-coder, qwen3-8-27b, qwen3-coder-30b-a3b, qwen3-coder-480b-a35b, recipe-deepcoder, recipe-deepswe, seed-coder-8b, skywork-or1-32b, smollm-recipes, smollm3-3b, swe-agent-lm-32b

granite-8b-code-base says 116 programming languages and nemotron-3-ultra says 43, both without a list on the card.

### Could not fetch

- Gated READMEs (HTTP 401): bigcode/the-stack, the-stack-v2, the-stack-v2-dedup, the-stack-v2-train-smol-ids, starcoderdata, the-stack-github-issues, nvidia/Nemotron-Pretraining-Code-v1 and v2, Nemotron-CC-Code-v1, GAIR/OpenSWE, QAQAQAQAQ/LiveCodeBench-Pro, Virtue-AI-HUB/SecCodePLT.
- GitHub tree API returned 403 (unauthenticated), so repo file listings (PurpleLlama, CWEval, bigcode-dataset) were not read.
