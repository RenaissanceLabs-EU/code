# Research notes: stack gaps (checked 2026-11-24)

Output: data/resources/stack-gaps.json, 65 new entries (43 benchmark, 16 dataset, 4 environment, 2 tool).
No id and no url collides with docs/data/resources.json (319 entries; ids and urls, including extra_links, were compared by script).
Each entry has the existing schema plus `levels` (stack level ids) and `layers` (program layer ids) from the rebuild brief.

## Method
- Read the catalog ids, the schema in data/resources/evals.json and data/taxonomy.json first.
- For every candidate: GitHub API (`gh api repos/X`, README, LICENSE file, last commit) and/or Hugging Face API
  (`/api/datasets/X`, raw README.md, datasets-server `/size`), plus the arXiv API abstract for the paper.
  Zenodo API for the two Zenodo records. All fetched 2026-11-24.
- Where GitHub reported the license as NOASSERTION I read the LICENSE file itself and say so in the entry.
- Numbers in `size` come from the HF API, the README or the paper abstract, and the entry says which.
  Where two sources disagree, both are given (CVDP, Decompile-Bench, NL2SH-ALFA, SUPER, xCodeEval).
- Hugging Face keyword search (sorted by downloads) for: code review, merge conflict, wasm, webassembly, vhdl, llvm,
  terraform, kubernetes, dockerfile, type inference, linux kernel, syzbot, decompil, verilog, transpil, refactor,
  vulnerab, execution trace.
- "released" is the arXiv first-version month when there is a paper, otherwise the HF or GitHub creation month
  (stated in caveats or evidence where it is a repository creation date: Csmith, TypyBench, BinKit, WasmBench, syzkaller).

## Entries per category
| # | Category | Entries | Ids |
|---|---|---|---|
| 1 | Hardware description | 5 | verilogeval, rtllm, cvdp, verigen-verilog-github, rtl-repo |
| 2 | Machine level | 5 | exebench, decompile-bench, decompile-bench-eval, binkit, wasmbench |
| 3 | Compilers | 7 | compilergym, compile-llvm-ir, llvm-apr-benchmark, csmith, codetransocean, crust-bench, xcodeeval |
| 4 | Operating systems | 5 | kgym, syzkaller, nl2bash, nl2sh-alfa, intercode |
| 5 | Types | 4 | manytypes4py, manytypes4typescript, typeevalpy, typybench |
| 6 | Execution | 3 | reval, codemind, semcoder-pyx |
| 7 | Change over time | 8 | commitbench, commit-chronicle, codereviewer-data, codereviewqa, congra, refactorbench, migrationbench, lca-ci-builds-repair |
| 8 | Networks and infrastructure | 5 | iac-eval, cloudeval-yaml, netconfeval, aiopslab, itbench |
| 9 | Security | 7 | primevul, cvefixes, cybergym, baxbench, sec-bench, cybench, nyu-ctf-bench |
| 10 | Applications and data | 8 | design2code, websight, web-bench, spreadsheetbench, arcade-nl2code, da-code, dabstep, elt-bench |
| 11 | Learned programs | 8 | mlagentbench, mlgym, re-bench, ml-bench, core-bench, super-benchmark, kernelbench, researchcodebench |

## Gaps (nothing solid found, or thin)
- VHDL: no solid entry. Everything verified is Verilog or SystemVerilog. HF search for "vhdl" returned only small
  scrapes with few downloads and mostly no license (for example rtl-llm/vhdl_github, NOKHAB-Lab/LLM_4_VHDL,
  Si2-LBC-Hub/VHDLBench created 2026-11-23); none was read closely enough to include.
- WebAssembly: one corpus of binaries (WasmBench, 2021), no tasks. No open LLM benchmark for WebAssembly found.
  JeremiahZ/humaneval_x_llvm_wasm exists on HF but has no license and 36 downloads; not included.
- Transistors and physics level: nothing looked for, nothing added.
- Operating system configuration and system administration: no dedicated open task set found beyond the shell
  datasets and the incident-response environments (AIOpsLab, ITBench), which are filed under networks with `os` as
  a second level. Kernel work is covered only by kGym/kBench.
- Kernel patch datasets: HF search for "linux kernel" and "syzbot" gave only small, recent, unreviewed uploads. Not included.
- Compiler fuzzing data: no dataset found; Csmith (a generator) and the LLVM APR benchmark stand in. llvm-test-suite
  exists (Apache-2.0 with LLVM exceptions) but is a compiler test suite, not model data; not included.
- Execution traces: no large open trace dataset with a clear license and documentation found. PyX is the nearest
  (model-written execution explanations), and its HF card is empty. HF search results for "execution trace" were
  2026 uploads from unknown publishers with no paper; not included.
