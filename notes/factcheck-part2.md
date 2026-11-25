# Fact-check of part two prose pages (2026-11-25)

Pages: data/pages/capability.html, data.html, evaluate.html, build-dataset.html. Checked against sources fetched on 2026-11-25, docs/data/resources.json, data/snippets.json, examples/build-dataset (RUN_LOG.md, out/logs, out/ files), and the 15-test suite (run: 15 tests, OK).

## Wrong

1. capability.html, approaches table, SFT row.
   Quote: "From about a thousand carefully chosen examples (LIMA) to hundreds of thousands (the OSS-Instruct set has 75,000 rows)."
   Wrong: 75,000 is tens of thousands, not hundreds of thousands (Magicoder-OSS-Instruct-75K has 75,197 rows by the HF datasets server). LIMA is also a general alignment study, not a code study.
   Source: https://datasets-server.huggingface.co/size?dataset=ise-uiuc/Magicoder-OSS-Instruct-75K ; https://arxiv.org/abs/2305.11206
   Corrected: "From about a thousand carefully chosen examples (LIMA, a general instruction-tuning study) to tens of thousands (the OSS-Instruct set has about 75,000 rows) and millions (OpenCodeInstruct has 5 million)."

2. data.html, section 4 table, Tokens row.
   Quote: "fill-in-the-middle splits at token or line boundaries."
   Wrong: the standard recipe applies fill-in-the-middle to the raw text at the character level, before tokenization. The original FIM paper (Bavarian et al.) recommends character-level spans and reports token-level spans did worse; line-level spans are a variant some recipes use.
   Source: https://arxiv.org/abs/2207.14255 (section on character-level vs token-level FIM, read from the PDF)
   Corrected: "fill-in-the-middle splits the text at random character positions before tokenization (some recipes use whole lines)."

3. build-dataset.html, section 7.
   Quote: "Pairs inherit the split of their source file, so a function never appears in train and test."
   Wrong: inheriting the file's split keeps one file out of two splits, but identical functions in different files can land in different splits. In the delivered data, 3 identical responses and 6 identical instructions appear in more than one split (the three responses checked are in both train and test; examples: `_get_normal_name`, `islink`, `get_config_var`). Pairs are not deduplicated across splits and decontamination only compares train files against the eval probe.
   Source: examples/build-dataset/out/docstring_pairs/{train,validation,test}.jsonl (compared with a short script).
   Corrected: "Pairs inherit the split of their source file, so one file never feeds two splits. Identical functions in different files can still land in different splits (3 responses appear in both train and test in this run), so deduplicate pairs across splits too if you need a strict split."

4. build-dataset.html, section 10 table, Format row.
   Quote: "About 2.3 million estimated tokens; 12.8 MB"
   Wrong: the JSONL files total 13,343,564 bytes, which is 13.3 MB (12.7 MiB). RUN_LOG.md gives 13.4 MB for all of out/. Neither is 12.8. The token estimate is right (2,338,183).
   Source: examples/build-dataset/out/, RUN_LOG.md.
   Corrected: "About 2.3 million estimated tokens; 13.3 MB of JSONL."

5. build-dataset.html, section 9, embedded 08_push.sh (`hf repo create`, `hf repo tag create ... -m`).
   Wrong for current releases: huggingface_hub main registers only `hf repos` (`hf repos create`, `hf repos tag create`, option `-m/--message`); there is no `hf repo` group. The current CLI guide documents `hf repos`. `hf repo` works in 0.36.0 (checked locally with --help). PyPI latest is 2.4.0; I checked main-branch source, not the 2.4.0 wheel itself, so the exact version where `repo` disappeared is not verified. `hf auth login` and `hf upload REPO out . --repo-type dataset --commit-message` are correct.
   Source: https://huggingface.co/docs/huggingface_hub/guides/cli ; https://raw.githubusercontent.com/huggingface/huggingface_hub/main/src/huggingface_hub/cli/repos.py ; https://raw.githubusercontent.com/huggingface/huggingface_hub/main/src/huggingface_hub/cli/hf.py
   Corrected: use `hf repos create ...` and `hf repos tag create ... -m ...` (in huggingface_hub 0.36 the same commands are spelled `hf repo ...`), or use the Python calls already in the script comments.

## Needs a qualifier

1. build-dataset.html, intro.
   Quote: "The whole pipeline uses only Python 3.9's standard library, needs no network, ... and produces byte-identical output when you run it again."
   Missing: only the core stages (01 to 07) are standard-library only. 09_check_load.py needs `datasets` and 08_push.sh needs huggingface_hub. Byte-identical holds on the same stdlib tree and with the fixed settings in run_all.sh (PYTHONHASHSEED=0, fixed RETRIEVAL_DATE). The corpus here is Apple's Xcode Python framework 3.9 tree; a different 3.9.6 build may differ.
   Corrected: "The core pipeline uses only Python 3.9's standard library, needs no network, ... and, on the same Python tree with the settings in run_all.sh, produces byte-identical output when you run it again."

