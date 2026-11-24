#!/usr/bin/env python3
"""Build the Renaissance Labs Code site into docs/.

  python3 tools/build.py

Inputs (all hand-checked data, nothing scraped at build time):
  data/taxonomy.json        stages, task axes, kinds
  data/resources/*.json     verified resource entries (see data/SCHEMA.md)
  data/snippets.json        verified command/config snippets
  data/recipes.json         rules for the recipe planner
  data/pages/*.html         long-form pages (guide, pitfalls, about) with {{r:id}} / {{snip:id}} / {{fig:grad}} tokens
Python 3.9, standard library only.
"""
import csv, hashlib, html, io, json, os, re, shutil, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
SITE = "https://code.renaissancelabs.eu"
e = html.escape
def J(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return json.load(f)

# ---------------------------------------------------------------- data
TAX = J("data/taxonomy.json")
STAGES = TAX["stages"]; STAGE_IDS = [s["id"] for s in STAGES]; STAGE = {s["id"]: s for s in STAGES}
TASKS = {t["id"]: t["label"] for t in TAX["tasks"]}
KINDS = {k["id"]: k["label"] for k in TAX["kinds"]}
RES = []
rdir = os.path.join(ROOT, "data/resources")
# Several research passes found the same resource. Merge by id or normalized URL: the first file in this priority order
# wins field by field, empty fields are filled from later copies, and list fields are unioned.
PRIORITY = ["rl-envs-sandboxes.json", "evals.json", "sft-reasoning-preference.json", "pretrain-and-tooling.json", "models-recipes.json"]
files = sorted((f for f in os.listdir(rdir) if f.endswith(".json")), key=lambda f: PRIORITY.index(f) if f in PRIORITY else 99)
_byid, _byurl = {}, {}
for fn in files:
    for r in J("data/resources/" + fn):
        r["_file"] = fn
        key = r["url"].rstrip("/").lower()
        base = _byid.get(r["id"]) or _byurl.get(key)
        if base is None:
            RES.append(r); _byid[r["id"]] = r; _byurl[key] = r; continue
        for k, v in r.items():
            if k.startswith("_"): continue
            if isinstance(v, list) and isinstance(base.get(k), list):
                for x in v:
                    if x not in base[k]: base[k].append(x)
            elif base.get(k) in (None, "", []) and v not in (None, "", []): base[k] = v
        base.setdefault("_merged", []).append(fn)
SNIPS = {s["id"]: s for s in J("data/snippets.json")} if os.path.exists(os.path.join(ROOT, "data/snippets.json")) else {}
RECIPES = J("data/recipes.json") if os.path.exists(os.path.join(ROOT, "data/recipes.json")) else None

def lic_class(s):
    t = (s or "").lower()
    if not t: return "unknown"
    if re.search(r"not applicable|arxiv preprint", t): return "na"
    if re.search(r"per-document|underlying files|blue oak", t): return "mixed"
    if re.search(r"non-production|open model license|openmdw|'inf'", t): return "gated"
    if re.search(r"per-file|mixed|varies|various|depends|per file|each", t): return "mixed"
    if re.search(r"\bnc\b|non-?commercial|-nc-|research only|research-only", t): return "noncommercial"
    if re.search(r"gated|openrail|custom|llama|terms|agreement|gemma|license-?agreement|proprietary|tongyi|qwen license|modified mit", t): return "gated"
    if re.search(r"-sa\b|gpl|odbl|share-?alike|mpl|epl|cc-by-sa", t): return "copyleft"
    if re.search(r"apache|\bmit\b|bsd|cc0|cc-by|odc-by|unlicense|isc|public domain|zlib|python", t): return "permissive"
    return "unknown"
LIC_LABEL = {"permissive": "Permissive", "copyleft": "Copyleft or share-alike", "noncommercial": "Non-commercial", "mixed": "Mixed or per-file", "gated": "Gated or custom terms", "na": "Not applicable (papers, services)", "unknown": "Unknown, read the source"}

seen = set()
for r in RES:
    assert r.get("id") and r["id"] not in seen, "duplicate or missing id: %r" % r.get("id"); seen.add(r["id"])
    for k in ("name", "kind", "url", "summary", "stages", "checked"): assert r.get(k), "%s missing %s" % (r["id"], k)
    assert r["kind"] in KINDS, "%s kind %s" % (r["id"], r["kind"])
    r["stages"] = sorted({("pretrain" if s == "midtrain" else s) for s in r["stages"]}, key=STAGE_IDS.index)
    r["tasks"] = [t for t in r.get("tasks") or [] if t in TASKS] if r["kind"] != "tool" else []   # tool entries carried generic task tags; tools are found by stage and kind
    r["languages"] = [x.lower() for x in r.get("languages") or []]
    r["lic_class"] = lic_class(r.get("license"))
    r["primary"] = ("tooling" if r["kind"] == "tool" and "tooling" in r["stages"] else "eval" if r["kind"] == "benchmark" and "eval" in r["stages"] else r["stages"][0] if r["stages"] else "tooling")
    for k in ("license", "size", "how_to_use", "caveats", "load_snippet", "released", "evidence", "difficulty"): r.setdefault(k, None)
    r.setdefault("extra_links", [])
RB = {r["id"]: r for r in RES}
LANGS = sorted({l for r in RES for l in r["languages"]})
CHECKED = max(r["checked"] for r in RES) if RES else str(date.today())

def short_lic(r):
    """Short license label for cards and previews: the exact text when it fits, else the license family (full text is on the resource page)."""
    t = (r["license"] or "").strip()
    if not t: return "license not stated"
    return t if len(t) <= 22 else {"permissive": "Permissive", "copyleft": "Copyleft", "noncommercial": "Non-commercial", "mixed": "Mixed licenses", "gated": "Gated or custom terms", "na": "n/a", "unknown": "See source"}[r["lic_class"]]
def short_size(r):
    t = (r["size"] or "").strip()
    return t if 0 < len(t) <= 24 else ""

def stage_count(s): return sum(1 for r in RES if s in r["stages"])
def fmt(n): return "{:,}".format(int(n))

# ---------------------------------------------------------------- code highlighting (light, language-agnostic)
KW = set("import from def class return for in if else elif while with as try except finally raise lambda None True False pip install run export docker git curl python python3 accelerate launch torchrun trl lm_eval evalplus inspect harbor pass yield assert not and or is".split())
HL = re.compile(r"(#[^\n]*)|(\"(?:[^\"\\\n]|\\.)*\"|'(?:[^'\\\n]|\\.)*')|(\b\d[\d_.e]*\b)|([A-Za-z_][A-Za-z_0-9]*)")
def hl(code, lang):
    out, pos = [], 0
    for m in HL.finditer(code):
        out.append(e(code[pos:m.start()]))
        if m.group(1): out.append('<span class="c">%s</span>' % e(m.group(0)))
        elif m.group(2): out.append('<span class="s">%s</span>' % e(m.group(0)))
        elif m.group(3): out.append('<span class="n">%s</span>' % e(m.group(0)))
        else:
            w = m.group(4); out.append('<span class="k">%s</span>' % w if w in KW else e(w))
        pos = m.end()
    out.append(e(code[pos:]))
    return "".join(out)

def codebox(code, lang="bash", label=None):
    return '<div class="codebox"><div class="lab"><span>%s</span><button class="copy" type="button">Copy</button></div><pre>%s</pre></div>' % (e(label or lang), hl(code.rstrip("\n"), lang))

def snippet_html(sid):
    s = SNIPS[sid]
    src = " ".join('<a href="%s">source</a>' % e(u) for u in s.get("source_urls", [])[:3])
    return codebox(s["code"], s.get("language", "bash"), s["title"]) + '<p class="snote"><b>Verified:</b> %s%s. %s %s</p>' % (
        e(s.get("verified_how", "")), (", version seen: " + e(str(s["tool_version_seen"]))) if s.get("tool_version_seen") else "", e(s.get("notes", "")), src)

# ---------------------------------------------------------------- page shell
VER = hashlib.md5(b"".join(open(p, "rb").read() for p in [os.path.join(OUT, "styles.css"), os.path.join(ROOT, "site_app.js"), os.path.join(ROOT, "site_recipe.js")] if os.path.exists(p))).hexdigest()[:8]
PAGES_OUT, SITEMAP = {}, []
NAV = [("/catalog/", "Catalog", "catalog"), ("/recipe/", "Recipe builder", "recipe"), ("/guide/", "Guide", "guide"), ("/pitfalls/", "Pitfalls", "pitfalls"), ("/about/", "About", "about")]

def shell(path, title, desc, body, current="", og=None, extra_head="", extra_foot=""):
    url = SITE + path
    img = "%s/assets/og/%s.jpg" % (SITE, og or "home")
    links = "".join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if k == current else "", t) for h, t, k in NAV)
    full = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:type" content="website">
