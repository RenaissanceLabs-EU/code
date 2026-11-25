# What was verified, and what was not (2026-11-25)

## The maps
- **Languages (44):** year, designers, influences, runtime model and the "built with it" examples were read from official sites, specifications, designers' own pages and repository statistics on the date shown; each language page lists its sources. Sample programs: 13 ran on a real toolchain (see each page's "Run and checked" line); the rest were written against official documentation and are marked "Not run here". Details and gaps: `notes/research-languages-a.md`, `notes/research-languages-b.md`.
- **Landmarks and open problems (19 pages):** every entry links to its source; bibliographic facts were checked by DOI. Corrections made to our own candidate list are recorded in `notes/research-landmarks-stack.md` and `notes/research-landmarks-program.md`. Several primary sources were blocked to our fetcher (ACM, IEEE, Nature, nobelprize.org); those entries lean on a second source, and the notes say which.
- **Code in the world:** 17 systems, 10 failures, 9 entries on why software is never finished, each fact with a link and a date. Widely repeated numbers that could not be traced to a readable primary source are not used (the list is in `data/world-unverified.json`, not shown on the site). Details: `notes/research-world.md`.
- **Prose:** all explanatory text was fact-checked adversarially against sources and by running code (`notes/factcheck-prose.md`): 6 errors and about 50 missing qualifiers were found and fixed. The machine code, bytecode and Lean proof shown were produced by Apple clang 17 (arm64), Python 3.9 and Lean 4.36 on the day.
- **Live figures (23):** every figure was loaded and exercised in headless Chrome (`node tools/fig_check.mjs`). They run on `site_lang.js`, a real lexer, parser, type checker, compiler and stack machine (tested in Node on correct programs and on error cases).

## Part two (how to train language models for code)
- **Pages:** capability, data, evaluation, how code models are trained, and the dataset build were fact-checked against sources and by running code (`notes/factcheck-how.md`, `notes/factcheck-part2.md`); every wrong statement and missing qualifier was fixed.
- **Datasets directory (51):** contents, format, size, license, limits, downloads and likes (Hugging Face and GitHub APIs, 2026-11-25) and which open models' reports use each one (`notes/research-starter-datasets.md`).
- **Tools directory (54):** versions and dates from PyPI and GitHub releases; install commands from each project's docs; two setups checked against dependency floors, not installed (`notes/research-tools-directory.md`). The local system Python 3.9 is too old for current TRL; the setups say Python 3.11 or newer.
- **Dataset pipeline (`examples/build-dataset`):** built and run twice end to end (identical SHA-256 for all outputs), 15 unit tests pass, runs in about 20 seconds in under 50 MB of memory. Pushing to the Hub was not tested.
- **First training run (`examples/first-run`):** commands and settings checked against source and docs; scripts pass syntax checks and the filter was run on 500 real rows. Nothing was trained or evaluated, so all memory, time and outcome figures are labeled estimates with their basis (`notes/research-first-run.md`).
- **Reading list (70)** and **model recipes (18):** read from arXiv abstracts and model reports (`notes/research-reading.md`, `notes/research-model-recipes.md`).

## The catalog (Train)
- **Entries (384):** the original 319, read from the Hugging Face API, cards, the GitHub API, arXiv metadata or official docs, plus 65 added for the lower levels of the stack (hardware, machine code, compilers, types, execution, change, infrastructure, security, applications, learned programs), each with an `evidence` field. 
- **Language coverage:** `data/coverage.json` lists, for 131 datasets, benchmarks, environments and models, the programming languages their own documentation names. 41 resources could not be resolved (silent or gated cards) and count for no language. 21 single-language tags were copied from the catalog without the language being named in the fetched text (`notes/research-coverage.md`).
- **Filing under forms and levels:** by rules in `build.py` plus hand corrections; read through by eye, but a judgment call, not a measurement.
- **Links:** 647 external URLs checked; 3 answered 403 to scripts (two ACM DOIs and an OpenReview PDF) and open in a browser.
- **Pages:** all 463 load in headless Chrome at 1280 and 390 px with no console errors, no failed requests, one h1 each and no horizontal overflow; internal links all resolve.

## Not verified / limits
- Gated corpora (The Stack, StarCoderData, Nemotron code sets): cards unreadable without access.
- Nineteen of the 44 sample programs and several language years or influences rest on weaker evidence than the rest; each language page and `notes/research-languages-*.md` say which.
- Some sentences on the maps rest on one source; the fact-check lists the ones it could not confirm.
- The license-family filter is a regex over license text, a hint and not legal advice.
- Planner rules are editorial judgment and have not been tested by training runs.
- No leaderboard scores are published; scores move.
- Deployment: the previous version of the site is live; this version has not been pushed.
