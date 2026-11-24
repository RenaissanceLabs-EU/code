# What was verified, and what was not (2026-11-24)

## Verified
- **Entries (319):** licenses, sizes, activity and gating were read from the Hugging Face API, dataset and model cards, the GitHub API, arXiv metadata, or official docs by five research passes; each entry's `evidence` field names the source. Unconfirmed fields are null or flagged in `caveats` rather than guessed.
- **Independent spot check:** 14 random entries re-checked against the live HF and GitHub APIs after the build: no license mismatches (repos that had moved were followed through redirects).
- **Links:** `tools/check_links.py` requested all 488 external URLs in the data and pages. First pass: 16 Hugging Face model pages answered 429 (rate limit); all 16 returned 200 through the HF API on retry. Final: 0 bad (`notes/link-report.json`). Internal links: all resolve (`page_check.mjs`).
- **Pages:** all 331 pages load in headless Chrome at 1280 px and 390 px (mobile emulation) with no console errors, no failed requests, one h1 each, and no horizontal overflow. Catalog hash filters, catalog search and every recipe-builder option toggle were exercised (no empty plans).
- **Snippets (17):** matched to current official docs or source; 4 run locally (hardened Docker sandbox, pass@k estimator, subprocess reward with pass/fail/timeout/syntax-error, datasets streaming). Each page states how and the version seen.
- **Social previews:** one 1200x630 image per page (331), generated from the data; home, SFT stage and a resource image reviewed by eye.
- **Interactive figure:** the pass-rate figure is computed as 1 - p^8 - (1-p)^8 for 8 rollouts; formula checked by hand.

## Not verified / limits
- Gated corpora (The Stack v1/v2, StarCoderData, Nemotron code sets): cards unreadable without access, so some sizes and the exact terms are null or taken from the Stack v3 table or NVIDIA's page.
- Ten SFT candidates (e.g. BIRD, CodeReviewer) were dropped because their HF ids returned 401; check on their own sites. No code-review benchmark and no EditEval entries.
- Some claims came from search summaries and were not read in full (noted in `notes/research-rl.md`: MiMo-V2-Flash, FrogNano). They are not used in site copy.
- Most snippets were not executed (they need Python 3.10+, GPUs, API keys or large images; local Python is 3.9). Inspect's `vllm/` provider line and the LLaMA-Factory custom-dataset entry are unconfirmed (`notes/snippets-unverified.md`). Subprocess reward rlimits were not exercised on macOS.
- The license-family filter is a regex over license text: a hint, not legal advice.
- Planner rules are editorial judgment from the cited evidence; they have not been tested by training runs.
- No scores are published except where an entry's caveats cite a primary source and date; leaderboards move.
- Deployment: nothing has been pushed, created on GitHub, or changed in DNS.