<meta property="og:image" content="{img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{e(title)}"><meta property="og:site_name" content="Renaissance Labs Code">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{img}"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="theme-color" content="#121311">
<link rel="icon" href="/assets/favicon.png">
<link rel="stylesheet" href="/styles.css?v={VER}">
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
{extra_head}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="bar">
  <a class="brand" href="/"><img src="/assets/mark.png" alt=""><span>Renaissance Labs &middot; Code</span></a>
  <nav>{links}<a class="ext" href="https://math.renaissancelabs.eu">Math</a><a class="ext" href="https://practice.renaissancelabs.eu">Practice</a><a class="ext" href="https://renaissancelabs.eu">Renaissance Labs</a></nav>
  <button class="theme" id="theme" type="button" aria-label="Toggle dark mode"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
</header>
<main id="main">
{body}
</main>
<footer class="wrap foot">
  <a class="brand" href="https://renaissancelabs.eu"><img src="/assets/mark.png" alt="">Renaissance Labs</a>
  <div class="foot-links"><a href="/about/">About</a><a href="/data/resources.json">Data</a><a href="/data/resources.csv">CSV</a><a href="/llms.txt">llms.txt</a><a href="https://math.renaissancelabs.eu">Math</a><a href="https://practice.renaissancelabs.eu">Practice</a><a href="https://huggingface.co/RenaissanceLabsEU">Hugging Face</a></div>
