#!/usr/bin/env python3
"""Build the Renaissance Labs Code site into docs/.

  python3 tools/build.py

Inputs (all hand-checked data, nothing scraped at build time):
  data/program.txt          the eight forms of a program (text ... change), one page each
  data/stack.txt            the nine levels of the stack (transistors ... learned programs)
  data/languages-*.json     verified language entries;  data/coverage.json  languages per catalog entry
  data/landmarks.json       dated landmarks and open problems per page;  data/world.json  code in the world
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
VER = hashlib.md5(b"".join(open(p, "rb").read() for p in [os.path.join(OUT, "styles.css"), os.path.join(ROOT, "site_app.js"), os.path.join(ROOT, "site_recipe.js"), os.path.join(ROOT, "site_lang.js"), os.path.join(ROOT, "site_figs.js")] if os.path.exists(p))).hexdigest()[:8]
PAGES_OUT, SITEMAP = {}, []
NAV = [("/program/", "Program", "program"), ("/stack/", "Stack", "stack"), ("/languages/", "Languages", "languages"), ("/world/", "World", "world"), ("/intelligence/", "Intelligence", "intelligence"), ("/train/", "Train", "train"), ("/about/", "About", "about")]
TRAIN_KEYS = ("catalog", "recipe", "guide", "pitfalls")

def shell(path, title, desc, body, current="", og=None, extra_head="", extra_foot=""):
    url = SITE + path
    img = "%s/assets/og/%s.jpg" % (SITE, og or "home")
    links = "".join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if (k == current or (k == "train" and current in TRAIN_KEYS)) else "", t) for h, t, k in NAV)
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
  <div class="foot-links"><a href="/catalog/">Catalog</a><a href="/recipe/">Recipe builder</a><a href="/guide/">Guide</a><a href="/about/">About</a><a href="/data/resources.json">Data</a><a href="/data/resources.csv">CSV</a><a href="/llms.txt">llms.txt</a><a href="https://math.renaissancelabs.eu">Math</a><a href="https://practice.renaissancelabs.eu">Practice</a><a href="https://huggingface.co/RenaissanceLabsEU">Hugging Face</a></div>
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
    s = " ".join([r["name"], r["summary"], r["kind"], " ".join(r["languages"]), " ".join(r["langs"]), " ".join(r["tasks"]), " ".join(STAGE[x]["short"] for x in r["stages"]), r["license"] or ""]).lower()
    sizepill = '<span class="pill">%s</span>' % e(short_size(r)) if short_size(r) else ""
    return (f'<a class="rc st-{primary}" href="/r/{r["id"]}/" data-stage="{" ".join(r["stages"])}" data-kind="{r["kind"]}" data-lang="{" ".join(r["langs"])}" data-task="{" ".join(r["tasks"])}" data-lic="{r["lic_class"]}" data-layer="{" ".join(r["layers"])}" data-level="{" ".join(r["levels"])}" data-s="{e(s)}">' 
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

# ---------------------------------------------------------------- the maps: content files, languages, coverage, filing
def load_sections(path):
    """Parse data/program.txt and data/stack.txt: pages separated by a line '@@@', fields introduced by '@key'."""
    full = os.path.join(ROOT, path)
    if not os.path.exists(full): return []
    out = []
    for chunk in open(full, encoding="utf-8").read().split("\n@@@\n"):
        d, key, buf, fence = {}, None, [], False
        for line in chunk.split("\n"):
            if line.startswith("```"): fence = not fence
            m = None if fence else re.match(r"@([a-z]+)(?: (.*))?$", line)
            if m:
                if key: d[key] = "\n".join(buf).strip("\n")
                key, buf = m.group(1), [m.group(2) or ""]
            else: buf.append(line)
        if key: d[key] = "\n".join(buf).strip("\n")
        if d.get("id"): out.append(d)
    return out

def inline(t):
    """Escape, then `code`, [text](url) and *emphasis*."""
    stash = []
    def keep(m): stash.append("<code>%s</code>" % e(m.group(1))); return "\x00%d\x00" % (len(stash) - 1)
    t = re.sub(r"`([^`]+)`", keep, t)
    t = e(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), t)
    t = re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", t)
    return re.sub("\x00(\\d+)\x00", lambda m: stash[int(m.group(1))], t)

def plainbox(code, label):
    return '<div class="codebox"><div class="lab"><span>%s</span><button class="copy" type="button">Copy</button></div><pre>%s</pre></div>' % (e(label), e(code.rstrip("\n")))

FENCE_LABEL = {"bytes": "bytes, in hexadecimal", "trace": "trace", "mini": "the small language used on this site", "lean": "Lean 4", "asm": "ARM64 machine code and assembly", "bytecode": "Python bytecode", "syscalls": "system calls", "binary": "binary", "sql": "SQL"}
def rich(text):
    """Blocks: ``` fences, '- ' lists, paragraphs."""
    out, parts = [], re.split(r"```([a-z]*)\n(.*?)\n```", text or "", flags=re.S)
    for i in range(0, len(parts), 3):
        for block in re.split(r"\n\s*\n", parts[i].strip()):
            lines = [l for l in block.split("\n") if l.strip()]
            if not lines: continue
            if all(l.startswith("- ") for l in lines): out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % inline(l[2:]) for l in lines))
            else: out.append("<p>%s</p>" % inline(" ".join(lines)))
        if i + 2 < len(parts): out.append(plainbox(parts[i + 2], FENCE_LABEL.get(parts[i + 1], parts[i + 1] or "code")))
    return "".join(out)

def first_para(text): return re.split(r"\n\s*\n", (text or "").strip())[0].replace("\n", " ")
def strip_md(t): return re.sub(r"[`*]", "", re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t))

PROGRAM = load_sections("data/program.txt")
STACK = load_sections("data/stack.txt")          # written top of the stack first
PROG = {d["id"]: d for d in PROGRAM}; LEVEL = {d["id"]: d for d in STACK}
LAYER_IDS = [d["id"] for d in PROGRAM]; LEVEL_IDS = [d["id"] for d in STACK]
def opt_json(p, default):
    return J(p) if os.path.exists(os.path.join(ROOT, p)) else default
LANDMARKS = {**opt_json("data/landmarks-stack.json", {}), **opt_json("data/landmarks-program.json", {})}
WORLD = opt_json("data/world.json", {"systems": [], "failures": [], "living": []})
COVER = opt_json("data/coverage.json", {"resources": {}})
LANGLIST = opt_json("data/languages-a.json", []) + opt_json("data/languages-b.json", [])
LANG = {l["id"]: l for l in LANGLIST}
FAMILIES = [
    ("hardware", "Hardware description", "Languages that describe circuits. The text is not a list of steps: it describes wires and gates that all act at once."),
    ("machine", "Machine level", "The processor's own instructions, or a thin readable layer over them."),
    ("systems", "Systems", "Languages that compile straight to machine code and leave memory in the programmer's hands. Operating systems, browsers and databases are written in them."),
    ("managed", "Application", "Compiled languages for building large applications, usually on a runtime that looks after memory. The workhorses of business software and mobile apps."),
    ("scripting", "Scripting", "Dynamically typed languages made for writing programs quickly. They trade machine speed for programmer speed, and they glue most systems together."),
    ("functional", "Functional", "Languages built around functions and values that do not change. Ideas now found everywhere, such as garbage collection and type inference, started here."),
    ("numeric", "Numeric and scientific", "Languages built for mathematics on arrays of numbers: science, statistics, engineering and simulation."),
    ("query-logic", "Query and logic", "Languages in which you state what is true or what you want, and the system searches for the answer."),
    ("shell", "Shell", "Languages for commanding an operating system: starting programs and connecting them to each other."),
    ("markup-config", "Markup and configuration", "Languages that describe a document or a desired state instead of a computation."),
    ("proof", "Proof", "Languages in which a program can carry a machine-checked proof that it is correct, and in which mathematics itself can be written."),
    ("contract", "Smart contract", "Languages for programs that run on a blockchain, where code is public, every step has a price, and a deployed program cannot be patched."),
]
FAM = {f[0]: f for f in FAMILIES}
LANG["cpp"]["level"] = "os"            # editorial placement: C++ is filed with the other systems languages
LANG["perl"]["influenced_by"] = [("sh" if x == "bash" else x) for x in LANG["perl"].get("influenced_by") or []]   # Perl predates Bash
for l in LANGLIST:
    assert l["family"] in FAM, "%s family %s" % (l["id"], l["family"])
    l["levels"] = [x for x in (l.get("levels") or [l["level"]]) if x in LEVEL] or ["languages"]
    if l["level"] not in LEVEL: l["level"] = l["levels"][0]
    l["influenced_by"] = l.get("influenced_by") or []
