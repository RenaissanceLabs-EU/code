# Build a documented code dataset: a worked, reproducible example

This folder takes source code from a provenance-clear source to a versioned, documented dataset that is ready to push to the Hugging Face Hub. Core pipeline: Python 3.9, standard library only, no network. Everything below was run on 2026-11-25; see `RUN_LOG.md` for commands, timings, memory and every count.

Corpus: the CPython 3.9.6 standard library read from the local Python installation (PSF License Version 2, text read from `LICENSE.txt` next to the source; its sha256 is recorded). The tree has no top-level `test` directory, so test-file pairing was dropped.

Result of the run: 682 `.py` files seen, 588 in the released `code_corpus` (about 2.3 million estimated tokens), 3,471 `docstring_pairs`, 13.4 MB in `out/`.

## Run it

```
cd examples/build-dataset
./run_all.sh                                   # about 20 seconds, under 50 MB of RAM
python3 -m unittest discover -s tests -v       # 15 tests
python3 -W ignore 09_check_load.py             # optional: loads out/ with the datasets library
```

Two runs from scratch gave identical sha256 for every file in `out/` (`out/SHA256SUMS`). To use another tree set `STDLIB_DIR`; the license check will refuse a tree whose `LICENSE.txt` does not contain the PSF license text.

## Stages

| Script | What it does | Output |
|---|---|---|
| `01_collect.py` | Walks the tree in sorted order. Records relative path, source tree and version, license identifier, license file sha256, content sha256, size, retrieval date. Skips non-UTF-8 files and files over 200,000 bytes. Detects third-party license headers per file (Apache-2.0, MIT, and unmapped HPND-style and BSD-style notices). | `data/raw.jsonl` |
| `02_filter.py` | Quality rules with a count for each: minimum size (150 bytes), max lines (5,000), max line length (1,000), average line length (100), alphanumeric fraction (0.25), auto-generated header in the first five lines. Then the license gate against `allowed_licenses.json`. | `data/filtered.jsonl` |
| `03_scrub.py` | Regex scrubber, see below. | `data/scrubbed.jsonl`, `out/logs/scrub_hits.jsonl` |
| `04_dedup.py` | Exact dedup by content sha256, then near-dedup: MinHash (64 permutations, seed 1337) over token 5-shingles, 16 bands of 4 rows for LSH, candidates confirmed by exact Jaccard >= 0.8, union-find clusters, the lexicographically smallest path is kept. | `data/deduped.jsonl` |
| `05_split.py` | Splits by group (top-level package directory, or module name for a top-level file) with `sha256(salt:group) mod 100`. Asserts that no group appears in two splits. | `data/split.jsonl`, `out/split_check.json` |
| `decontaminate.py` | Removes train files that share a token 13-gram with an evaluation file. | `data/split_decon.jsonl`, `out/logs/decontamination.json` |
| `06_format.py` | Writes the two record types, one file per split. | `out/code_corpus/*.jsonl`, `out/docstring_pairs/*.jsonl` |
| `07_card.py` | Writes the dataset card from the logs. | `out/README.md` |
| `08_push.sh` | Creates the dataset repo, uploads `out/`, tags the version. Not run; needs `REPO_ID` and `CONFIRM_PUSH=yes`. | |

### Counts from the run

| Step | In | Out | Dropped or changed |
|---|---|---|---|
| collect | 682 seen | 674 | 6 non-UTF-8, 2 over the size cap |
| filter | 674 | 633 | 24 too small, 3 auto-generated header, 14 license gate |
| scrub | 633 | 633 | 127 files changed |
| dedup | 633 | 589 | 0 exact, 44 near duplicates in 16 clusters (all in `encodings/`) |
| split + decontaminate | 589 | 588 | 1 train file removed (planted overlap) |

### What the scrubber does and cannot do

Rules (`03_scrub.py`): private key blocks, AWS access key ids (`AKIA` plus 16 characters), GitHub tokens (`ghp_` and the other `gh?_` prefixes), generic `password = "..."` style assignments (also `passwd`, `pwd`, `secret`, `api_key`), e-mail addresses, and globally routable IPv4 addresses. Loopback, private and documentation addresses are kept on purpose (`127.0.0.1` in examples is not personal data and replacing it breaks doctests). Replacements: 0 keys, 0 AWS ids, 0 GitHub tokens, 1 password literal, 163 e-mail addresses in 119 files, 10 IPv4 addresses. The log holds rule, path and line, never the matched text. After scrubbing every file that parsed before still parses with `ast`.

A regex scrubber cannot catch: secrets with no fixed format (random passwords in config files, bearer tokens without a prefix), names and other personal data in prose or comments, usernames in file paths, private information that is not a string pattern, and secrets split across lines or encoded. It also produces false positives (author addresses in headers). Stronger tools:

- BigCode PII pipeline: https://github.com/bigcode-project/bigcode-dataset/tree/main/pii (its README describes an NER model approach for names, emails, keys, passwords and IP addresses, and a regex approach, plus detect-secrets with extra filters).
- detect-secrets (Yelp, Apache-2.0): https://github.com/Yelp/detect-secrets
- gitleaks (MIT): https://github.com/gitleaks/gitleaks