</footer>
<script src="/app.js?v={VER}" defer></script>
{extra_foot}</body>
</html>
'''
    PAGES_OUT[path] = full
    SITEMAP.append(url)

def wrap(inner, cls=""): return '<div class="wrap %s">%s</div>' % (cls, inner)

# ---------------------------------------------------------------- shared pieces
def stage_pills(r): return "".join('<span class="pill st st-%s">%s</span>' % (s, e(STAGE[s]["short"])) for s in r["stages"])

def card(r):
    primary = r["primary"]
    lic = short_lic(r)
    wl = " warn" if r["lic_class"] in ("noncommercial", "gated", "unknown") else (" good" if r["lic_class"] == "permissive" else "")
    s = " ".join([r["name"], r["summary"], r["kind"], " ".join(r["languages"]), " ".join(r["tasks"]), " ".join(STAGE[x]["short"] for x in r["stages"]), r["license"] or ""]).lower()
    sizepill = '<span class="pill">%s</span>' % e(short_size(r)) if short_size(r) else ""
    return (f'<a class="rc st-{primary}" href="/r/{r["id"]}/" data-stage="{" ".join(r["stages"])}" data-kind="{r["kind"]}" data-lang="{" ".join(r["languages"])}" data-task="{" ".join(r["tasks"])}" data-lic="{r["lic_class"]}" data-s="{e(s)}">'
            f'<div class="top"><span class="k">{e(KINDS[r["kind"]])}</span><span>{e(r["released"] or "")}</span></div>'
            f'<h3>{e(r["name"])}</h3><p class="sum">{e(r["summary"])}</p>'
            f'<div class="facts">{stage_pills(r)}<span class="pill lic{wl}">{e(lic)}</span>{sizepill}</div></a>')

def opts(items, allv="All"):
    return '<option value="">%s</option>' % allv + "".join('<option value="%s">%s</option>' % (e(v), e(l)) for v, l in items)

def refs(text):
    """Expand {{r:id}}, {{snip:id}}, {{fig:grad}} tokens in long-form pages."""
    def rr(m):
        i = m.group(1); assert i in RB, "unknown resource in page: " + i
        return '<a href="/r/%s/">%s</a>' % (i, e(RB[i]["name"]))
    def sn(m):
        assert m.group(1) in SNIPS, "unknown snippet in page: " + m.group(1)
        return snippet_html(m.group(1))
    text = re.sub(r"\{\{r:([a-z0-9\-\.]+)\}\}", rr, text)
    text = re.sub(r"\{\{snip:([a-z0-9\-_\.]+)\}\}", sn, text)
    text = text.replace("{{fig:grad}}", GRAD_FIG)
    return text

GRAD_FIG = '''<figure class="fig" id="gradfig"><svg viewBox="0 0 640 230" role="img" aria-label="Chance that a group of rollouts gives a learning signal, by the model's pass rate on the task"><line x1="20" y1="190" x2="620" y2="190" stroke="var(--rule-strong)"/><g id="gradbars"></g></svg>
<div class="ctl"><label for="gradp">Model pass rate on a task</label><input id="gradp" type="range" min="0" max="1" step="0.05" value="0.5"><b id="gradv">50%</b></div>
<figcaption id="gradtxt"></figcaption><figcaption>Bars: the chance that a group of 8 rollouts for one task is mixed (some pass, some fail), assuming each rollout passes independently with the pass rate on the x-axis. Groups where every rollout gets the same reward have zero advantage under group-relative methods such as GRPO, so they teach nothing. This is why RL task sets are filtered to a middle band of difficulty. Computed as 1 - p^8 - (1-p)^8.</figcaption></figure>'''

# ---------------------------------------------------------------- pages
def page_home():
    heat = matrix_html()
    rail = "".join(f'<a class="node st-{s["id"]}" href="/stage/{s["id"]}/"><span class="n">{s["n"]}</span><h3>{e(s["title"].split(":")[0])}</h3><p>{e(s["tagline"])}</p><span class="ct"><b>{stage_count(s["id"])}</b> resources</span></a>' for s in STAGES)
    term = '''<div class="term"><div class="term-bar"><i></i><i></i><i></i><span>the loop</span></div><pre><span class="d"># the whole method, in five lines</span>