for l in LANGLIST: l["influenced"] = [m["id"] for m in LANGLIST if l["id"] in m["influenced_by"]]
ALIAS = {"c++": "cpp", "c#": "csharp", "shell": "bash", "sh": "bash", "coq": "rocq", "lean4": "lean", "js": "javascript", "ts": "typescript", "systemverilog": "verilog", "html": "html-css", "css": "html-css", "terraform": "hcl"}

RULES_LAYER = {
    "text": r"dedup|decontaminat|license filter|\bpii\b|secret|near-duplicate",
    "tokens": r"tokeniz|fill-in-the-middle|\bfim\b|infill",
    "tree": r"tree-sitter|\bast\b|syntax tree|\bparser\b|grammar-constrained|constrained decoding|structure-aware",
    "types": r"type (inference|prediction|check|annotation|error)|type-check|typecheck|\bmypy\b|pyright",
    "execution": r"sandbox|execution trace|output prediction|execution-based|execute[sd]? (the |model|untrusted|code)|code execution|\bruntime\b",
    "tests": r"unit test|test case|test generation|test suite|hidden tests|testbench",
    "proof": r"\blean\b|\bcoq\b|rocq|isabelle|dafny|verus|formal verif|theorem|proof",
    "change": r"\bcommit|pull request|\bdiff\b|\bpatch|code review|merge conflict|refactor|migration|github issue",
}
RULES_LEVEL = {
    "gates": r"verilog|vhdl|\brtl\b|hardware description|chip design",
    "machine": r"assembly|\bbinar(y|ies)\b|decompil|webassembly|\bwasm\b|machine code|\bx86\b|disassembl",
    "os": r"\bkernel\b|\bshell\b|\bbash\b|terminal|sandbox|container|docker|apptainer|syscall|system administration|command.line",
    "compilers": r"compiler|\bllvm\b|transpil|code translation|intermediate representation|superoptim",
    "apps": r"\bweb\b|front-?end|\bhtml\b|\bsql\b|database|data science|notebook|spreadsheet|\bui\b|android|website|design-to-code|data analysis",
    "networks": r"kubernetes|terraform|infrastructure.as.code|\biac\b|devops|cloud (infrastructure|config|service)|network config|distributed system|ansible|incident",
    "learned": r"machine learning (code|engineering|research|task)|ml engineering|\bmle\b|research replication|ml research|training script",
}
def file_resource(r):
    """Assign each catalog entry to forms of a program (layers) and levels of the stack. Explicit fields win; the rest is rule-based and reviewed by eye."""
    text = " ".join([r["name"], r["summary"], (r.get("how_to_use") or "") if r["kind"] != "tool" else ""]).lower()   # tools are filed by what they are, not by how they are used
    T, S, K = set(r["tasks"]), set(r["stages"]), r["kind"]
    lay = set(x for x in (r.get("layers") or []) if x in PROG); lev = set(x for x in (r.get("levels") or []) if x in LEVEL)
    explicit = bool(lay or lev)
    for k, rx in RULES_LAYER.items():
        if re.search(rx, text): lay.add(k)
    for k, rx in RULES_LEVEL.items():
        if re.search(rx, text): lev.add(k)
    if not explicit:
        if "pretrain" in S and K in ("dataset", "tool"): lay.add("text")
        if "completion" in T: lay.add("tokens")
        if "testing" in T or (S & {"rl", "eval"} and T & {"generation", "competitive"} and K in ("benchmark", "environment", "dataset")): lay.add("tests")
        if "formal" in T: lay.add("proof")
        if T & {"repair", "review", "repo-level", "agentic"}: lay.add("change")
        if "terminal" in T: lev.add("os")
        if "sql" in T: lev.add("apps")
        if "repo-level" in T: lev.add("apps")
        if T & {"completion", "generation", "competitive", "reasoning"} or "pretrain" in S: lev.add("languages")
        if K in ("model", "recipe") or (K == "tool" and S & {"sft", "rl", "preference"} and not r["id"].startswith("sb-") and not re.search(r"sandbox|harness|benchmark|isolat", text)): lev.add("learned")
    if r["id"].startswith("sb-"): lay.add("execution"); lev.add("os")
    if not lev: lev.add("languages")
    r["layers"] = [x for x in LAYER_IDS if x in lay]; r["levels"] = [x for x in LEVEL_IDS if x in lev]
    cov = (COVER.get("resources") or {}).get(r["id"])
    own = [ALIAS.get(x, x) for x in r["languages"]]
    langs = (cov or {}).get("langs") or [x for x in own if x in LANG or not LANG]
    r["langs"] = [x for x in dict.fromkeys(langs) if x in LANG] if LANG else [x for x in own if x != "multi"]
    r["langs_total"] = (cov or {}).get("all_langs_count")
UNFILE = {"lean-workbook": ("levels", "compilers"), "scancode-toolkit": ("layers", "types"), "sb-kata": ("levels", "networks"), "bespoke-stratos-17k": ("layers", "proof"), "sec-bench": ("layers", "proof"), "compilergym": ("layers", "tree"), "compile-llvm-ir": ("layers", "tree")}   # rule misfires found by reading the output
for r in RES:
    file_resource(r)
    if r["id"] in UNFILE: k, v = UNFILE[r["id"]]; r[k] = [x for x in r[k] if x != v]
def in_layer(i): return [r for r in RES if i in r["layers"]]
def in_level(i): return [r for r in RES if i in r["levels"]]
def in_lang(i): return [r for r in RES if i in r["langs"]]
MEASURED = ("dataset", "benchmark", "environment")
def lang_counts(i):
    rs = in_lang(i); return {k: sum(1 for r in rs if r["kind"] == k) for k in MEASURED}
FIG_COUNT = len({d["fig"] for d in PROGRAM + STACK if d.get("fig")}) + 4   # + home, the two on the intelligence page, and the pass-rate figure in the guide

def fig_html(name, title, cap, attrs=""):
    return ('<figure class="fig live" data-fig="%s"%s><div class="fig-head"><span class="eyebrow">Interactive</span><h3>%s</h3></div>'
            '<p class="nojs">This figure is computed in your browser and needs JavaScript.</p><figcaption>%s</figcaption></figure>') % (name, attrs, e(title), inline(cap))
def lang_data():
    return '<script type="application/json" id="langdata">%s</script>' % json.dumps({l["id"]: {"name": l["name"], "year": l["year"], "code": l["sample"]["code"], "runs": l["runs"]} for l in sorted(LANGLIST, key=lambda x: x["name"].lower()) if l.get("sample")}, ensure_ascii=False).replace("</", "<\\/")
FIG_JS = '<script src="/lang.js?v=%s" defer></script><script src="/figs.js?v=%s" defer></script>' % (VER, VER)

