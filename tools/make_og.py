#!/usr/bin/env python3
"""Generate social preview images (1200 x 630 JPEG) into docs/assets/og/.

  python3 tools/make_og.py              # all pages
  python3 tools/make_og.py home recipe  # only these names

Names: home, program, stack, languages, world, intelligence, train, catalog, recipe, guide, pitfalls, about,
       p-<form id>, s-<level id>, l-<language id>, stage-<id>, r-<resource id>.
Each image is HTML rendered by headless Chrome (tools/render_og.mjs). The pipeline graphic is the real
stage list with real counts; resource images carry the entry's license and size as stated in the data.
"""
import html, json, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, ROOT)
import build as B
e = html.escape
OUT = os.path.join(ROOT, "docs", "assets", "og")
FONTS = os.path.join(ROOT, "docs", "assets", "fonts")
GOLD = "#e0b657"; GREEN = "#5fcfa6"
HUE = {"pretrain": "#d89a5a", "sft": "#7fb0d4", "preference": "#c08fb8", "rl": "#5fcfa6", "eval": "#e8837c", "tooling": "#bdb862"}

CSS = """
@font-face{font-family:'Fraunces';font-style:normal;font-weight:100 900;src:url('file://%(f)s/fraunces-latin-opsz-normal.woff2') format('woff2')}
@font-face{font-family:'Fraunces';font-style:italic;font-weight:100 900;src:url('file://%(f)s/fraunces-latin-opsz-italic.woff2') format('woff2')}
*{box-sizing:border-box;margin:0}
html,body{width:1200px;height:630px;overflow:hidden}
body{position:relative;background:radial-gradient(60%% 80%% at 85%% 0%%,rgba(60,170,135,.26),transparent 62%%),radial-gradient(55%% 70%% at 0%% 100%%,rgba(194,149,53,.16),transparent 62%%),linear-gradient(135deg,#0b0c0b,#121311 55%%,#181a17);
 color:#efece3;font-family:-apple-system,'Helvetica Neue',Arial,sans-serif}
.brand{position:absolute;left:72px;top:58px;font:600 19px/1 ui-monospace,Menlo,monospace;letter-spacing:.2em;text-transform:uppercase;color:%(gold)s}
.brand i{font:italic 400 28px/1 'Fraunces',Georgia,serif;letter-spacing:0;text-transform:none;margin-left:10px;color:#f3d79b}
.h1{position:absolute;left:72px;top:140px;width:760px;font:400 80px/1.02 'Fraunces',Georgia,serif;letter-spacing:-.02em}
.h1 em{font-style:italic;color:%(green)s}
.sub{position:absolute;left:72px;top:372px;width:700px;font-size:27px;line-height:1.42;color:#c7c3b6}
.url{position:absolute;left:72px;bottom:34px;font:500 17px/1 ui-monospace,Menlo,monospace;color:#7f7b70;letter-spacing:.05em}
.rail{position:absolute;left:72px;right:72px;bottom:86px;display:flex;gap:8px}
.rail div{flex:1;height:78px;border-radius:10px;border:1px solid #2a2c27;background:#171915;position:relative;padding:14px 14px 0;font:600 15px/1 ui-monospace,Menlo,monospace;color:#b3afa3}
.rail div::before{content:'';position:absolute;left:0;right:0;top:0;height:5px;border-radius:10px 10px 0 0;background:var(--c)}
.rail b{display:block;font:400 30px/1 'Fraunces',Georgia,serif;color:#efece3;margin-top:10px}
.chips{position:absolute;left:72px;top:520px;display:flex;gap:10px}
.chip{font:500 20px/1 ui-monospace,Menlo,monospace;padding:10px 16px;border-radius:10px;border:1px solid #3a3d35;background:#171915;color:#d9d5c8}
.kind{position:absolute;left:72px;top:112px;font:600 17px/1 ui-monospace,Menlo,monospace;letter-spacing:.14em;text-transform:uppercase}
.bar6{position:absolute;right:0;top:0;bottom:0;width:26px;background:var(--c)}
""" % {"f": FONTS, "gold": GOLD, "green": GREEN}