<span class="p">$</span> measure   <span class="d"># fixed eval, frozen settings</span>
<span class="p">$</span> clean     <span class="d"># dedup, decontaminate, license filter</span>
<span class="p">$</span> sft       <span class="d"># instructions + checked traces</span>
<span class="p">$</span> rl        <span class="d"># run the tests, reward passes</span>
<span class="p">$</span> measure   <span class="d"># same eval. Did it move?</span><span class="cur"></span></pre></div>'''
    npaper = sum(1 for r in RES if r["kind"] in ("paper", "recipe"))
    body = f'''<section class="hero"><div class="hero-in"><div>
<span class="eyebrow">Renaissance Labs &middot; Code</span>
<h1>Train a model that <em>actually</em> codes.</h1>
<p class="lede">A verified map of the datasets, environments, benchmarks and tools for training coding models, plus a recipe builder that turns your model size, compute and goal into an ordered plan. Every entry was checked against its source.</p>
<div class="cta-row"><a class="btn primary" href="/recipe/">Build a recipe</a><a class="btn" href="/guide/">Read the guide</a><a class="btn" href="/catalog/">Browse {len(RES)} resources</a></div>
<div class="stats"><div class="stat"><b>{len(RES)}</b><span>verified entries</span></div><div class="stat"><b>{sum(1 for r in RES if r["kind"] in ("dataset",))}</b><span>datasets</span></div><div class="stat"><b>{sum(1 for r in RES if r["kind"] in ("benchmark",))}</b><span>benchmarks</span></div><div class="stat"><b>{sum(1 for r in RES if r["kind"] in ("environment",))}</b><span>environments</span></div><div class="stat"><b>{len(SNIPS)}</b><span>checked snippets</span></div></div>
</div>{term}</div></section>
<div class="wrap"><section class="blk"><div class="sec-head"><div><span class="eyebrow">The pipeline</span><h2>Six stages, one loop</h2><p>Improving a coding model is a loop, not a ladder. Measure first, change one thing, measure again. Each stage has a page with the decisions, the pitfalls and the resources.</p></div></div>
<div class="rail">{rail}</div>
<p class="loopnote"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8M21 3v5h-5M21 12a9 9 0 0 1-15.5 6.2L3 16M3 21v-5h5"/></svg>After every stage, go back to Evaluation and re-measure with the same settings.</p></section>
<section class="blk"><div class="sec-head"><div><span class="eyebrow">Start where you are</span><h2>Three ways in</h2></div></div>
<div class="paths"><a class="path" href="/guide/"><span class="eyebrow">I have a model</span><h3>How to improve any model at coding</h3><p>The honest short version: measure, fix data, SFT, verifiable-reward RL, measure again.</p></a>
<a class="path" href="/recipe/"><span class="eyebrow">I have a budget</span><h3>Give me a plan</h3><p>Pick model size, compute, languages and goal. Get an ordered recipe with datasets, evals, verifiers and pitfalls.</p></a>
<a class="path" href="/catalog/"><span class="eyebrow">I need a thing</span><h3>Find a dataset, eval or tool</h3><p>Filter by stage, language, task, license and kind. Each entry lists caveats and when it was checked.</p></a></div></section>
<section class="blk"><div class="sec-head"><div><span class="eyebrow">Taxonomy</span><h2>What exists, and where the gaps are</h2><p>Resources by task type and stage. Click a cell to see them. Hatched cells are empty in this catalog, which tells you where you will have to build your own data or look harder.</p></div></div>{heat}
<p class="mnote">Counts are entries in this catalog (checked {e(CHECKED)}), not a census of the field.</p></section></div>'''
    shell("/", "Renaissance Labs Code: datasets, environments and tools for training coding models",
          "A verified taxonomy of code datasets, RL environments, benchmarks and tools, with a recipe builder and an honest guide to improving any model at coding.", body, og="home")