All three links were fetched on 2026-11-25. For a real dataset, run at least one of them and review a sample by hand.

### Leakage and contamination

Related files in one package share names, helper functions and copy-pasted blocks. A random file-level split would put near copies in train and test and inflate scores. Grouping by package keeps them together (the check in `out/split_check.json`: 0 groups in more than one split). The group is the top-level directory, so `encodings` (78 files) stays whole in train and `email` (28 files) stays whole in test; sizes follow the hash, so validation is small (16 files).

Benchmark contamination is separate: a train file can contain a benchmark problem or its solution. `decontaminate.py` removes train files with a 13-token overlap. `eval_probe.jsonl` holds three problems written for this demo. Problem `probe-02` reuses the body of `colorsys.rgb_to_hsv` on purpose. The run found 220 overlapping 13-grams, removed `colorsys.py` from train, and left the other two problems alone. In real use pass the actual benchmark files (HumanEval, MBPP, and any benchmark you evaluate on). Removal is whole-file, which is blunt; cutting out the function is an option.

## Example records

Real output, strings shortened to 160 characters (`out/code_corpus/validation.jsonl`, first two records):

```json
{"id": "b16008396f44e302", "repo": "_pyio", "path": "_pyio.py", "language": "python", "license": "PSF-2.0",
 "sha256": "18219c71...5a129e72", "source_sha256": "18219c71...5a129e72", "n_tokens_estimate": 23353,
 "split": "validation", "source_version": "cpython-stdlib-3.9.6",
 "content": "\"\"\"\nPython implementation of the io module.\n\"\"\"\n\nimport os\nimport abc\nimport codecs\nimport errno\nimport stat\nimport sys\n# Import _thread instead of threading to [...]"}

{"id": "b39619937b22e8d2", "repo": "_threading_local", "path": "_threading_local.py", "language": "python", "license": "PSF-2.0",
 "sha256": "e1bf3dae...ef29cb", "source_sha256": "e1bf3dae...ef29cb", "n_tokens_estimate": 1805,
 "split": "validation", "source_version": "cpython-stdlib-3.9.6",
 "content": "\"\"\"Thread-local objects.\n\n(Note that this module provides a Python version of the threading.local\n class.  Depending on the version of Python you're using, ther [...]"}
```

`out/docstring_pairs/validation.jsonl`, first two records:

```json
{"id": "0d69675883e850a8", "source_id": "163f083a8d3a678c", "license": "PSF-2.0", "split": "validation", "qualname": "insort_left",
 "instruction": "Write the Python function below. Its docstring is:\n\nInsert item x in list a, and keep it sorted assuming a is sorted.\n\nIf x is already in a, insert it to the le [...]",
 "response": "def insort_left(a, x, lo=0, hi=None):\n    lo = bisect_left(a, x, lo, hi)\n    a.insert(lo, x)"}

{"id": "785dd109985d3cb4", "source_id": "163f083a8d3a678c", "license": "PSF-2.0", "split": "validation", "qualname": "insort_right",
 "instruction": "Write the Python function below. Its docstring is:\n\nInsert item x in list a, and keep it sorted assuming a is sorted.\n\nIf x is already in a, insert it to the ri [...]",
 "response": "def insort_right(a, x, lo=0, hi=None):\n    lo = bisect_right(a, x, lo, hi)\n    a.insert(lo, x)"}
```

The `sha256` values are shortened here with `...`; the files hold the full 64 characters. The pair instruction ends with the signature line (cut by the 160-character limit above); the response is the function without its docstring.

## The dataset card and versioning

`out/README.md` is a Hugging Face dataset card: YAML front matter (`license`, `language`, `task_categories`, `size_categories`, `pretty_name`, `configs` with `data_files` per split for both record types) and sections for summary, provenance, licensing, processing counts, splits, schema, limitations, contamination checks and a citation placeholder. All numbers come from `out/logs/*.json`. The card sets `license: other` with `license_name` and `license_link: LICENSE`, because the Hub's license list has no PSF-2.0 entry (checked 2026-11-25) and the files carry mixed licenses. Spec: https://huggingface.co/docs/hub/datasets-cards and https://huggingface.co/docs/hub/datasets-manual-configuration.

`08_push.sh` creates the repo, uploads `out/`, and tags `v0.1.0`; consumers pin it with `load_dataset(repo, "docstring_pairs", revision="v0.1.0")`. CLI names were checked against huggingface_hub 0.36.0 (`hf repo create`, `hf repo tag create`, `hf upload`) and the current CLI guide (which spells the group `hf repos`). The script was syntax-checked with `bash -n` and never pushed.

## Limits of this example

One language, one source, a few hundred files. The license step is a header regex plus a human-readable allow-list, not a legal review (the license reasoning is in `notes/research-build-dataset.md`). Publishing training examples is redistribution of code and carries the license duties of every file; publishing only a catalog of resource metadata (names, links, licenses) does not redistribute the code. The scrubber, the MinHash settings and the 13-gram check are teaching versions of tools that exist at larger scale.