2. build-dataset.html, second paragraph.
   Quote: "its license is clear (PSF License Version 2, read from the license file next to the source)."
   Missing: the Python docs say some incorporated software is under different licenses, and the run itself found files under other terms (14 dropped for unmapped notices; 3 kept under Apache-2.0 or MIT OR Apache-2.0 per the card). The PSF license covers Python itself.
   Source: https://docs.python.org/3.9/license.html ; out/logs/stage_06_format.json
   Corrected: "its main license is clear (PSF License Version 2, read from the license file next to the source), though a few files carry other notices, which the license step handles."

3. build-dataset.html, section 2.
   Quote: "The example has none, because its source is the PSF's own standard library."
   Missing: the standard library includes third-party code (see item 2), so "PSF's own" is not accurate.
   Corrected: "The example has none, because its source is the Python standard library, which the PSF publishes."

4. build-dataset.html, section 6.
   Quote: "Result: 523 files for training, 16 for validation, 49 for test"
   Missing: the split step itself gave 524 train files (stage_05_split.json); 523 is after decontamination removed colorsys.py, which the next paragraph describes.
   Corrected: "Result: 524 files for training, 16 for validation, 49 for test (523 for training after the decontamination step below)".

5. build-dataset.html, section 10.
   Quote: "almost all of it in the MinHash step"
   Missing: 04_dedup took 15.9 s of about 21 s (75 percent), and that stage includes exact dedup and LSH. RUN_LOG.md run 2.
   Corrected: "most of it in the deduplication step (about 16 of 21 seconds)".

6. build-dataset.html, section 0.
   Quote: "which is why The Stack v1.1 excluded MPL, EPL and LGPL code."
   Missing: the exclusion is confirmed, but the card gives no reason for it (it only calls them weak copyleft). The causal "which is why" is the site's inference.
   Source: https://huggingface.co/datasets/bigcode/the-stack
   Corrected: "The Stack v1.1 excluded MPL, EPL and LGPL code, which its card calls weak copyleft."

7. build-dataset.html, section 0, permissive list.
   Quote: "Files under permissive licenses (MIT, BSD, Apache-2.0, PSF-2.0, 0BSD) can be combined and republished if their notices travel with them."
   Missing: obligations differ. Apache-2.0 also asks for the license text, NOTICE content and a statement of changes; PSF-2.0 requires a brief summary of changes to derivative works (paragraph 3); 0BSD requires no notice.
   Source: https://docs.python.org/3.9/license.html
   Corrected: "... can be combined and republished if you meet each license's terms: keep the license text and notices, and where required (Apache-2.0, PSF-2.0) say what you changed. 0BSD asks for nothing."

8. build-dataset.html, section 0 table.
   Quote: "None of the code licenses." and "Copies and derived records are copies or derivative works of the source."
   Missing: these are legal conclusions that depend on jurisdiction (for example database rights in the EU) and on how much text the entry copies. Page already has a not-legal-advice line later; put the hedge at the claim.
   Corrected: "In general, none of the code licenses, because you are not copying the code (local law may add database or other rights)." and "Copies are copies of the source, and derived records usually count as derivative works."

9. build-dataset.html, section 1 link ("Get the code" callout).
   Missing: https://github.com/RenaissanceLabs-EU/code/tree/main/examples/build-dataset returned HTTP 404 when fetched now (not pushed or not public). Same repo path is used for the card link in section 8. The three tool links (bigcode pii, detect-secrets, gitleaks) and datatrove and bigcode near_deduplication return 200.
   Corrected: publish the repository before the page goes live.

10. data.html, tradeoffs table, Quality row.
    Quote: "The OpenCoder study found that keeping only popular repositories by star count hurt a small model."
    Missing: the test (section 6.3) trained two 1.5B models, one on all data and one on repositories with at least 5 stars; the unfiltered model did better. A 5-star cutoff is a low bar, and it is a single comparison.
    Source: https://arxiv.org/html/2411.04905
    Corrected: "The OpenCoder study trained two 1.5B models and found that keeping only repositories with at least 5 stars did worse than keeping all of them, which the authors attribute to lost diversity."