def matrix_html():
    cols = [s for s in STAGES]
    MK = ("dataset", "benchmark", "environment", "model")   # tools and papers carry generic task tags, so they are left out of the heat map
    cnt = {(t, s["id"]): sum(1 for r in RES if t in r["tasks"] and s["id"] in r["stages"]) for t in TASKS for s in cols}
    mx = max(cnt.values()) or 1
    head = "".join(f'<th class="st-{s["id"]}">{e(s["short"])}</th>' for s in cols)
    rows = ""
    for t, lab in TASKS.items():
        tds = ""
        for s in cols:
            n = cnt[(t, s["id"])]; w = 0 if n == 0 else int(14 + 56 * n / mx)
            tds += f'<td class="st-{s["id"]}{" z" if n == 0 else ""}"><a href="/catalog/#stage={s["id"]}&amp;task={t}" style="--w:{w}" title="{n} resources: {e(lab)} x {e(s["short"])}">{n}</a></td>'
        rows += f"<tr><th>{e(lab)}</th>{tds}</tr>"
    return f'<div class="matrix"><table><thead><tr><th></th>{head}</tr></thead><tbody>{rows}</tbody></table></div>'

def page_catalog():
    sorder = {s: i for i, s in enumerate(STAGE_IDS)}
    items = sorted(RES, key=lambda r: (sorder[r["primary"]], r["kind"], r["name"].lower()))
    chips = "".join(f'<button type="button" class="chipb st-{s["id"]}" data-stage="{s["id"]}" aria-pressed="false">{e(s["short"])}</button>' for s in STAGES)
    f_kind = opts([(k, v) for k, v in KINDS.items() if any(r["kind"] == k for r in RES)], "All kinds")
    f_lang = opts([(l, l) for l in LANGS], "All languages")
    f_task = opts([(t, TASKS[t]) for t in TASKS if any(t in r["tasks"] for r in RES)], "All tasks")
    f_lic = opts([(k, v) for k, v in LIC_LABEL.items()], "Any license")
    body = wrap(f'''<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / Catalog</div><span class="eyebrow">Catalog</span><h1>{len(RES)} resources, each checked at the source</h1>
<p class="lede">Filter by stage, kind, language, task and license family. The license family is derived from the license text and is a hint only: read the source before you train on anything.</p></div>
<div class="filters"><div class="row1"><div class="search"><input id="q" type="search" placeholder="Search names, tasks, languages..." aria-label="Search resources" autocomplete="off"></div>
<select class="f" id="f-kind" aria-label="Kind">{f_kind}</select><select class="f" id="f-lang" aria-label="Language">{f_lang}</select><select class="f" id="f-task" aria-label="Task">{f_task}</select><select class="f" id="f-lic" aria-label="License family">{f_lic}</select><span class="count" id="cnt"></span></div>
<div class="chips">{chips}<button type="button" class="chipb" id="reset">Reset</button></div></div>
<div class="grid" id="grid">{"".join(card(r) for r in items)}</div><p class="empty" id="none" hidden>Nothing matches. Loosen a filter, or this is a gap worth filling.</p></div>''')
    shell("/catalog/", "Catalog of code datasets, environments, benchmarks and tools", "Filterable, verified catalog of resources for training and evaluating coding models: license, size, caveats and date checked for each.", body, "catalog", og="catalog")

def kv(label, val): return "<dt>%s</dt><dd>%s</dd>" % (e(label), val) if val else ""