def lang_chip(i, small=False):
    l = LANG.get(i)
    if not l: return '<span class="lchip none">%s</span>' % e(i)
    return '<a class="lchip fam-%s%s" href="/languages/%s/">%s</a>' % (l["family"], " sm" if small else "", i, e(l["name"]))
def landmarks_html(key, title=None):
    d = LANDMARKS.get(key) or {}
    h = ""
    if d.get("landmarks"):
        items = sorted(d["landmarks"], key=lambda x: x.get("year") or 0)
        h += '<h2>%s</h2><ol class="marks">%s</ol>' % (e(title or "Landmarks"), "".join('<li><span class="yr">%s</span><div><b>%s</b>%s<p>%s%s</p></div></li>' % (
            e(str(x.get("year") or "")), e(x["name"]), (' <span class="who">%s</span>' % e(x["who"])) if x.get("who") else "", inline(x["text"]), (' <a class="src" href="%s">source</a>' % e(x["url"])) if x.get("url") else "") for x in items))
    if d.get("open"):
        h += '<h2>%s</h2>' % e(("Open problems: " + title.split(": ")[-1]) if title else "Open problems and frontiers") + '<ul class="opens">%s</ul>' % "".join('<li><b>%s</b><p>%s%s</p></li>' % (e(x["name"]), inline(x["text"]), (' <a class="src" href="%s">source</a>' % e(x["url"])) if x.get("url") else "") for x in d["open"])
    return h

