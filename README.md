# Renaissance Labs Code

Source for https://code.renaissancelabs.eu: a map of what code is, from the program to the transistor, with working resources attached.

- **What a program is** (`data/program.txt`): eight forms of one program (text, tokens, tree, types, execution, tests, proof, change).
- **The stack** (`data/stack.txt`): nine levels, transistors to learned programs.
- **Languages** (`data/languages-*.json`): 44 verified language entries, each with the same sample program.
- **Code in the world** (`data/world.json`): sourced facts, failures, and why software is never finished.
- **Code and intelligence** (`data/pages/intelligence.html`): computation, its limits, learned programs.
- **Train**: the verified catalog of datasets, environments, benchmarks and tools for training coding models (`data/resources/*.json`), a recipe builder and a guide. Every entry is filed under a form of a program, a level of the stack and a language.

```
docs/            the built site (static HTML, served by GitHub Pages from main:/docs)
data/            program.txt, stack.txt, languages-*.json, landmarks-*.json, world.json, coverage.json (languages per catalog entry),
                 taxonomy.json, resources/*.json (schema in SCHEMA.md), snippets.json, recipes.json, pages/*.html
tools/           build.py (site), make_og.py + render_og.mjs (social previews), page_check.mjs and fig_check.mjs (headless Chrome),
                 check_links.py, shot.mjs (screenshots)
notes/           research notes per topic, factcheck-prose.md, link-report.json, what could not be verified
site_lang.js     Mini: a tiny language (lexer, parser, type checker, compiler, stack machine) that the figures run on
site_figs.js     the 21 live figures;  site_app.js, site_recipe.js   catalog filters and recipe planner
```

## Commands

```bash
python3 tools/build.py                 # rebuild docs/ (Python 3.9, standard library only)
python3 tools/make_og.py               # social previews, one per page (needs Chrome + tools/node)
python3 tools/check_links.py           # every external link in the data (HF links are checked via the HF API; 429s retried)
node tools/page_check.mjs              # every page, desktop and mobile, console errors, overflow, internal links, filters, planner
node tools/fig_check.mjs               # every live figure: loads, interacts, checks the text it produces
```

First time: `cd tools/node && npm install` (puppeteer-core; uses your installed Chrome).

## How the data works

Every entry in `data/resources/*.json` follows `data/SCHEMA.md` and carries the date it was checked and the evidence used. Several research passes found the same resource, so `build.py` merges entries by id or URL (priority order set in `PRIORITY`). The license family used by the catalog filter is derived from the license text and is a hint only. To add or fix an entry: edit the JSON with a primary source, rebuild, run the checks.

## How the maps are written

`program.txt` and `stack.txt` hold one page per section, separated by `@@@`, with fields introduced by `@key` (question, lede, example, fig, notice, ideas, models, ...). Catalog entries are filed under forms and levels by the rules in `file_resource()` in `build.py`, with `UNFILE` for hand corrections. A language counts as covered by a resource only when `coverage.json` records that the resource's own documentation lists it.

## Planner

`data/recipes.json` holds the rules (inputs, checks, ordered steps with `when` conditions, picks with a reason, snippets, pitfalls). `site_recipe.js` only matches conditions and renders. The build fails if a page references an unknown resource or snippet.

Code MIT, data and content CC BY 4.0. Linked resources keep their own licenses.