11. data.html, tradeoffs table, Diversity row.
    Quote: "Diversity of problems often matters more than verifying each solution. The OpenCodeReasoning authors report this in their ablations."
    Missing: the abstract says they "prioritize instruction diversity over solution correctness." The ablation (section 4.1) is one CodeContests subset with Qwen2.5-14B-Instruct: all 445,618 samples 54.1 on LiveCodeBench, correct-only 47.0, incorrect-only 52.3. The diversity claim itself comes from scaling the number of unique questions, not from an ablation of diversity against verification.
    Source: https://arxiv.org/abs/2504.01943
    Corrected: "Diversity of problems can matter more than verifying each solution. The OpenCodeReasoning authors found that, in one setup, filtering to solutions that pass tests scored lower than keeping all of them, and that adding more unique questions gave the largest gains."

12. capability.html, approaches table, pretraining row.
    Quote: "StarCoder2 trained on 3.3 to 4.3 trillion tokens"
    Missing: the figure is tokens seen in training. The training data holds roughly 0.6 to 0.9 trillion unique tokens (622B, 658B, 913B for 3B, 7B, 15B per the paper), repeated over several epochs. The figure is accurate to the abstract.
    Source: https://arxiv.org/abs/2402.19173
    Corrected: "StarCoder2 was trained on 3.3 to 4.3 trillion tokens (counting repeated passes over a smaller dataset)."

13. capability.html and evaluate.html, SWE-bench Verified.
    Missing: OpenAI stopped reporting SWE-bench Verified on 2026-02-23, citing flawed tests (at least 59.4 percent of an audited 27.6 percent subset of hard problems; 35.5 percent too narrow, 18.8 percent testing unspecified behavior) and training-data contamination. The pages list it as a standard measure with only a generic "some items have flawed tests" line in evaluate.html.
    Source: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
    Corrected: add after the repository-level row: "SWE-bench Verified is still widely reported, but OpenAI stopped using it in February 2026 because of flawed tests and contamination; treat its numbers as upper bounds and add a contamination-resistant set such as SWE-bench-Live."

14. capability.html, debugging row, "How you measure it".
    Quote: "{{r:humanevalpack}}, {{r:canitedit}}, {{r:swe-bench-verified}}" under Debugging and repair.
    Missing: CanItEdit measures instruction-driven code editing, not repair specifically; HumanEvalPack covers repair (fix), explanation and synthesis, so only its fix tasks measure repair.
    Source: https://arxiv.org/abs/2312.12450 ; https://arxiv.org/abs/2308.07124
    Corrected: "HumanEvalPack (its fix tasks), CanItEdit (instructional editing), SWE-bench Verified."

15. capability.html, test generation row.
    Quote: "KodCode (tests as targets), AceCode-V2-122K"
    Missing: both datasets pair questions and solutions with tests used to validate solutions. Using the tests as training targets is the reader's own transformation, and I found no source describing them as test-generation sets.
    Corrected: "KodCode and AceCode-V2-122K (they ship tests with each problem; you would turn the tests into targets yourself)".

16. data.html, section 1, Documentation and Q&A row.
    Quote: Examples "{{r:stack-exchange-preferences}}, {{r:smollm-corpus}}"
    Missing: SmolLM-Corpus is FineWeb-Edu web text, Cosmopedia synthetic textbooks and Python-Edu code, so it is mostly not documentation or Q&A.
    Corrected: drop it from this row, or write "SmolLM-Corpus (educational web text, synthetic textbooks and Python-Edu)".

17. data.html, section 4 table, Types row.
    Quote: "Type data is thin in most languages and mostly in Python and TypeScript."
    Missing: no source. Say it as a judgment or cite the type-annotation coverage you rely on.
    Corrected: "Type annotations are common mainly in Python and TypeScript code; most other languages have little type-prediction data."

18. data.html, tradeoffs table, Difficulty row.
    Quote: "a model that fails all of them learns nothing from RL."
    Missing: true for outcome-reward methods that normalize within a group of samples (GRPO style), where an all-zero group gives no gradient. Other methods or partial-credit rewards differ.
    Corrected: "with group-based RL such as GRPO, a model that fails every sample learns nothing from that problem."

19. evaluate.html, section 4.
    Quote: "A Docker container shares the host kernel" and "the reward function runs inside the sandbox" (followed by the subprocess snippet).
    Missing: on macOS and Windows, Docker Desktop containers share the kernel of its Linux VM, not the host's. The snippet itself says it is not a security sandbox (no network or file isolation; memory and process limits apply only on Linux), so the reward function must be run inside the container.
    Source: data/snippets.json (code-reward-subprocess, docker-hardened-sandbox)
    Corrected: "A Docker container shares the kernel of the Linux host (or of Docker Desktop's Linux VM)." and "For RL, run the reward function inside the sandbox; the snippet below limits time and resources but does not isolate anything by itself."