def page(inner, color=None):
    c = color or GREEN
    return "<!doctype html><meta charset=utf-8><style>%s</style><body style='--c:%s'>%s</body>" % (CSS, c, inner)

BRAND = '<div class="brand">Renaissance Labs<i>Code</i></div>'
def rail():
    return '<div class="rail">%s</div>' % "".join('<div style="--c:%s">%s<b>%d</b></div>' % (HUE[s["id"]], e(s["short"]), B.stage_count(s["id"])) for s in B.STAGES)

def simple(title_html, sub, url, with_rail=True, color=None):
    return page(BRAND + '<div class="h1">%s</div><div class="sub">%s</div>%s<div class="url">%s</div>' % (title_html, e(sub), rail() if with_rail else "", e(url)), color)

LV = {"physics": "#e08a6e", "gates": "#d89a5a", "machine": "#cdbb5c", "os": "#a3c070", "compilers": "#6fcfa0", "languages": "#5fcfa6", "apps": "#74bcd4", "networks": "#93a6e6", "learned": "#c79ad0"}
def stackart(cur=None):
    """The nine levels as a small tower on the right. `cur` is a set of level ids to light up (all lit when None)."""
    rows = "".join('<div style="height:44px;margin-bottom:6px;border-radius:8px;border:1px solid #2a2c27;border-left:7px solid %s;background:%s;padding:12px 14px;font:600 17px/1 ui-monospace,Menlo,monospace;color:%s;opacity:%s">%s</div>' % (
        LV[d["id"]], "#1c1f1a" if (cur is None or d["id"] in cur) else "#141613", "#efece3" if (cur is None or d["id"] in cur) else "#7f7b70", "1" if (cur is None or d["id"] in cur) else ".5", e(d["title"])) for d in B.STACK)
    return '<div style="position:absolute;right:64px;top:96px;width:270px">%s</div>' % rows
def formsart(cur=None):
    rows = "".join('<div style="height:50px;margin-bottom:6px;border-radius:8px;border:1px solid %s;background:#171915;padding:15px 14px;font:600 17px/1 ui-monospace,Menlo,monospace;color:%s"><span style="color:#5fcfa6;margin-right:12px">%s</span>%s</div>' % (
        "#5fcfa6" if d["id"] == cur else "#2a2c27", "#efece3" if (cur is None or d["id"] == cur) else "#8f8b80", d["n"], e(d["title"])) for d in B.PROGRAM)
    return '<div style="position:absolute;right:64px;top:92px;width:270px">%s</div>' % rows
def art(title_html, sub, url, forms=False, cur=None, color=None):
    side = formsart(cur) if forms else stackart({cur} if cur else None)
    big = "74px" if len(title_html) < 48 else "58px"
    return page(BRAND + '<div class="h1" style="width:760px;font-size:%s">%s</div><div class="sub" style="width:740px;top:400px;font-size:25px">%s</div>%s<div class="url">%s</div>' % (big, title_html, e(sub), side, e(url)), color)