def page_resource(r):
    primary = r["primary"]
    related = sorted((x for x in RES if x["id"] != r["id"] and set(x["stages"]) & set(r["stages"])),
                     key=lambda x: (-(len(set(x["tasks"]) & set(r["tasks"])) * 2 + len(set(x["languages"]) & set(r["languages"]))), x["name"]))[:6]
    srclink = '<a href="%s">%s</a>' % (e(r["url"]), e(re.sub(r"^https?://(www[.])?", "", r["url"])[:48]))
    extra = "".join('<li><a href="%s">%s</a></li>' % (e(l["url"]), e(l["label"])) for l in r["extra_links"])
    snip = codebox(r["load_snippet"], "python" if "import" in r["load_snippet"] else "bash", "load") if r["load_snippet"] else ""
    lic_note = "" if r["lic_class"] in ("permissive", "na") else '<div class="callout warn"><b>License</b>This entry is not plainly permissive (family: %s). Read the license on the source page before using it for training or for a product.</div>' % e(LIC_LABEL[r["lic_class"]].lower())
    body = wrap(f'''<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / <a href="/catalog/">Catalog</a> / <a href="/stage/{primary}/">{e(STAGE[primary]["short"])}</a></div>
<span class="eyebrow">{e(KINDS[r["kind"]])}{(" &middot; " + e(r["released"])) if r["released"] else ""}</span><h1>{e(r["name"])}</h1><p class="lede">{e(r["summary"])}</p></div>
<div class="layout"><div class="prose">
{('<h2>How to use it</h2><p>%s</p>' % e(r["how_to_use"])) if r["how_to_use"] else ""}
{('<h2>Caveats</h2><p>%s</p>' % e(r["caveats"])) if r["caveats"] else ""}
{lic_note}{snip}
{('<h2>Related</h2><ul>%s</ul>' % "".join('<li><a href="/r/%s/">%s</a>: %s</li>' % (x["id"], e(x["name"]), e(x["summary"][:110].rsplit(" ", 1)[0] + "...")) for x in related)) if related else ""}
</div><aside class="aside"><div class="panel"><h3>At a glance</h3><dl>
{kv("Source", srclink)}
{kv("License", e(r["license"] or ""))}{kv("Size", e(r["size"] or ""))}
{kv("Stage", " ".join('<a class="pill st st-%s" href="/stage/%s/">%s</a>' % (s, s, e(STAGE[s]["short"])) for s in r["stages"]))}
{kv("Languages", e(", ".join(r["languages"])))}{kv("Tasks", e(", ".join(TASKS[t] for t in r["tasks"])))}{kv("Difficulty", e(r["difficulty"] or ""))}
{kv("Checked", e(r["checked"]))}</dl></div>
{('<div class="panel"><h3>More links</h3><ul>%s</ul></div>' % extra) if extra else ""}
{('<div class="panel"><h3>Evidence</h3><p class="mono">%s</p></div>' % e(r["evidence"])) if r["evidence"] else ""}</aside></div></div>''')
    shell("/r/%s/" % r["id"], "%s: %s | Renaissance Labs Code" % (r["name"], KINDS[r["kind"]]), r["summary"][:190], body, "catalog", og="r-" + r["id"])

def page_stage(s):
    items = sorted((r for r in RES if s["id"] in r["stages"]), key=lambda r: (r["kind"], r["name"].lower()))
    byk = {}
    for r in items: byk.setdefault(r["kind"], []).append(r)
    sections = "".join(f'<h2 style="margin:1.6em 0 .6em">{e(KINDS[k])}s <small class="mono" style="color:var(--ink-faint)">{len(v)}</small></h2><div class="grid">{"".join(card(r) for r in v)}</div>' for k, v in byk.items())
    li = lambda xs: "".join("<li>%s</li>" % e(x) for x in xs)
    idx = STAGE_IDS.index(s["id"]); prev_ = STAGES[idx - 1] if idx else None; next_ = STAGES[idx + 1] if idx + 1 < len(STAGES) else None
    nav = '<div class="cta-row">%s%s</div>' % ('<a class="btn" href="/stage/%s/">&larr; %s</a>' % (prev_["id"], e(prev_["short"])) if prev_ else "", '<a class="btn" href="/stage/%s/">%s &rarr;</a>' % (next_["id"], e(next_["short"])) if next_ else "")
    body = wrap(f'''<div class="page st-{s["id"]}"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / Stage {s["n"]}</div><span class="eyebrow" style="color:var(--hue)">Stage {s["n"]}</span><h1>{e(s["title"])}</h1><p class="lede">{e(s["tagline"])}</p></div>
<div class="prose"><h2>Who needs this</h2><p>{e(s["who"])}</p><h2>Decisions you will make</h2><ul>{li(s["decide"])}</ul><h2>Pitfalls</h2><ul>{li(s["pitfalls"])}</ul></div>
{sections}<div style="margin-top:34px">{nav}</div></div>''')
    shell("/stage/%s/" % s["id"], "%s | Renaissance Labs Code" % s["title"], s["tagline"] + " " + str(len(items)) + " verified resources.", body, "", og="stage-" + s["id"])