## Confirmed

- StarCoder2 abstract: "3B, 7B, and 15B parameters on 3.3 to 4.3 trillion tokens" (arXiv 2402.19173).
- Code Llama: initialized from Llama 2 weights; 500B tokens for 7B, 13B, 34B; 1T for 70B (arXiv 2308.12950, read from PDF).
- LIMA: "only 1,000 carefully curated prompts and responses" (arXiv 2305.11206).
- OSS-Instruct: 75,197 rows (HF datasets server).
- DeepCoder-Preview-Dataset card: "24K problems paired with their test cases"; the 24K count is a training-set size of the released dataset.
- AceCodePair-300K: 307,019 rows in default config (HF API), so "hundreds of thousands" holds; the page quotes no DPO result numbers.
- OpenCoder star filtering experiment exists (qualified above).
- OpenCodeReasoning "prioritize instruction diversity over solution correctness" is in the abstract (qualified above).
- EvalPlus: HumanEval tests "limited in quantity and quality"; HumanEval+ extends tests 80x (arXiv 2305.01210); the weak-tests statement is right.
- LiveCodeBench: continuously collected problems published May 2023 to May 2024 for v1 abstract; release dates recorded per problem (arXiv 2403.07974).
- The Stack v1.1 excluded MPL, EPL, LGPL (card changelog; reason unstated).
- The Stack v2 card: repository-level licenses from GH Archive, ScanCode file-level detection when missing, propagation to files with the same base path; opt-out and removal requests with an "Am I In The Stack?" Space.
- PSF license paragraphs 2 and 3: retain license and copyright notice; include a brief summary of changes in derivative works.
- HF Hub license list has no PSF entry; `license: other` needs a LICENSE file and `license_name`; `license_link` of "LICENSE" or "LICENSE.md" links to a file in the repo (hub-docs datasetcard.md).
- `hf auth login`; `hf upload REPO LOCAL PATH_IN_REPO --repo-type --commit-message`; `--private`, `--exist-ok`, `--repo-type` on create (CLI guide).
- LSH: P(candidate | J=0.8) = 1-(1-0.8^4)^16 = 0.99978 > 0.999 (computed); at J=0.7 it is 0.988, at 0.5 it is 0.644. 16 bands of 4 rows = 64 permutations as stated.
- Every Docker flag in docker-hardened-sandbox exists and does what the page says (Docker run reference; `--memory-swap` equal to `--memory` disables swap; snippet was also run on Docker 29.1.3 per its note). gVisor (user-space kernel) and Firecracker (microVM) descriptions are right; both are in the tools catalog (sb-gvisor, sb-firecracker).
- SAFIM: syntax-aware FIM, 17,720 examples from code after April 2022 (arXiv 2403.04814).
- RepoBench: repository-level completion in Python and Java (arXiv 2306.03091). CrossCodeEval: cross-file completion, static-analysis construction, Python, Java, TypeScript, C# (arXiv 2310.11248).
- HumanEvalPack: HumanEval extended to six languages and repair, explanation, synthesis (arXiv 2308.07124).
- TestGenEval: test authoring, 68,647 tests from 1,210 code-test pairs in 11 Python projects, based on SWE-bench (arXiv 2410.00752).
- SWT-bench: LLM agents turn GitHub issues into test cases; evaluated by reproduction rate and coverage change (arXiv 2406.12952).
- Terminal-Bench 2.0: hard command-line agent tasks (arXiv 2601.11868). InterCode: interactive coding as RL environments with Bash, SQL, Python and execution feedback (arXiv 2306.14898).
- Run numbers match out/logs and RUN_LOG.md: 682 seen, 6 non-UTF-8, 2 over 200 KB, 674 kept; 24 too small, 3 auto-generated, 14 license gate, 633 out; 163 emails in 119 files, 10 global IPv4, 1 password literal, 127 files changed, 633 of 633 still parse; no exact duplicates, 44 near-duplicates in 16 clusters, all under encodings/, Jaccard 0.801 to 0.98, 589 out; split 524/16/49 then 523 after decontamination, 0 groups in two splits; 220 overlapping 13-grams, 1 file removed (colorsys.py), 588 files; 3,471 pairs (318, 2,909, 244); 2.34 million estimated tokens; two runs identical; 20.56 and 21.19 s; peak 46 MB; 15 tests pass (re-run now).
- Schema field lists for code_corpus and docstring_pairs match the JSONL keys. Card YAML (license other, license_name, license_link, configs with splits) matches what the page says.
- Catalog entries linked by {{r:...}} match the page's use (license, size, kind) except as flagged above.
