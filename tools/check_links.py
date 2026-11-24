#!/usr/bin/env python3
"""Check every external link in the data files resolves (HTTP < 400).  python3 tools/check_links.py [--out file]
HEAD first, then a ranged GET if the server refuses HEAD. 8 threads, 20 s timeout. Writes docs-independent report to notes/link-report.json."""
import json, os, re, sys, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
urls = {}
rd = os.path.join(ROOT, "data/resources")
for fn in sorted(os.listdir(rd)):
    if fn.endswith(".json"):
        for r in json.load(open(os.path.join(rd, fn), encoding="utf-8")):
            urls.setdefault(r["url"], []).append(r["id"])
            for l in r.get("extra_links") or []: urls.setdefault(l["url"], []).append(r["id"])
for p in ("data/snippets.json",):
    fp = os.path.join(ROOT, p)
    if os.path.exists(fp):
        for s in json.load(open(fp, encoding="utf-8")):
            for u in s.get("source_urls", []): urls.setdefault(u, []).append("snippet:" + s["id"])
for fn in os.listdir(os.path.join(ROOT, "data/pages")) if os.path.isdir(os.path.join(ROOT, "data/pages")) else []:
    for u in re.findall(r'href="(https?://[^"]+)"', open(os.path.join(ROOT, "data/pages", fn), encoding="utf-8").read()): urls.setdefault(u, []).append("page:" + fn)
UA = {"User-Agent": "Mozilla/5.0 (compatible; link-check)"}
HF = threading.Semaphore(2)
def hf_api(u):
    m = re.match(r"https://huggingface\.co/(datasets|models|spaces)/([^/]+/[^/#?]+|[^/#?]+)(/.*)?$", u)
    return "https://huggingface.co/api/%s/%s" % (m.group(1), m.group(2)) if m and not u.startswith("https://huggingface.co/docs") else u
def once(u, method):
    req = urllib.request.Request(u, method=method, headers=dict(UA, **({"Range": "bytes=0-512"} if method == "GET" else {})))
    with urllib.request.urlopen(req, timeout=25) as r: return r.status
def check(u):
    target = hf_api(u); is_hf = "huggingface.co" in u
    last = "?"
    for attempt in range(5):
        try:
            if is_hf:
                with HF:
                    time.sleep(0.4); return u, once(target, "GET")
            return u, once(target, "HEAD")
        except urllib.error.HTTPError as ex:
            last = ex.code
            if ex.code in (429, 502, 503, 504): time.sleep(2 + attempt * 4); continue
            if not is_hf and ex.code in (403, 405, 400):
                try: return u, once(target, "GET")
                except urllib.error.HTTPError as e2: last = e2.code
                except Exception as e2: last = str(e2)[:80]
            return u, last
        except Exception as ex:
            last = str(ex)[:80]; time.sleep(1)
    return u, last
with ThreadPoolExecutor(8) as ex: res = list(ex.map(check, urls))
bad = [(u, s) for u, s in res if not (isinstance(s, int) and s < 400)]
json.dump({"checked": len(res), "bad": [{"url": u, "status": s, "used_by": urls[u]} for u, s in bad]}, open(os.path.join(ROOT, "notes/link-report.json"), "w"), indent=1)
print("checked %d urls, %d bad" % (len(res), len(bad)))
for u, s in bad: print(" ", s, u, urls[u][:3])
sys.exit(1 if bad else 0)