def load_page(name):
    p = os.path.join(ROOT, "data/pages", name + ".html")
    return refs(open(p, encoding="utf-8").read())

def page_long(name, path, title, desc, eyebrow, h1, lede, current, og):
    body = wrap(f'<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / {e(eyebrow)}</div><span class="eyebrow">{e(eyebrow)}</span><h1>{h1}</h1><p class="lede">{lede}</p></div><div class="prose">{load_page(name)}</div></div>')
    shell(path, title, desc, body, current, og=og)

def page_recipe():
    if RECIPES is None: return
    slim = {r["id"]: {k: r[k] for k in ("name", "kind", "url", "license", "size", "stages", "languages", "tasks", "caveats", "lic_class")} for r in RES}
    for k, v in slim.items(): v["summary"] = RB[k]["summary"]
    data = {"resources": slim, "recipes": RECIPES, "snippets": {k: {"title": v["title"], "language": v.get("language", "bash"), "code": v["code"], "notes": v.get("notes", ""), "verified_how": v.get("verified_how", "")} for k, v in SNIPS.items()},
            "stages": {s["id"]: {"title": s["title"], "short": s["short"], "n": s["n"]} for s in STAGES}, "lic": LIC_LABEL}
    inp = RECIPES["inputs"]
    def group(key, label, kind="radio", hint=""):
        g = inp[key]; t = "checkbox" if kind == "checkbox" else "radio"
        o = "".join(f'<label class="opt"><input type="{t}" name="{key}" value="{e(v["id"])}"{" checked" if v.get("default") else ""}><span>{e(v["label"])}</span></label>' for v in g["options"])
        return f'<div class="fld"><span class="lab">{e(label)}</span><div class="opts">{o}</div>{("<p class=hint>%s</p>" % e(hint)) if hint else ""}</div>'
    form = (group("goal", "Goal") + group("start", "Starting point") + group("size", "Model size", hint="Parameters of the model you will train.") + group("budget", "Compute budget") +
            group("languages", "Languages", "checkbox", "Pick all you care about. Python-only is the best-supported case.") + group("data", "Data you already have", "checkbox"))
    body = wrap(f'''<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / Recipe builder</div><span class="eyebrow">Recipe builder</span><h1>Tell us what you have. Get an ordered plan.</h1>
<p class="lede">Rules written by hand from the catalog, not generated on the fly. It picks stages, datasets, evals and verifiers that fit your size, budget and goal, says why, and flags the pitfalls. It is a starting point, not a guarantee: run the measure step first and let your numbers decide.</p></div>
<div class="planner"><form class="form" id="form" onsubmit="return false">{form}</form><div class="out" id="out" aria-live="polite"></div></div></div>''')
    shell("/recipe/", "Recipe builder for training a coding model | Renaissance Labs Code", "Pick model size, compute, languages and goal. Get an ordered, honest recipe with datasets, evals, verifiers and pitfalls from a verified catalog.", body, "recipe", og="recipe",
          extra_foot='<script type="application/json" id="rdata">%s</script><script src="/recipe.js?v=%s" defer></script>' % (json.dumps(data).replace("</", "<\\/"), VER))

