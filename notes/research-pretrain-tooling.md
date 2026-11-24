# Research notes: pretraining corpora and data tooling (checked 2026-11-24)

## Dropped or not included
- bigcode/the-stack-inspector, pii-annotated-toxic-dataset, commit-chronicle (bigcode), stack-exchange-preferences (bigcode), common_pile_v0.1, smollm3-pretrain-mix, jupyter-structured-clean-dedup, the-stack-v2-train-extras, starcoder2-instruct-data, ibm CodeAlchemy, stack-edu-classifier models' license: HF API returned "not found" or auth errors for the ids I tried, so no entry (or null license).
- IBM CodeAlchemy and MegaCode (EMNLP 2026 Findings) surfaced in search only; I could not find a verifiable HF id or repo, so they are not listed.
- MegaMath, Zyda-2, Dolma3 6T mix: ids not resolvable via HF API here.
- Gated cards (Stack v1/v2, StarCoderData, Nemotron code sets) could not be read without login. Sizes for them come from the Stack v3 card table or NVIDIA's research page and are cited as such; unverified fields are null or flagged.
- The HF API rate-limited me late, so StarPII and Stack-Edu classifier model licenses are unverified.

## Practical insights
- Pipeline order that The Stack v3 card documents: language detection (go-enry), license detection (ScanCode on license files, propagate down the directory tree), MinHash-LSH near dedup (256 perms, 5-grams, Jaccard 0.7), quality heuristics, PII redaction (StarPII).
- Dedup before decontamination, and decontaminate against all eval sets (HumanEval, MBPP, LiveCodeBench, SWE-bench repos) after final mixing; synthetic data seeded from benchmarks can leak.
- License filter first if policy is permissive-only: it shrinks the data and saves dedup compute. Note Stack v3 keeps "no_license" files; Common Pile keeps only Blue Oak licensed ones.
- Many "datasets" are metadata only (Stack v2, Stack-Edu, RefineCode meta, Nemotron code metadata): you must refetch contents from Software Heritage S3 or GitHub, which has attrition and rate limits.
- Dataset-level license labels (odc-by, MIT, Apache) do not relicense contained code.
- Count tokens with your own tokenizer; code token counts vary a lot by tokenizer.

## Surprising
- The Stack v3 (HuggingFaceCode, July 2026) is ungated, odc-by, has file contents inline and a 2025-08 GitHub cutoff; v3.1 cut tokens from 4.9T to 3.6T after removing leaked exact duplicates.
- Nemotron-Pretraining-Code v1/v2/v3 are incremental metadata lists, v3 being open (cc-by-4.0) while v1/v2 are manually gated.
- google-research/deduplicate-text-datasets and fastText are archived; facebookresearch/fastText was not listed as an entry.
- Memory caution: suffix-array and MinHash dedup at scale can exhaust RAM; chunk and cap.
