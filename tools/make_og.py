#!/usr/bin/env python3
"""Generate social preview images (1200 x 630 JPEG) into docs/assets/og/.

  python3 tools/make_og.py              # all pages
  python3 tools/make_og.py home recipe  # only these names

Names: home, catalog, recipe, guide, pitfalls, about, stage-<id>, r-<resource id>.
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

def jobs(only):
    J = []
    def add(name, html_): 
        if not only or name in only: J.append({"name": name, "html": html_})
    n = len(B.RES)
    add("home", simple("Train a model that <em>actually</em> codes.", "%d verified datasets, environments, benchmarks and tools. A recipe builder. An honest guide." % n, "code.renaissancelabs.eu"))
    add("catalog", simple("%d resources, <em>checked</em> at the source" % n, "License, size, caveats and date checked for every entry.", "code.renaissancelabs.eu/catalog"))
    add("recipe", simple("Tell us what you have. Get an <em>ordered plan</em>.", "Model size, compute, languages and goal in. Datasets, evals, verifiers and pitfalls out.", "code.renaissancelabs.eu/recipe"))
    add("guide", simple("How to improve <em>any</em> model at coding", "Measure, fix the data, SFT, reward what passes, measure again.", "code.renaissancelabs.eu/guide"))
    add("pitfalls", simple("What goes wrong, and how to <em>see</em> it coming", "Contamination, reward hacking, weak tests, license traps.", "code.renaissancelabs.eu/pitfalls"))
    add("about", simple("About this <em>catalog</em>", "How entries were verified, and what is missing.", "code.renaissancelabs.eu/about"))
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
