"""Held-out execution eval, paired comparison, and a small sanity prompt set.

  python eval_heldout.py generate --model Qwen/Qwen2.5-Coder-1.5B-Instruct --data data/oci-heldout/heldout.jsonl --out runs/base_gen.jsonl
  python eval_heldout.py generate --model out/merged --data data/oci-heldout/heldout.jsonl --out runs/tuned_gen.jsonl
  python eval_heldout.py reference --data data/oci-heldout/heldout.jsonl --out runs/ref_gen.jsonl   # sandbox self-check
  python eval_heldout.py score --gen runs/base_gen.jsonl --data data/oci-heldout/heldout.jsonl --out runs/base_score.jsonl
  python eval_heldout.py compare --a runs/base_score.jsonl --b runs/tuned_score.jsonl
  python eval_heldout.py sanity --model out/merged --out runs/tuned_sanity.json

`score` runs generated code in Docker (flags from data/snippets.json, docker-hardened-sandbox) unless --no-docker,
which falls back to a plain subprocess with rlimits and is NOT a security sandbox.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from math import comb

MAX_NEW_TOKENS = 1024

RUNNER = r'''
import json, sys
case = json.load(open(sys.argv[1]))
marker = sys.argv[2]
ns = {"__name__": "solution"}
loaded = True
try:
    exec(compile(case["code"], "<solution>", "exec"), ns)
except BaseException:
    loaded = False
res = []
for t in case["tests"]:
    if not loaded:
        res.append(False)
        continue
    try:
        exec(compile(t, "<test>", "exec"), ns)
        res.append(True)
    except BaseException:
        res.append(False)
print(marker + json.dumps(res))
'''


def extract_code(text):
    blocks = re.findall(r"```(?:python|py)?[ \t]*\n(.*?)```", text, re.S)
    return blocks[0] if blocks else text


def read_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_model(name):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    dtype = torch.bfloat16 if dev == "cuda" else torch.float32
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(name, dtype=dtype).to(dev)
    model.eval()
    return tok, model, dev


def chat(tok, model, dev, user_text, max_new_tokens):
    import torch

    text = tok.apply_chat_template([{"role": "user", "content": user_text}], tokenize=False,
                                   add_generation_prompt=True)
    ids = tok([text], return_tensors="pt").to(dev)
    with torch.inference_mode():
        # Greedy. generation_config.json of the model (for Qwen: repetition_penalty 1.1) still applies,
        # so keep that file identical between the base and the merged model.
        out = model.generate(**ids, do_sample=False, max_new_tokens=max_new_tokens)
    new = out[0][ids["input_ids"].shape[1]:]
    finished = len(new) < max_new_tokens  # stopped on an end token instead of hitting the limit
    return tok.decode(new, skip_special_tokens=True), finished


def cmd_generate(a):
    tok, model, dev = load_model(a.model)
    rows = read_jsonl(a.data)
    out = []
    for i, r in enumerate(rows):
        text, finished = chat(tok, model, dev, r["input"], MAX_NEW_TOKENS)
        out.append({"id": r["id"], "output": text, "finished": finished})
        if i % 25 == 0:
            print(i, "/", len(rows), flush=True)
    write_jsonl(a.out, out)


def cmd_reference(a):
    rows = read_jsonl(a.data)
    write_jsonl(a.out, [{"id": r["id"], "output": r["reference_output"], "finished": True} for r in rows])


def run_case(code, tests, docker, timeout=30):
    marker = "RESULT-" + uuid.uuid4().hex + ":"
    with tempfile.TemporaryDirectory() as tmp:
        os.chmod(tmp, 0o755)
        with open(os.path.join(tmp, "runner.py"), "w") as f:
            f.write(RUNNER)
        with open(os.path.join(tmp, "case.json"), "w") as f:
            json.dump({"code": code, "tests": tests}, f)
        if docker:
            cmd = ["docker", "run", "--rm", "--network", "none", "--read-only", "--memory", "256m",
                   "--memory-swap", "256m", "--cpus", "1", "--pids-limit", "64", "--cap-drop", "ALL",
                   "--security-opt", "no-new-privileges", "--user", "65534:65534",
                   "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m", "-v", tmp + ":/work:ro", "-w", "/work",
                   "python:3.12-slim", "timeout", str(timeout - 5), "python", "-I", "runner.py",
                   "case.json", marker]
            kw = {}
        else:
            import resource

            def limits():
                os.setsid()
                resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
                resource.setrlimit(resource.RLIMIT_FSIZE, (1 << 20, 1 << 20))
            cmd = [sys.executable, "-I", "runner.py", "case.json", marker]
            kw = {"cwd": tmp, "preexec_fn": limits, "env": {"PATH": os.environ.get("PATH", "")}}
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, **kw)
        except subprocess.TimeoutExpired:
            return [False] * len(tests)
        for line in reversed(p.stdout.splitlines()):
            if line.startswith(marker):
                return json.loads(line[len(marker):])
        return [False] * len(tests)


def cmd_score(a):
    data = {r["id"]: r for r in read_jsonl(a.data)}
    gens = read_jsonl(a.gen)
    rows = []
    for g in gens:
        r = data[g["id"]]
        res = run_case(extract_code(g["output"]), r["tests"], docker=not a.no_docker)
        rows.append({"id": g["id"], "all_pass": all(res), "frac": sum(res) / len(res),
                     "finished": g.get("finished", True)})
    write_jsonl(a.out, rows)
    n = len(rows)
    print(json.dumps({"n": n, "strict_pass@1": sum(r["all_pass"] for r in rows) / n,
                      "mean_test_pass": sum(r["frac"] for r in rows) / n,
                      "unfinished": sum(not r["finished"] for r in rows)}, indent=2))


def cmd_compare(a):
    A = {r["id"]: r["all_pass"] for r in read_jsonl(a.a)}
    B = {r["id"]: r["all_pass"] for r in read_jsonl(a.b)}
    ids = sorted(set(A) & set(B))
    b = sum(A[i] and not B[i] for i in ids)   # only the first run passes
    c = sum(B[i] and not A[i] for i in ids)   # only the second run passes
    n = b + c
    # exact two-sided McNemar test (binomial, p = 0.5) on the discordant pairs
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, k) for k in range(0, min(b, c) + 1)) / 2 ** n)
    print(json.dumps({"n": len(ids), "a_pass": sum(A[i] for i in ids) / len(ids),
                      "b_pass": sum(B[i] for i in ids) / len(ids), "only_a": b, "only_b": c,
                      "mcnemar_exact_p": p}, indent=2))


SANITY = [
    ("What is the capital of Sweden? Answer in one word.", r"(?i)stockholm"),
    ("Explain in one sentence what a hash map is.", r"(?i)\bkey"),
    ('Reply with valid JSON only: an object with keys "name" and "age" for a person named Ada aged 36.',
     "json"),
    ("Translate to French: Good morning", r"(?i)bonjour"),
    ("Write a SQL query that returns the 5 largest values of column price from table items.",
     r"(?is)select.*order\s+by.*desc.*limit\s+5"),
    ("Write a JavaScript function that reverses a string.", r"(?is)(function|=>).*reverse|split\(''\)"),
    ("What is 17 * 23? Answer with the number only.", r"\b391\b"),
    ("Explain in two sentences what a unit test is.", r"(?i)\btest"),
    ("Write a bash one-liner that counts the lines in file.txt.", r"wc\s+-l"),
    ("Fix the bug and show only the corrected function: def add(a, b): return a - b",
     r"a\s*\+\s*b"),
    ("Say hello and stop.", "short"),
    ("Write a Python function is_prime(n) and one sentence explaining it.", r"def\s+is_prime"),
]


def check(kind, text):
    if kind == "json":
        m = re.search(r"\{.*\}", text, re.S)
        try:
            d = json.loads(m.group(0))
            return "name" in d and "age" in d
        except Exception:
            return False
    if kind == "short":
        return 0 < len(text) < 300
    return re.search(kind, text) is not None


def cmd_sanity(a):
    tok, model, dev = load_model(a.model)
    results = []
    for prompt, kind in SANITY:
        text, finished = chat(tok, model, dev, prompt, 256)
        results.append({"prompt": prompt, "ok": check(kind, text), "finished": finished, "output": text})
    summary = {"passed": sum(r["ok"] for r in results), "total": len(results),
               "unfinished": sum(not r["finished"] for r in results)}
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2, ensure_ascii=False)
    print(summary)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--model", required=True)
    g.add_argument("--data", required=True)
    g.add_argument("--out", required=True)
    g.set_defaults(fn=cmd_generate)
    r = sub.add_parser("reference")
    r.add_argument("--data", required=True)
    r.add_argument("--out", required=True)
    r.set_defaults(fn=cmd_reference)
    s = sub.add_parser("score")
    s.add_argument("--gen", required=True)
    s.add_argument("--data", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--no-docker", action="store_true")
    s.set_defaults(fn=cmd_score)
    c = sub.add_parser("compare")
    c.add_argument("--a", required=True)
    c.add_argument("--b", required=True)
    c.set_defaults(fn=cmd_compare)
    t = sub.add_parser("sanity")
    t.add_argument("--model", required=True)
    t.add_argument("--out", required=True)
    t.set_defaults(fn=cmd_sanity)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