# ---------------------------------------------------------------- pages
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
    f_lang = opts(sorted(((l["id"], l["name"]) for l in LANGLIST if in_lang(l["id"])), key=lambda x: x[1].lower()), "All languages")
    f_layer = opts([(d["id"], d["n"] + " " + d["title"]) for d in PROGRAM], "Any form of a program")
    f_level = opts([(d["id"], d["n"] + " " + d["title"]) for d in reversed(STACK)], "Any level of the stack")
    f_task = opts([(t, TASKS[t]) for t in TASKS if any(t in r["tasks"] for r in RES)], "All tasks")
    f_lic = opts([(k, v) for k, v in LIC_LABEL.items()], "Any license")
    body = wrap(f'''<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / <a href="/train/">Train</a> / Catalog</div><span class="eyebrow">Catalog</span><h1>{len(RES)} resources, each checked at the source</h1>
<p class="lede">Filter by training stage, kind, language, task, license family, the <a href="/program/">form of a program</a> an entry teaches or checks, and the <a href="/stack/">level of the stack</a> it works at. The license family is derived from the license text and is a hint only: read the source before you train on anything.</p></div>
<div class="filters"><div class="row1"><div class="search"><input id="q" type="search" placeholder="Search names, tasks, languages..." aria-label="Search resources" autocomplete="off"></div>
<select class="f" id="f-kind" aria-label="Kind">{f_kind}</select><select class="f" id="f-lang" aria-label="Language">{f_lang}</select><select class="f" id="f-task" aria-label="Task">{f_task}</select><select class="f" id="f-lic" aria-label="License family">{f_lic}</select><select class="f" id="f-layer" aria-label="Form of a program">{f_layer}</select><select class="f" id="f-level" aria-label="Level of the stack">{f_level}</select><span class="count" id="cnt"></span></div>
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
    body = wrap(f'''<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / <a href="/train/">Train</a> / <a href="/catalog/">Catalog</a> / <a href="/stage/{primary}/">{e(STAGE[primary]["short"])}</a></div>
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
{kv("Languages", (names(r["langs"][:14]) + ((" and %d more" % (len(r["langs"]) - 14)) if len(r["langs"]) > 14 else "") + ((" <small>(source lists %s in all)</small>" % r["langs_total"]) if r.get("langs_total") else "")) if r["langs"] else e(", ".join(r["languages"])))}
{kv("Form", " ".join('<a class="pill" href="/program/%s/">%s</a>' % (x, e(PROG[x]["title"])) for x in r["layers"]))}{kv("Stack level", " ".join('<a class="pill" href="/stack/%s/">%s</a>' % (x, e(LEVEL[x]["title"])) for x in r["levels"]))}{kv("Tasks", e(", ".join(TASKS[t] for t in r["tasks"])))}{kv("Difficulty", e(r["difficulty"] or ""))}
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
    body = wrap(f'''<div class="page st-{s["id"]}"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / <a href="/train/">Train</a> / Stage {s["n"]}</div><span class="eyebrow" style="color:var(--hue)">Stage {s["n"]}</span><h1>{e(s["title"])}</h1><p class="lede">{e(s["tagline"])}</p></div>
<div class="prose"><h2>Who needs this</h2><p>{e(s["who"])}</p><h2>Decisions you will make</h2><ul>{li(s["decide"])}</ul><h2>Pitfalls</h2><ul>{li(s["pitfalls"])}</ul></div>
{sections}<div style="margin-top:34px">{nav}</div></div>''')
    shell("/stage/%s/" % s["id"], "%s | Renaissance Labs Code" % s["title"], s["tagline"] + " " + str(len(items)) + " verified resources.", body, "", og="stage-" + s["id"])

def load_page(name):
    p = os.path.join(ROOT, "data/pages", name + ".html")
    return refs(open(p, encoding="utf-8").read())

def page_long(name, path, title, desc, eyebrow, h1, lede, current, og):
    tr = '<a href="/train/">Train</a> / ' if current in TRAIN_KEYS else ""
    body = wrap(f'<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / {tr}{e(eyebrow)}</div><span class="eyebrow">{e(eyebrow)}</span><h1>{h1}</h1><p class="lede">{lede}</p></div><div class="prose">{load_page(name)}</div></div>')
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
    body = wrap(f'''<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / <a href="/train/">Train</a> / Recipe builder</div><span class="eyebrow">Recipe builder</span><h1>Tell us what you have. Get an ordered plan.</h1>
<p class="lede">Rules written by hand from the catalog, not generated on the fly. It picks stages, datasets, evals and verifiers that fit your size, budget and goal, says why, and flags the pitfalls. It is a starting point, not a guarantee: run the measure step first and let your numbers decide.</p></div>
<div class="planner"><form class="form" id="form" onsubmit="return false">{form}</form><div class="out" id="out" aria-live="polite"></div></div></div>''')
    shell("/recipe/", "Recipe builder for training a coding model | Renaissance Labs Code", "Pick model size, compute, languages and goal. Get an ordered, honest recipe with datasets, evals, verifiers and pitfalls from a verified catalog.", body, "recipe", og="recipe",
          extra_foot='<script type="application/json" id="rdata">%s</script><script src="/recipe.js?v=%s" defer></script>' % (json.dumps(data).replace("</", "<\\/"), VER))

# ---------------------------------------------------------------- the maps: pages
def res_block(items, link, what, head="<h2>Training resources filed here</h2>"):
    """Resources filed under a form, level or language: counts by kind, the first cards, and a link to the full filtered catalog."""
    if not items: return head + '<p class="gapnote">Nothing in the catalog is filed here. That is a finding, not an omission we are hiding: we looked, and open material for %s is scarce or absent.</p>' % e(what)
    order = {"benchmark": 0, "environment": 1, "dataset": 2, "tool": 3, "model": 4, "recipe": 5, "paper": 6}
    items = sorted(items, key=lambda r: (order.get(r["kind"], 9), r["name"].lower()))
    counts = " ".join('<span class="pill">%d %s%s</span>' % (n, e(KINDS[k].lower()), "" if n == 1 else "s") for k, n in ((k, sum(1 for r in items if r["kind"] == k)) for k in order) if n)
    show, seen = [], {}
    for r in items:                                    # a spread across kinds, not twelve of the same
        if seen.get(r["kind"], 0) < 4 and len(show) < 12: show.append(r); seen[r["kind"]] = seen.get(r["kind"], 0) + 1
    more = '<p class="more"><a class="btn" href="%s">All %d in the catalog &rarr;</a></p>' % (link, len(items)) if len(items) > len(show) else ""
    return head + '<p class="rescount">%s</p></div><div class="grid">%s</div>%s<div class="prose wide">' % (counts, "".join(card(r) for r in show), more)

def stack_slabs(current=None):
    rows = ""
    for d in STACK:
        langs = [LANG[x.strip()] for x in (d.get("langs") or "").split(",") if x.strip() in LANG]      # the languages named on the level's own page, in that order
        chips = "".join('<span class="lchip sm fam-%s">%s</span>' % (l["family"], e(l["name"])) for l in langs[:7]) + ('<span class="lchip sm more">+%d</span>' % (len(langs) - 7) if len(langs) > 7 else "")
        n = len(in_level(d["id"]))
        rows += (f'<a class="slab lv-{d["id"]}{" cur" if d["id"] == current else ""}" href="/stack/{d["id"]}/"><span class="n">{d["n"]}</span><span class="t"><b>{e(d["title"])}</b><i>{e(d["short"])}</i></span>'
                 f'<span class="ch">{chips}</span><span class="ct">{("<b>%d</b> resources" % n) if n else "no resources"}</span></a>')
    return '<div class="stackmap">%s</div>' % rows

def program_strip(current=None):
    return '<div class="forms">%s</div>' % "".join(
        f'<a class="form{" cur" if d["id"] == current else ""}" href="/program/{d["id"]}/"><span class="n">{d["n"]}</span><b>{e(d["title"])}</b><i>{e(d["short"])}</i><span class="ct">{len(in_layer(d["id"]))} resources</span></a>' for d in PROGRAM)

def ideas_html(text):
    rows = [l.split(" :: ", 1) for l in (text or "").split("\n") if " :: " in l]
    return '<dl class="ideas">%s</dl>' % "".join("<dt>%s</dt><dd>%s</dd>" % (inline(a), inline(b)) for a, b in rows)

def page_node(kind, d):
    """One form of a program, or one level of the stack. Same shape as an area page on the mathematics site."""
    prog = kind == "program"
    seq = PROGRAM if prog else list(reversed(STACK))           # reading order: forms 1..8, levels bottom to top
    idx = [x["id"] for x in seq].index(d["id"]); prev_ = seq[idx - 1] if idx else None; next_ = seq[idx + 1] if idx + 1 < len(seq) else None
    base = "/program/" if prog else "/stack/"
    items = in_layer(d["id"]) if prog else in_level(d["id"])
    fig = fig_html(d["fig"], d["figtitle"], d["figcap"]) if d.get("fig") else ""
    ex_title, _, ex_body = (d.get("example") or "").partition("\n")
    side = "".join('<li%s><a href="%s%s/"><span>%s</span>%s</a></li>' % (' class="cur"' if x["id"] == d["id"] else "", base, x["id"], x["n"], e(x["title"])) for x in (PROGRAM if prog else STACK))
    extra = ""
    if not prog:
        langs = [x.strip() for x in (d.get("langs") or "").split(",") if x.strip()]
        extra += '<div class="panel"><h3>Rests on</h3><p>%s</p><h3 style="margin-top:14px">Gives the level above</h3><p>%s</p></div>' % (inline(d.get("rests", "")), inline(d.get("gives", "")))
        extra += '<div class="panel"><h3>Languages at this level</h3><div class="chipsrow">%s</div></div>' % ("".join(lang_chip(x, True) for x in langs) if langs else '<p>None. Nothing is programmed here; it is built.</p>')
    nav = '<div class="cta-row">%s%s</div>' % ('<a class="btn" href="%s%s/">&larr; %s</a>' % (base, prev_["id"], e(prev_["title"])) if prev_ else "", '<a class="btn" href="%s%s/">%s &rarr;</a>' % (base, next_["id"], e(next_["title"])) if next_ else "")
    label = ("Form %s of %d" % (d["n"], len(PROGRAM))) if prog else ("Level %s of %d" % (d["n"], len(STACK)))
    cat = "/catalog/#%s=%s" % ("layer" if prog else "level", d["id"])
    what = "this form of a program" if prog else "this level of the stack"
    body = wrap(f'''<div class="page nodepage"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / <a href="{base}">{"What a program is" if prog else "The stack"}</a> / {e(d["title"])}</div>
<span class="eyebrow">{label}</span><h1>{e(d["full"])}</h1><p class="question">{e(d["question"])}</p></div>
<div class="layout"><div class="maincol"><div class="prose wide">{rich(d["lede"])}
<h2>{e(ex_title)}</h2>{rich(ex_body)}
{fig}
{('<div class="notice"><b>What to notice</b>%s</div>' % rich(d["notice"])) if d.get("notice") else ""}
<h2>Central ideas</h2>{ideas_html(d.get("ideas"))}
{landmarks_html(d["id"])}
<h2>What this means for training models</h2>{rich(d.get("models"))}
{res_block(items, cat, what)}
{nav}</div></div>
<aside class="aside"><div class="panel"><h3>{"The forms of a program" if prog else "The stack, top to bottom"}</h3><ol class="sidenav">{side}</ol></div>{extra}</aside></div></div>''')
    desc = strip_md(d["short"]) + " " + d["question"]
    shell("%s%s/" % (base, d["id"]), "%s | Renaissance Labs Code" % d["full"], desc[:200], body, "program" if prog else "stack", og=("p-" if prog else "s-") + d["id"],
          extra_foot=(lang_data() if d.get("fig") == "langs" else "") + FIG_JS)

def page_program_index():
    body = wrap(f'''<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / What a program is</div><span class="eyebrow">Map one</span><h1>What a program <em>is</em></h1>
<p class="lede">A program is one thing seen in eight forms. It is text, then words, then a tree, then something with types, then a running process, then something tested, something proved, and something that keeps changing. Each form is a different answer to the question "what is this?", and each gives a machine a different way to check it.</p></div>
<div class="prose"><p>Follow one small program through all eight. The program is Euclid's algorithm for the greatest common divisor, written about 2,300 years ago and still run every day. On each page you can edit it and watch that form respond, because the figures are driven by a real lexer, parser, type checker, compiler and machine running in your browser.</p></div>
{program_strip()}
<div class="prose"><h2>Why the order matters</h2><p>Each form is built from the one before, and each is harder to get right. Text that cannot be cut into tokens has no tree. A tree with a type error is never run. A program that runs may fail its tests, and a program that passes its tests may still be wrong for an input nobody tried.</p>
<p>Read the other way, the list is a ladder of checks, from cheapest to strongest: does it parse, does it type-check, does it run, does it pass, is it proved. That ladder is the reason code is the best understood subject for training models. At every rung a machine can say yes or no without asking a person.</p></div></div>''')
    shell("/program/", "What a program is: eight forms of the same thing | Renaissance Labs Code", "Text, tokens, tree, types, execution, tests, proof and change: one small program followed through every form it takes, with live figures.", body, "program", og="program", extra_foot=FIG_JS)

DESCENT = [
    ("apps", "In a spreadsheet", "=A1+B1", "A person asks for a sum."),
    ("languages", "In Python", "a + b", "A programmer writes the same request in a general language."),
    ("compilers", "In Python's virtual machine", "BINARY_ADD", "The compiler has turned the line into an instruction for an imaginary processor (the name is from Python 3.10 and earlier; newer versions call it BINARY_OP)."),
    ("machine", "In the real processor", "add w0, w1, w0", "Compiled C, here for a 64-bit ARM chip. One instruction, stored as the number 0B000020 in hexadecimal."),
    ("gates", "In logic", "32 full adders", "In the simplest design, the instruction switches on a circuit that adds two 32-bit numbers one column at a time, passing carries along. Real processors use faster adders."),
    ("physics", "In matter", "charge moves", "At least a thousand transistors open and close for the addition itself, and many more fetch, decode and store the result. The answer is a pattern of voltages."),
]
def page_stack_index():
    desc = "".join('<li class="lv-%s"><span class="lvl"><a href="/stack/%s/">%s</a></span><div><span class="where">%s</span><code>%s</code><p>%s</p></div></li>' % (i, i, e(LEVEL[i]["title"]), e(w), e(c), e(t)) for i, w, c, t in DESCENT if i in LEVEL)
    body = wrap(f'''<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / The stack</div><span class="eyebrow">Map two</span><h1>The stack: from <em>sand</em> to trained models</h1>
<p class="lede">A computer is built in levels. Each level is made entirely out of the one below it, and offers the one above a simpler, more powerful set of things to work with. A programmer at any level can mostly forget the levels underneath. That forgetting is what makes software possible, and understanding code means knowing what was forgotten.</p></div>
{stack_slabs()}
<div class="prose wide"><h2>One addition, all the way down</h2><p>Adding two numbers looks like a single act. Followed down the stack, it is the same request restated six times, each time closer to the physics.</p>
<ol class="descent">{desc}</ol>
<p>No level contains the meaning of the one above. The transistors do not know they are adding, the adder does not know it serves Python, and Python does not know it is totaling an invoice. Each level only keeps a promise to its neighbor. Software is that tower of promises.</p>
<h2>How to read the map</h2><p>The top of the stack is where intent enters and the bottom is where physics takes over. Programming languages are placed at the level where they most characteristically work, though many reach across several. Each level's page explains the one idea that level contributes, lets you operate a working model of it, and lists the open resources for training models to write code there.</p>
<p>The numbers on the right are entries in our <a href="/catalog/">verified catalog</a>. They fall away steeply toward the bottom of the stack. Models have been taught to write Python functions far more thoroughly than to write hardware or reason about a network.</p></div></div>''')
    shell("/stack/", "The stack: from transistors to learned programs | Renaissance Labs Code", "Nine levels, each built from the one below: transistors, logic gates, machine code, operating systems, compilers, languages, applications, networks and trained models.", body, "stack", og="stack")

def cov_total(i): c = lang_counts(i); return sum(c.values())
def page_languages():
    if not LANGLIST: return
    mx = max([cov_total(l["id"]) for l in LANGLIST] + [1])
    def chip(l):
        n = cov_total(l["id"]); w = 0 if not n else int(12 + 60 * n / mx)
        return '<a class="lcell fam-%s" href="/languages/%s/" style="--w:%d" title="%s, %d: %d datasets, benchmarks and environments in the catalog"><b>%s</b><i>%s</i><span>%d</span></a>' % (l["family"], l["id"], w, e(l["name"]), l["year"], n, e(l["name"]), n if n else "0", l["year"])
    rows = ""
    for d in STACK:
        ls = sorted((l for l in LANGLIST if l["level"] == d["id"]), key=lambda x: x["year"])
        if ls: rows += '<div class="lrow lv-%s"><a class="lvl" href="/stack/%s/"><span>%s</span>%s</a><div class="lcells">%s</div></div>' % (d["id"], d["id"], d["n"], e(d["title"]), "".join(chip(l) for l in ls))
    fams = ""
    for fid, name, text in FAMILIES:
        ls = sorted((l for l in LANGLIST if l["family"] == fid), key=lambda x: x["year"])
        if ls: fams += '<div class="famblk fam-%s"><h3>%s</h3><p>%s</p><div class="chipsrow">%s</div></div>' % (fid, e(name), e(text), "".join(lang_chip(l["id"]) for l in ls))
    bars = ""
    for l in sorted(LANGLIST, key=lambda x: (-cov_total(x["id"]), x["name"].lower())):
        c = lang_counts(l["id"]); t = sum(c.values())
        seg = "".join('<i class="k-%s" style="width:%.2f%%"></i>' % (k, 100.0 * c[k] / mx) for k in MEASURED if c[k])
        bars += '<a class="cbar%s" href="/languages/%s/"><span class="nm">%s</span><span class="cb">%s</span><span class="ct">%d</span></a>' % ("" if t else " zero", l["id"], e(l["name"]), seg, t)
    timeline = "".join('<a class="tl fam-%s" href="/languages/%s/"><span>%d</span>%s</a>' % (l["family"], l["id"], l["year"], e(l["name"])) for l in sorted(LANGLIST, key=lambda x: (x["year"], x["name"])))
    legend = "".join('<span class="lchip sm fam-%s">%s</span>' % (f[0], e(f[1])) for f in FAMILIES if any(l["family"] == f[0] for l in LANGLIST))
    nbench = sum(1 for l in LANGLIST if lang_counts(l["id"])["benchmark"]); nenv = sum(1 for l in LANGLIST if lang_counts(l["id"])["environment"])
    body = wrap(f'''<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / Languages</div><span class="eyebrow">Map three</span><h1>{len(LANGLIST)} languages, placed on the <em>stack</em></h1>
<p class="lede">Every general-purpose language can compute the same things. They differ in where they sit between the machine and the person, and in what they refuse to let you get wrong. This map places each language at the level of the stack where it does its characteristic work, and shows how much open material exists for training a model to write it.</p></div>
<div class="legend">{legend}</div>
<div class="langmap">{rows}</div>
<p class="mnote">Each tile: name, year of first appearance, and the number of datasets, benchmarks and environments in our catalog that explicitly cover the language. Darker means more. Checked {e(CHECKED)}.</p>
<div class="prose wide"><h2>One algorithm in every language</h2><p>Each language page shows the same small program, Euclid's algorithm, so the notations can be compared like translations of one sentence. Pick any two.</p>
{fig_html("langs", "The same program in two languages", "Samples were run on a real toolchain where one was available, and otherwise checked against the language's own documentation. Each language page says which.")}
<h2>Twelve families</h2><p>Languages cluster by what they are for. The families below are a practical grouping, not a strict taxonomy, and many languages borrow from several.</p></div>
<div class="famgrid">{fams}</div>
<div class="prose wide"><h2>Seventy years, in order</h2><p>Languages are not replaced so much as layered. Fortran, Lisp and COBOL, all from the 1950s, are still in use.</p></div>
<div class="timeline">{timeline}</div>
<div class="prose wide"><h2>Where the training data is</h2><p>The count for each language is the number of datasets, benchmarks and environments in the catalog whose own documentation lists that language. It measures what is openly available to train and test on, not how good or how popular a language is. Every language here appears in at least one large corpus of public code, but that is where it ends for many: only {nbench} of the {len(LANGLIST)} have a benchmark that covers them, and only {nenv} have an environment a model can practice in.</p></div>
<div class="covkey"><span><i class="k-dataset"></i>datasets</span><span><i class="k-benchmark"></i>benchmarks</span><span><i class="k-environment"></i>environments</span></div>
<div class="covbars">{bars}</div></div>''')
    shell("/languages/", "%d programming languages, mapped to the stack | Renaissance Labs Code" % len(LANGLIST), "Where each programming language sits between the machine and the person, what family it belongs to, the same program in each, and how much open training data exists for it.", body, "languages", og="languages", extra_foot=lang_data() + FIG_JS)

def names(ids): return ", ".join(('<a href="/languages/%s/">%s</a>' % (x, e(LANG[x]["name"]))) if x in LANG else e(x) for x in ids)
def page_language(l):
    c = lang_counts(l["id"]); rs = in_lang(l["id"])
    s = l.get("sample") or {}
    ran = ('<p class="snote"><b>Run and checked:</b> %s</p>' % e(s.get("how") or "")) if s.get("ran") else ('<p class="snote"><b>Not run here.</b> %s</p>' % e(s.get("how") or "Checked against the language documentation."))
    notable = "".join('<li><b>%s</b> %s <a class="src" href="%s">source</a></li>' % (e(n["name"]), inline(n["text"]), e(n["url"])) for n in l.get("notable") or [])
    mini = "".join('<a class="slab sm lv-%s%s" href="/stack/%s/"><span class="n">%s</span><span class="t"><b>%s</b></span></a>' % (d["id"], " cur" if d["id"] in l["levels"] else "", d["id"], d["n"], e(d["title"])) for d in STACK)
    other = "python" if l["id"] != "python" else "c"
    srcs = "".join('<li><a href="%s">%s</a></li>' % (e(u), e(re.sub(r"^https?://(www[.])?", "", u)[:44])) for u in (l.get("sources") or [])[:6])
    fam = FAM[l["family"]]
    cov = "This language is explicitly covered by <b>%d</b> datasets, <b>%d</b> benchmarks and <b>%d</b> environments in the catalog." % (c["dataset"], c["benchmark"], c["environment"]) if rs else ""
    body = wrap(f'''<div class="page nodepage fam-{l["family"]}"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / <a href="/languages/">Languages</a> / {e(fam[1])}</div>
<span class="eyebrow">{e(fam[1])} language &middot; {l["year"]}</span><h1>{e(l["name"])}</h1><p class="lede">{inline(l["what"])}</p></div>
<div class="layout"><div class="maincol"><div class="prose wide">
<h2>How it runs</h2><p>{inline(l["runs"])}</p><p><b>Types:</b> {inline(l.get("typing") or "not applicable")}. <b>Style:</b> {e(", ".join(l.get("paradigms") or []))}.</p>
<h2>Euclid's algorithm in {e(l["name"])}</h2>{plainbox(s.get("code", ""), l["name"]) if s.get("code") else ""}{ran}
{fig_html("langs", "Compare with another language", "The same program, side by side.", ' data-a="%s" data-b="%s"' % (l["id"], other))}
<h2>What it is used for</h2><ul>{"".join("<li>%s</li>" % inline(u) for u in l.get("used_for") or [])}</ul>
{('<h2>Built with it</h2><ul class="notable">%s</ul>' % notable) if notable else ""}
<h2>Training a model to write {e(l["name"])}</h2><p>{cov}</p>
{res_block(rs, "/catalog/#lang=" + l["id"], l["name"], "")}
</div></div><aside class="aside"><div class="panel"><h3>At a glance</h3><dl>
{kv("First appeared", "%d<br><small>%s</small>" % (l["year"], e(l.get("year_note") or "")))}
{kv("Designed by", e(", ".join(l.get("designers") or [])))}{kv("Steward", e(l.get("org") or ""))}
{kv("Family", '<a href="/languages/">%s</a>' % e(fam[1]))}
{kv("Came from", names(l["influenced_by"]))}{kv("Led to", names(l["influenced"]))}
{kv("Official site", '<a href="%s">%s</a>' % (e(l["official_url"]), e(re.sub(r"^https?://(www[.])?", "", l["official_url"]).rstrip("/")[:40])) if l.get("official_url") else "")}
{kv("Specification", '<a href="%s">read</a>' % e(l["spec_url"]) if l.get("spec_url") else "")}</dl></div>
<div class="panel"><h3>Where it works on the stack</h3><div class="stackmap mini">{mini}</div></div>
{('<div class="panel"><h3>Sources</h3><ul>%s</ul></div>' % srcs) if srcs else ""}</aside></div></div>''')
    shell("/languages/%s/" % l["id"], "%s: what it is, how it runs, and what exists to train on it | Renaissance Labs Code" % l["name"], strip_md(l["what"])[:200], body, "languages", og="l-" + l["id"], extra_foot=lang_data() + FIG_JS)

DOMAIN = {"infrastructure": "Infrastructure", "internet": "The internet", "finance": "Money", "government": "Government", "transport": "Transport", "space": "Space", "health": "Health", "industry": "Industry", "science": "Science", "security": "Security", "data": "Data", "commons": "The commons", "assurance": "Verified software", "ai": "Models"}
def facts_html(facts, keep=2):
    li = lambda f: '<li>%s <a class="src" href="%s">source%s</a></li>' % (inline(f["text"]), e(f["url"]), (", " + e(f["date"])) if f.get("date") else "")
    facts = facts or []
    h = '<ul class="facts">%s</ul>' % "".join(li(f) for f in facts[:keep])
    if len(facts) > keep: h += '<details class="morefacts"><summary>%d more sourced facts</summary><ul class="facts">%s</ul></details>' % (len(facts) - keep, "".join(li(f) for f in facts[keep:]))
    return h
def page_world():
    if not WORLD.get("systems"): return
    sysh = ""
    for s in WORLD["systems"]:
        chips = "".join(lang_chip(x, True) for x in s.get("languages") or []) + "".join('<a class="lchip sm lvchip" href="/stack/%s/">%s</a>' % (x, e(LEVEL[x]["title"])) for x in s.get("levels") or [] if x in LEVEL)
        sysh += '<article class="wsys" id="%s"><span class="eyebrow">%s</span><h3>%s</h3><p class="claim">%s</p>%s%s%s</article>' % (
            e(s["id"]), e(DOMAIN.get(s.get("domain"), s.get("domain") or "")), e(s["title"]), inline(s["claim"]), facts_html(s.get("facts")), ('<div class="chipsrow">%s</div>' % chips) if chips else "", ('<p class="caveat"><b>How solid is this</b> %s</p>' % inline(s["caveat"])) if s.get("caveat") else "")
    fail = "".join('<li id="%s"><span class="yr">%s</span><div><b>%s</b><p>%s</p><p class="lesson">%s <a class="src" href="%s">source</a></p></div></li>' % (e(f["id"]), f["year"], e(f["title"]), inline(f["what"]), inline(f["lesson"]), e(f["url"])) for f in sorted(WORLD["failures"], key=lambda x: x["year"]))
    liv = "".join('<article class="wsys" id="%s"><h3>%s</h3><p class="claim">%s</p>%s%s</article>' % (e(x["id"]), e(x["title"]), inline(x["text"]), facts_html(x.get("facts")), ('<p class="caveat"><b>How solid is this</b> %s</p>' % inline(x["caveat"])) if x.get("caveat") else "") for x in WORLD["living"])
    unv = "".join("<li>%s</li>" % inline(x) for x in opt_json("data/world-unverified.json", []))
    body = wrap(f'''<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / Code in the world</div><span class="eyebrow">Map four</span><h1>What the world <em>runs on</em></h1>
<p class="lede">Most of the rules a modern society follows are no longer carried out by people. A payment clears, a plane holds its course, a dose is measured, a message finds its way across the planet, and at each step the thing doing the work is a program somebody wrote, often long ago. This page collects what can actually be sourced about that, and says where the popular numbers cannot be.</p></div>
<div class="prose wide"><h2>Where code holds things up</h2><p>Each claim below links to the document it was read from, with the date. Where a field publishes standards instead of statistics, we cite the standard.</p></div>
<div class="wgrid">{sysh}</div>
<div class="prose wide"><h2>When code fails</h2><p>Because programs act without anyone watching, their mistakes act too. These are well documented cases, each from the official report or the maintainers' own account. They are worth knowing for the same reason engineers study bridge collapses.</p>
<ol class="marks fails">{fail}</ol>
<h2>Why code is never finished</h2><p>A bridge, once built, stays built. Software sits on other software that keeps moving, so a program left alone slowly stops working. Keeping it alive is most of the work.</p></div>
<div class="wgrid">{liv}</div>
<div class="prose wide">{('<h2>What we could not verify</h2><p>These claims are repeated widely. We looked for a primary source for each and did not find one we could read, so none of them appears above.</p><ul>%s</ul>' % unv) if unv else ""}
<h2>What this means for training models</h2><p>Three things follow for anyone teaching a model to write code. Most real code is old, large and written in languages that benchmarks barely touch. The cost of a mistake is set by where the code runs, not by how hard it was to write. And the dominant activity is maintenance: reading and changing what exists. The <a href="/program/change/">change</a> page and the <a href="/languages/">languages map</a> show how far current open training material is from that picture.</p></div></div>''')
    shell("/world/", "Code in the world: what civilization runs on | Renaissance Labs Code", "Sourced facts about the software that payments, aviation, medicine, the internet and science depend on, the best documented failures, and why software is never finished.", body, "world", og="world")

def page_train():
    rail = "".join(f'<a class="node st-{s["id"]}" href="/stage/{s["id"]}/"><span class="n">{s["n"]}</span><h3>{e(s["title"].split(":")[0])}</h3><p>{e(s["tagline"])}</p><span class="ct"><b>{stage_count(s["id"])}</b> resources</span></a>' for s in STAGES)
    body = wrap(f'''<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / Train</div><span class="eyebrow">Train</span><h1>Teaching a model to <em>write</em> code</h1>
<p class="lede">The maps on this site say what code is. This section is the practical side: {len(RES)} verified datasets, benchmarks, environments and tools, a planner that turns your model size and budget into an ordered recipe, and an honest guide to what works.</p>
<div class="cta-row"><a class="btn primary" href="/recipe/">Build a recipe</a><a class="btn" href="/guide/">Read the guide</a><a class="btn" href="/catalog/">Browse the catalog</a><a class="btn" href="/pitfalls/">Pitfalls</a></div></div>
<div class="prose"><h2>Why code can be trained on at all</h2><p>A model learns from feedback, and code is unusual in how much feedback a machine can give without a person. Each <a href="/program/">form of a program</a> is a check: it parses or it does not, the types agree or they do not, the tests pass or fail, the proof is accepted or rejected. Training a coding model is the craft of turning those checks into data and rewards without fooling yourself.</p></div>
<section class="blk"><div class="sec-head"><div><span class="eyebrow">The pipeline</span><h2>Six stages, one loop</h2><p>Measure first, change one thing, measure again. Each stage has a page with the decisions, the pitfalls and the resources.</p></div></div>
<div class="rail">{rail}</div>
<p class="loopnote"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8M21 3v5h-5M21 12a9 9 0 0 1-15.5 6.2L3 16M3 21v-5h5"/></svg>After every stage, go back to Evaluation and measure again with the same settings.</p></section>
<section class="blk"><div class="sec-head"><div><span class="eyebrow">Taxonomy</span><h2>What exists, by task and stage</h2><p>Click a cell to see the entries. Hatched cells are empty in this catalog.</p></div></div>{matrix_html()}
<p class="mnote">Counts are entries in this catalog (checked {e(CHECKED)}), not a census of the field.</p></section></div>''')
    shell("/train/", "Train a coding model: catalog, recipe builder and guide | Renaissance Labs Code", "Verified datasets, RL environments, benchmarks and tools for training coding models, with a recipe builder and a guide.", body, "train", og="train")

def page_home():
    nlang = len(LANGLIST)
    body = f'''<section class="hero"><div class="hero-in one"><div>
<span class="eyebrow">Renaissance Labs &middot; Code</span>
<h1>Code is thought that <em>runs</em>.</h1>
<p class="lede">Mathematics describes structure. Code is the part of human reasoning written precisely enough for a machine to carry out without us. This site maps it whole: what a program is, the stack it runs on from transistors to trained models, the languages people write, what the world runs on, and verified resources for teaching models to write it.</p>
<div class="stats"><div class="stat"><b>{len(PROGRAM)}</b><span>forms of a program</span></div><div class="stat"><b>{len(STACK)}</b><span>levels of the stack</span></div><div class="stat"><b>{nlang}</b><span>languages</span></div><div class="stat"><b>{FIG_COUNT}</b><span>live figures</span></div><div class="stat"><b>{len(RES)}</b><span>verified training resources</span></div></div>
</div></div></section>
<div class="wrap">
<section class="blk first"><figure class="fig live homefigure" data-fig="home"><p class="nojs">This figure is computed in your browser and needs JavaScript.</p><figcaption>Euclid's algorithm in a small language that runs in this page. Edit it, and every form on the right is recomputed by a real lexer, parser, type checker, compiler and machine.</figcaption></figure></section>
<section class="blk"><div class="essay"><div><span class="eyebrow">Start here</span><h2>What is code?</h2></div><div class="prose">
<p>A recipe, a law and a proof on paper are all exact writing, but each needs a person to carry it out or to judge it. Code is the one kind of writing that does not. It is reasoning set down so completely that a machine, which understands nothing, can execute it. That demand for total precision is a large part of the difficulty of programming, and all of its power.</p>
<p>Once written, a program acts alone. It can be copied without loss and run a billion steps a second, for decades, with nobody watching. Knowledge that used to live only in people (how to compute a payroll, route a call, land an aircraft) now exists outside any person and does the work itself. Code is the most general way we have found to put reasoning outside a human head and have it keep working.</p>
<p>Its nearest relative is mathematics. Mathematics says what is true, and code says what to do. The two meet exactly: a constructive proof can be read as a program, and a program can be proved. Our sister site <a href="https://math.renaissancelabs.eu">maps mathematics</a>. This one maps the half that moves.</p>
<p>The newest programs were not written at all. A trained model is a program whose behavior was found by a search over numbers, and such models now write code themselves. Code is the best ground for teaching them, for one reason: at many levels, a machine can check the answer.</p></div></div></section>
<section class="blk"><div class="sec-head"><div><span class="eyebrow">Map one</span><h2>What a program is</h2><p>One program, eight forms. Each is a different answer to "what is this?", and each gives a machine a different way to check it.</p></div><a class="btn" href="/program/">Follow the program &rarr;</a></div>{program_strip()}</section>
<section class="blk"><div class="sec-head"><div><span class="eyebrow">Map two</span><h2>The stack</h2><p>Nine levels, each built entirely from the one below. Intent enters at the top. Physics takes over at the bottom. The count on the right is how much open training material exists at each level.</p></div><a class="btn" href="/stack/">Read the stack &rarr;</a></div>{stack_slabs()}</section>
<section class="blk"><div class="sec-head"><div><span class="eyebrow">Map three</span><h2>The languages</h2><p>{nlang} languages, from hardware description to proof, each placed on the stack, each showing the same program, each with a count of what exists to train on it.</p></div><a class="btn" href="/languages/">See all {nlang} &rarr;</a></div>
<div class="timeline">{"".join('<a class="tl fam-%s" href="/languages/%s/"><span>%d</span>%s</a>' % (l["family"], l["id"], l["year"], e(l["name"])) for l in sorted(LANGLIST, key=lambda x: (x["year"], x["name"])))}</div></section>
<section class="blk"><div class="paths">
<a class="path" href="/world/"><span class="eyebrow">Map four</span><h3>What the world runs on</h3><p>Payments, aircraft, medicine, the internet: sourced facts about the code underneath, the best documented failures, and why software is never finished.</p></a>
<a class="path" href="/intelligence/"><span class="eyebrow">The idea underneath</span><h3>Code and intelligence</h3><p>What can be computed, what cannot, why a three-line program can defeat prediction, and what changes when programs are learned instead of written.</p></a>
<a class="path" href="/train/"><span class="eyebrow">The practical side</span><h3>Train a model to code</h3><p>{len(RES)} verified datasets, benchmarks, environments and tools, a recipe builder, and a guide with the caveats left in.</p></a></div></section></div>'''
    shell("/", "Renaissance Labs Code: what code is, mapped from transistors to trained models",
          "What a program is, the stack it runs on, %d languages, what the world runs on, and %d verified resources for training models to write code. With live figures." % (nlang, len(RES)), body, og="home", extra_foot=FIG_JS)

def page_intelligence():
    p = os.path.join(ROOT, "data/pages/intelligence.html")
    if not os.path.exists(p): return
    t = refs(open(p, encoding="utf-8").read())
    t = re.sub(r"\{\{fig:(\w+)\|([^|]+)\|([^}]+)\}\}", lambda m: fig_html(m.group(1), m.group(2), m.group(3)), t)
    t = re.sub(r"\{\{marks:(\w+)\|([^}]+)\}\}", lambda m: landmarks_html(m.group(1), m.group(2)), t)
    body = wrap(f'''<div class="page"><div class="page-head"><div class="crumbs"><a href="/">Code</a> / Code and intelligence</div><span class="eyebrow">The idea underneath</span><h1>Code and <em>intelligence</em></h1>
<p class="lede">What it means to compute, where computation stops, and what changes now that programs can be found by training instead of written by hand.</p></div><div class="prose wide">{t}</div></div>''')
    shell("/intelligence/", "Code and intelligence: computation, its limits, and learned programs | Renaissance Labs Code", "What can be computed and what cannot, why simple programs resist prediction, how proofs and programs are the same thing, and what changes when programs are learned.", body, "intelligence", og="intelligence", extra_foot=FIG_JS)

# ---------------------------------------------------------------- exports and files
def exports():
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    clean = [{k: v for k, v in r.items() if not k.startswith("_")} for r in RES]
    json.dump({"generated": CHECKED, "site": SITE, "count": len(clean), "resources": clean}, open(os.path.join(OUT, "data/resources.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump(TAX, open(os.path.join(OUT, "data/taxonomy.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump(list(SNIPS.values()), open(os.path.join(OUT, "data/snippets.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for name, obj in (("program", PROGRAM), ("stack", STACK), ("languages", LANGLIST), ("landmarks", LANDMARKS), ("world", WORLD)):
        json.dump(obj, open(os.path.join(OUT, "data/%s.json" % name), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if RECIPES: json.dump(RECIPES, open(os.path.join(OUT, "data/recipes.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    buf = io.StringIO(); w = csv.writer(buf)
    cols = ["id", "name", "kind", "url", "license", "license_family", "size", "stages", "languages", "program_forms", "stack_levels", "tasks", "difficulty", "released", "checked", "summary", "caveats"]
    w.writerow(cols)
    for r in clean:
        w.writerow([r["id"], r["name"], r["kind"], r["url"], r["license"] or "", r["lic_class"], r["size"] or "", ";".join(r["stages"]), ";".join(r["langs"] or r["languages"]), ";".join(r["layers"]), ";".join(r["levels"]), ";".join(r["tasks"]), r["difficulty"] or "", r["released"] or "", r["checked"], r["summary"], r["caveats"] or ""])
    open(os.path.join(OUT, "data/resources.csv"), "w", encoding="utf-8", newline="").write(buf.getvalue())

def llms():
    L = ["# Renaissance Labs Code", "", "> What code is, mapped: the eight forms a program takes, the nine levels of the stack from transistors to trained models, %d programming languages, sourced facts about the software the world runs on, and %d verified resources for training models to write code. Every fact and entry was checked against its source on the date shown. Machine-readable data: %s/data/" % (len(LANGLIST), len(RES), SITE), "",
         "## What a program is"]
    for d in PROGRAM: L.append("- [%s](%s/program/%s/): %s" % (d["full"], SITE, d["id"], strip_md(d["short"])))
    L += ["", "## The stack (top to bottom)"]
    for d in STACK: L.append("- [%s](%s/stack/%s/): %s (%d resources)" % (d["full"], SITE, d["id"], strip_md(d["short"]), len(in_level(d["id"]))))
    L += ["", "## Languages", "- [Language map](%s/languages/)" % SITE]
    for l in sorted(LANGLIST, key=lambda x: x["name"].lower()): L.append("- [%s](%s/languages/%s/): %d, %s family. %s" % (l["name"], SITE, l["id"], l["year"], FAM[l["family"]][1].lower(), strip_md(first_para(l["what"]))))
    L += ["", "## More", "- [Code in the world](%s/world/): sourced facts, failures, and why software is never finished" % SITE, "- [Code and intelligence](%s/intelligence/): computation, its limits, and learned programs" % SITE,
          "- [Train](%s/train/): the practical section" % SITE, "- [Catalog](%s/catalog/): all %d resources, filterable" % (SITE, len(RES)), "- [Recipe builder](%s/recipe/): ordered plan from model size, budget, languages and goal" % SITE, "- [Guide: how to improve any model at coding](%s/guide/)" % SITE, "- [Pitfalls](%s/pitfalls/)" % SITE, "- [About and method](%s/about/)" % SITE, "", "## Training stages"]
    for s in STAGES: L.append("- [%s](%s/stage/%s/): %s (%d resources)" % (s["title"], SITE, s["id"], s["tagline"], stage_count(s["id"])))
    L += ["", "## Data"] + ["- [%s](%s/data/%s)" % (f, SITE, f) for f in ("resources.json", "resources.csv", "program.json", "stack.json", "languages.json", "landmarks.json", "world.json", "taxonomy.json", "snippets.json")] + ["", "## Resources"]
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
    shutil.copy(os.path.join(ROOT, "site_lang.js"), os.path.join(OUT, "lang.js")); shutil.copy(os.path.join(ROOT, "site_figs.js"), os.path.join(OUT, "figs.js"))
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
    shell("/404/", "Not found | Renaissance Labs Code", "Page not found.", wrap('<div class="page"><div class="page-head"><span class="eyebrow">404</span><h1>That page is not on the map.</h1><p class="lede"><a href="/catalog/" style="color:var(--accent)">Browse the catalog</a> or <a href="/" style="color:var(--accent)">go home</a>.</p></div></div>'))
    h = PAGES_OUT.pop("/404/"); SITEMAP.pop(); return h

def main():
    page_home(); page_program_index(); page_stack_index(); page_languages(); page_world(); page_intelligence(); page_train(); page_catalog()
    for d in PROGRAM: page_node("program", d)
    for d in STACK: page_node("stack", d)
    for l in LANGLIST: page_language(l)
    for s in STAGES: page_stage(s)
    for r in RES: page_resource(r)
    page_recipe()
    for name, path, title, desc, eb, h1, lede, cur in LONG:
        if os.path.exists(os.path.join(ROOT, "data/pages", name + ".html")): page_long(name, path, title, desc, eb, h1, lede, cur, name)
    exports(); llms(); write_all()
    print("built %d pages, %d resources, %d languages, %d snippets" % (len(PAGES_OUT), len(RES), len(LANGLIST), len(SNIPS)))

LONG = [
    ("guide", "/guide/", "How to improve any model at coding: a guide | Renaissance Labs Code", "Measure first, fix data, SFT, then verifiable-reward RL, then re-measure. The honest short version, with caveats.", "Guide", "How to improve <em>any</em> model at coding", "The short version: measure, fix the data, teach the format, reward what passes, measure again.", "guide"),
    ("pitfalls", "/pitfalls/", "Pitfalls when training coding models | Renaissance Labs Code", "Contamination, reward hacking, weak tests, license traps and unsafe code execution: what goes wrong and how to avoid it.", "Pitfalls", "What goes wrong, and how to <em>see</em> it coming", "Most failed runs fail for the same few reasons.", "pitfalls"),
    ("about", "/about/", "About and method | Renaissance Labs Code", "How this catalog was built and verified, what it does not cover, and how to contribute a correction.", "About", "About this <em>site</em>", "How the maps were made, how every fact and entry was verified, what is missing, and how to correct us.", "about"),
]

if __name__ == "__main__":
    main()
