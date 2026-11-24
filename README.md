# Renaissance Labs Code

Source for https://code.renaissancelabs.eu: a verified taxonomy of datasets, RL environments, benchmarks, models, papers and tools for training coding models, a recipe builder that turns model size, compute budget, languages and goal into an ordered plan, and an honest guide to improving any model at coding.

```
docs/            the built site (static HTML, served by GitHub Pages from main:/docs)
data/            taxonomy.json (stages, task axes), resources/*.json (verified entries, schema in SCHEMA.md),
                 snippets.json (checked commands), recipes.json (planner rules), pages/*.html (guide, pitfalls, about)
tools/           build.py (site), make_og.py + render_og.mjs (social previews), page_check.mjs (headless Chrome), check_links.py
notes/           research notes per topic, link-report.json, what could not be verified
site_app.js, site_recipe.js   browser code (copied into docs/ by the build)
```

## Commands

```bash
python3 tools/build.py                 # rebuild docs/ (Python 3.9, standard library only)
python3 tools/make_og.py               # social previews, one per page (needs Chrome + tools/node)
python3 tools/check_links.py           # every external link in the data (HF links are checked via the HF API; 429s retried)
node tools/page_check.mjs              # every page, desktop and mobile, console errors, overflow, internal links, filters, planner
```

First time: `cd tools/node && npm install` (puppeteer-core; uses your installed Chrome).

## How the data works

Every entry in `data/resources/*.json` follows `data/SCHEMA.md` and carries the date it was checked and the evidence used. Several research passes found the same resource, so `build.py` merges entries by id or URL (priority order set in `PRIORITY`). The license family used by the catalog filter is derived from the license text and is a hint only. To add or fix an entry: edit the JSON with a primary source, rebuild, run the checks.

## Planner

`data/recipes.json` holds the rules (inputs, checks, ordered steps with `when` conditions, picks with a reason, snippets, pitfalls). `site_recipe.js` only matches conditions and renders. The build fails if a page references an unknown resource or snippet.

Code MIT, data and content CC BY 4.0. Linked resources keep their own licenses.