- Merge conflicts: only ConGra, which has no license. HF search found nothing usable.
- Code review: CodeReviewer data (2022) and CodeReviewQA (gated). The newer HF hits (for example
  code-review-bench/code-review-bench, whitney-ai/code-review-rl) were not read and are not included.
- Dockerfile and Kubernetes training data: no vetted dataset. HF results were small or from unknown publishers.
  Only evaluation sets (IaC-Eval for Terraform, CloudEval-YAML for Kubernetes, Envoy and Istio) are included.
- Distributed systems and protocol tasks (consensus, protocol implementation): nothing found.
- Training data in general: most of these categories have benchmarks but little open training data. Exceptions:
  Verilog_GitHub, ExeBench, Decompile-Bench, ComPile, CommitChronicle, CommitBench, CodeReviewer, WebSight,
  ManyTypes4Py/TypeScript, PyX, NL2SH-ALFA train, PrimeVul, CVEfixes.

## Rejected or left out, and why
- DiverseVul (wagner-group/diversevul): repository holds only a README, no license, data on Google Drive. PrimeVul
  covers the same need with better labeling.
- CVE-Bench (uiuc-kang-lab/cve-bench): verified (Apache-2.0, active), but the task is exploiting web applications.
  Left out to keep the security set to detection, repair, secure generation and standard CTF evaluation.
- PyraNet-Verilog (bnadimi/PyraNet-Verilog): gated, CC-BY-NC-SA-4.0, card not readable without login. Left out.
- MG-Verilog (GaTech-EIC/MG-Verilog): MIT on HF, but the viewer shows no splits and I did not read sizes. Left out.
- jTrans / BinaryCorp (vul337/jTrans): code is MIT, but the dataset is on a private cloud link. BinKit kept instead.
- AVATAR (wasiahmad/AVATAR): archived, and the README opens with a notice about a major dataset bug. Left out.
- Project CodeNet (IBM/Project_CodeNet): verified (Apache-2.0 repository, active), but it is a general competitive
  programming corpus and its translation use overlaps xCodeEval. Left out to limit the compilers category.
- kubectl-ai k8s-bench: the repository exists (Apache-2.0) but the k8s-bench path returned 404 through the API. Not included.
- SREGym: the GitHub path I tried redirected to a repository with a different name and 0 stars. Not included.
- DSBench (LiqiangJing/DSBench): verified MIT and ICLR 2025, but DA-Code and DABstep already cover agentic data
  science; left out for balance, could be added.
- RefactorBench, MLGym, RE-Bench, CompilerGym, ARCADE are included although archived; each entry says so.
- Long Code Arena: only the CI builds repair set is included (the one that fits "change" and infrastructure). The
  other five LCA datasets were not checked individually.
- kGymSuite is an extra link on the kgym entry, not its own entry.

## Not verified
- TypyBench paper link (openreview.net/pdf?id=xl9sv9vEDy) returns 403 to scripts and the OpenReview API did not
  answer; the link is the repository's homepage field. ICML 2025 is from the repository description only.
- ACM links for ExeBench and NetConfEval return 403 to scripts; both DOIs resolve through the doi.org handle API.
- CodeReviewQA: gated, so the card, row counts and data format were not read. Size is null.
- DA-Code: task count not verified (size is null).
- kGym: size of the original (smaller) kBench set not verified; only the 504-bug C-reproducer set from the README.
- InterCode: whether the repository still ships a CTF environment was not checked; the entry names only the Bash,
  SQL and Python environments from the paper abstract.
- CyberGym languages (c, cpp) come from the project_language field of a few sampled rows, not a full count.
- SEC-bench languages: the lang column reads "c++" for all 300 rows; I list c and cpp.
- CVDP: what the "commercial" and "no_commercial" config names mean was not read; the entry tells users to read the card.
- RTLLM: the per-design file layout and the count of designs in v2.1 (the README gives 50 for v2.0).
- VerilogEval: 156 problems is from the 2023 paper abstract; the count in the current repository was not recounted.
- ComPile: the viewer row count (37,305) was not used because its meaning (rows vs. modules) was not checked.
- CompilerGym: only the LLVM environments were confirmed in the README text read.
- Venue claims (NeurIPS, ICLR, ICML, EMNLP, ICSE, WWW) are taken from the projects' own READMEs or repository
  descriptions, not from proceedings.
- "At release" scores quoted in caveats are from paper abstracts and are not current leaderboard values.
- No dataset was downloaded or loaded; load snippets use config and split names seen in the HF API but were not executed.

## URL check
All 65 entry urls returned HTTP 200 on 2026-11-24 (HF dataset pages checked through the API endpoint). Extra
links also returned 200 except the three bot-blocked links listed above. arXiv links were confirmed by matching
each id to its title through the arXiv API.