def jobs(only):
    J = []
    def add(name, html_): 
        if not only or name in only: J.append({"name": name, "html": html_})
    n = len(B.RES)
    add("home", art("Code is thought that <em>runs</em>.", "What a program is, the stack from transistors to trained models, %d languages, and %d verified resources for training models to write code." % (len(B.LANGLIST), n), "code.renaissancelabs.eu"))
    add("program", art("What a program <em>is</em>", "One program, eight forms: text, tokens, tree, types, execution, tests, proof, change.", "code.renaissancelabs.eu/program", forms=True))
    add("stack", art("The stack: from <em>sand</em> to trained models", "Nine levels, each built entirely from the one below.", "code.renaissancelabs.eu/stack"))
    add("languages", art("%d languages, placed on the <em>stack</em>" % len(B.LANGLIST), "Where each sits between machine and person, the same program in each, and what exists to train on it.", "code.renaissancelabs.eu/languages"))
    add("world", art("What the world <em>runs on</em>", "Sourced facts about the code under payments, aircraft, medicine and the internet.", "code.renaissancelabs.eu/world"))
    add("intelligence", art("Code and <em>intelligence</em>", "What can be computed, what cannot, and what changes when programs are learned.", "code.renaissancelabs.eu/intelligence"))
    add("train", simple("Teaching a model to <em>write</em> code", "%d verified datasets, benchmarks, environments and tools. A recipe builder. An honest guide." % n, "code.renaissancelabs.eu/train"))
    add("catalog", simple("%d resources, <em>checked</em> at the source" % n, "License, size, caveats and date checked for every entry.", "code.renaissancelabs.eu/catalog"))
    add("recipe", simple("Tell us what you have. Get an <em>ordered plan</em>.", "Model size, compute, languages and goal in. Datasets, evals, verifiers and pitfalls out.", "code.renaissancelabs.eu/recipe"))
    add("guide", simple("How to improve <em>any</em> model at coding", "Measure, fix the data, SFT, reward what passes, measure again.", "code.renaissancelabs.eu/guide"))
    add("pitfalls", simple("What goes wrong, and how to <em>see</em> it coming", "Contamination, reward hacking, weak tests, license traps.", "code.renaissancelabs.eu/pitfalls"))
    add("about", simple("About this <em>site</em>", "How the maps were made and how every fact was verified.", "code.renaissancelabs.eu/about", False))
    for d in B.PROGRAM:
        add("p-" + d["id"], art(e(d["full"]), d["question"], "code.renaissancelabs.eu/program/" + d["id"], forms=True, cur=d["id"]))
    for d in B.STACK:
        add("s-" + d["id"], art(e(d["full"]), d["question"], "code.renaissancelabs.eu/stack/" + d["id"], cur=d["id"], color=LV[d["id"]]))
    for l in B.LANGLIST:
        w = B.strip_md(B.first_para(l["what"])); w = w if len(w) < 170 else w[:167].rsplit(" ", 1)[0] + "..."
        add("l-" + l["id"], page(BRAND + '<div class="kind" style="color:%s">%s language &middot; %d</div><div class="h1" style="top:160px;font-size:%s">%s</div><div class="sub" style="top:%s;font-size:25px;width:760px">%s</div>%s<div class="url">code.renaissancelabs.eu/languages/%s</div>' % (
            GOLD, e(B.FAM[l["family"]][1]), l["year"], "96px" if len(l["name"]) < 14 else "68px", e(l["name"]), "300px", e(w), stackart(set(l["levels"])), e(l["id"]))))
    for s in B.STAGES:
        add("stage-" + s["id"], simple(e(s["title"]), s["tagline"], "code.renaissancelabs.eu/stage/" + s["id"], True, HUE[s["id"]]))
    for r in B.RES:
        c = HUE[r["primary"]]
        nm = r["name"]; size = "72px" if len(nm) < 24 else ("58px" if len(nm) < 40 else "46px")
        chips = "".join('<span class="chip" style="border-color:%s;color:%s">%s</span>' % (HUE[s], HUE[s], e(B.STAGE[s]["short"])) for s in r["stages"][:4])
        lic = B.short_lic(r)
        extra = '<span class="chip">%s</span>' % e(lic) + ('<span class="chip">%s</span>' % e(B.short_size(r)) if B.short_size(r) else "")
        sub = r["summary"]; sub = sub if len(sub) < 150 else sub[:147].rsplit(" ", 1)[0] + "..."
        add("r-" + r["id"], page(BRAND + '<div class="kind" style="color:%s">%s</div><div class="h1" style="top:160px;font-size:%s">%s</div><div class="sub" style="top:340px;font-size:25px;width:900px">%s</div><div class="chips" style="top:520px">%s%s</div><div class="url" style="right:72px;left:auto">code.renaissancelabs.eu</div><div class="bar6"></div>' % (c, e(B.KINDS[r["kind"]]), size, e(nm), e(sub), chips, extra), c))
    return J

if __name__ == "__main__":
    J = jobs(set(sys.argv[1:]))
    f = os.path.join(tempfile.mkdtemp(), "jobs.json"); json.dump(J, open(f, "w"))
    os.makedirs(OUT, exist_ok=True)
    subprocess.run(["node", os.path.join(ROOT, "tools/render_og.mjs"), f, OUT], check=True, cwd=ROOT)