# ---------------------------------------------------------------- exports and files
def exports():
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    clean = [{k: v for k, v in r.items() if not k.startswith("_")} for r in RES]
    json.dump({"generated": CHECKED, "site": SITE, "count": len(clean), "resources": clean}, open(os.path.join(OUT, "data/resources.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump(TAX, open(os.path.join(OUT, "data/taxonomy.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump(list(SNIPS.values()), open(os.path.join(OUT, "data/snippets.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if RECIPES: json.dump(RECIPES, open(os.path.join(OUT, "data/recipes.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    buf = io.StringIO(); w = csv.writer(buf)
    cols = ["id", "name", "kind", "url", "license", "license_family", "size", "stages", "languages", "tasks", "difficulty", "released", "checked", "summary", "caveats"]
    w.writerow(cols)
    for r in clean:
        w.writerow([r["id"], r["name"], r["kind"], r["url"], r["license"] or "", r["lic_class"], r["size"] or "", ";".join(r["stages"]), ";".join(r["languages"]), ";".join(r["tasks"]), r["difficulty"] or "", r["released"] or "", r["checked"], r["summary"], r["caveats"] or ""])
    open(os.path.join(OUT, "data/resources.csv"), "w", encoding="utf-8", newline="").write(buf.getvalue())

def llms():
    L = ["# Renaissance Labs Code", "", "> A verified taxonomy of datasets, RL environments, benchmarks and tools for training coding models, with a recipe builder and an honest guide. Every entry was checked against its primary source on the date shown. Machine-readable data: %s/data/resources.json" % SITE, "",
         "## Pages", "- [Catalog](%s/catalog/): all %d resources, filterable" % (SITE, len(RES)), "- [Recipe builder](%s/recipe/): ordered plan from model size, budget, languages and goal" % SITE, "- [Guide: how to improve any model at coding](%s/guide/)" % SITE, "- [Pitfalls](%s/pitfalls/)" % SITE, "- [About and method](%s/about/)" % SITE, "", "## Stages"]
    for s in STAGES: L.append("- [%s](%s/stage/%s/): %s (%d resources)" % (s["title"], SITE, s["id"], s["tagline"], stage_count(s["id"])))
    L += ["", "## Data", "- [resources.json](%s/data/resources.json)" % SITE, "- [resources.csv](%s/data/resources.csv)" % SITE, "- [taxonomy.json](%s/data/taxonomy.json)" % SITE, "- [snippets.json](%s/data/snippets.json)" % SITE, "", "## Resources"]
    for s in STAGES:
        L += ["", "### " + s["title"]]
        for r in sorted((r for r in RES if r["primary"] == s["id"]), key=lambda r: r["name"].lower()):
            L.append("- [%s](%s/r/%s/): %s [%s; license: %s]" % (r["name"], SITE, r["id"], r["summary"], r["kind"], r["license"] or "not stated"))
    open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")

def write_all():
    for p, h in PAGES_OUT.items():
        d = os.path.join(OUT, p.strip("/")); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(h)
    shutil.copy(os.path.join(ROOT, "site_app.js"), os.path.join(OUT, "app.js"))
    if os.path.exists(os.path.join(ROOT, "site_recipe.js")): shutil.copy(os.path.join(ROOT, "site_recipe.js"), os.path.join(OUT, "recipe.js"))
    open(os.path.join(OUT, "CNAME"), "w").write("code.renaissancelabs.eu\n")
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE)
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    sm = "".join("<url><loc>%s</loc><lastmod>%s</lastmod></url>" % (u, CHECKED) for u in SITEMAP)
    open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>\n' % sm)
    nf = shell_404()
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(nf)

def shell_404():
    saved = dict(PAGES_OUT), list(SITEMAP)
    shell("/404/", "Not found | Renaissance Labs Code", "Page not found.", wrap('<div class="page"><div class="page-head"><span class="eyebrow">404</span><h1>That page is not in the catalog.</h1><p class="lede"><a href="/catalog/" style="color:var(--accent)">Browse the catalog</a> or <a href="/" style="color:var(--accent)">go home</a>.</p></div></div>'))
    h = PAGES_OUT.pop("/404/"); SITEMAP.pop(); return h

def main():
    page_home(); page_catalog()
    for s in STAGES: page_stage(s)
    for r in RES: page_resource(r)
    page_recipe()
    for name, path, title, desc, eb, h1, lede, cur in LONG:
        if os.path.exists(os.path.join(ROOT, "data/pages", name + ".html")): page_long(name, path, title, desc, eb, h1, lede, cur, name)
    exports(); llms(); write_all()
    print("built %d pages, %d resources, %d snippets" % (len(PAGES_OUT), len(RES), len(SNIPS)))

LONG = [
    ("guide", "/guide/", "How to improve any model at coding: a guide | Renaissance Labs Code", "Measure first, fix data, SFT, then verifiable-reward RL, then re-measure. The honest short version, with caveats.", "Guide", "How to improve <em>any</em> model at coding", "The short version: measure, fix the data, teach the format, reward what passes, measure again.", "guide"),
    ("pitfalls", "/pitfalls/", "Pitfalls when training coding models | Renaissance Labs Code", "Contamination, reward hacking, weak tests, license traps and unsafe code execution: what goes wrong and how to avoid it.", "Pitfalls", "What goes wrong, and how to <em>see</em> it coming", "Most failed runs fail for the same few reasons.", "pitfalls"),
    ("about", "/about/", "About and method | Renaissance Labs Code", "How this catalog was built and verified, what it does not cover, and how to contribute a correction.", "About", "About this <em>catalog</em>", "How entries were verified, what is missing, and how to correct us.", "about"),
]

if __name__ == "__main__":
    main()
