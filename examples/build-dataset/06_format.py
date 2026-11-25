#!/usr/bin/env python3
"""Stage 6: write the two record types as JSONL under out/ (one file per split)."""
import ast
import math
import os
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

SPLITS = ["train", "validation", "test"]
DOC_MIN, DOC_MAX = 30, 1500          # docstring characters
BODY_MIN_LINES, BODY_MAX_LINES = 3, 60  # response lines (def line plus body without the docstring)


def estimate_tokens(text):
    return int(math.ceil(len(text) / 4.0))  # rough chars/4 rule of thumb, not a tokenizer count


def docstring_pairs(rec):
    """Yield (instruction, response, qualname) for each function with a usable docstring in rec['content']."""
    text = rec["content"]
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return
    lines = text.split("\n")

    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                yield child, prefix + child.name
                yield from walk(child, prefix + child.name + ".<locals>.")
            elif isinstance(child, ast.ClassDef):
                yield from walk(child, prefix + child.name + ".")

    for fn, qual in walk(tree, ""):
        doc = ast.get_docstring(fn)
        if not doc or not (DOC_MIN <= len(doc) <= DOC_MAX) or len(fn.body) < 2:
            continue
        first = fn.body[0]
        if first.lineno == fn.lineno:  # one-line def with docstring on the same line
            continue
        header = lines[fn.lineno - 1:first.lineno - 1]
        body = lines[first.end_lineno:fn.end_lineno]
        while body and not body[0].strip():
            body = body[1:]
        response = textwrap.dedent("\n".join(header + body))
        n_lines = len(response.split("\n"))
        if not (BODY_MIN_LINES <= n_lines <= BODY_MAX_LINES):
            continue
        sig = lines[fn.lineno - 1].strip()
        instruction = "Write the Python function below. Its docstring is:\n\n%s\n\nStart from this signature line: %s" % (doc, sig.rstrip(":") + ":")
        yield instruction, response, qual


def main():
    common.cap_memory()
    corpus = {s: [] for s in SPLITS}
    pairs = {s: [] for s in SPLITS}
    for rec in common.read_jsonl(os.path.join(common.DATA, "split_decon.jsonl")):
        cid = common.sha256_text(rec["source_version"] + "/" + rec["path"])[:16]
        corpus[rec["split"]].append({
            "id": cid, "repo": rec["repo"], "path": rec["path"], "language": "python", "license": rec["license"],
            "sha256": rec["sha256"], "content": rec["content"], "n_tokens_estimate": estimate_tokens(rec["content"]),
            "split": rec["split"], "source_version": rec["source_tree"] + "-" + rec["source_version"],
            "source_sha256": rec["source_sha256"]})
        for k, (ins, resp, qual) in enumerate(docstring_pairs(rec)):
            pairs[rec["split"]].append({
                "id": common.sha256_text(cid + ":" + qual + ":" + str(k))[:16], "instruction": ins, "response": resp,
                "source_id": cid, "license": rec["license"], "split": rec["split"], "qualname": qual})
    counts = {"code_corpus": {}, "docstring_pairs": {}}
    tokens_est = {}
    for s in SPLITS:
        corpus[s].sort(key=lambda r: r["path"])
        pairs[s].sort(key=lambda r: (r["source_id"], r["id"]))
        counts["code_corpus"][s] = common.write_jsonl(os.path.join(common.OUT, "code_corpus", s + ".jsonl"), corpus[s])
        counts["docstring_pairs"][s] = common.write_jsonl(os.path.join(common.OUT, "docstring_pairs", s + ".jsonl"), pairs[s])
        tokens_est[s] = sum(r["n_tokens_estimate"] for r in corpus[s])
    lic = {}
    for s in SPLITS:
        for r in corpus[s]:
            lic[r["license"]] = lic.get(r["license"], 0) + 1
    log = {"stage": "06_format", "counts": counts, "n_tokens_estimate_by_split": tokens_est,
           "docstring_filter": {"docstring_chars": [DOC_MIN, DOC_MAX], "response_lines": [BODY_MIN_LINES, BODY_MAX_LINES],
                                "requires": "function body has a statement besides the docstring; test pairing dropped (no top-level test dir)"},
           "license_counts_in_corpus": dict(sorted(lic.items()))}
    common.write_log("stage_06_format.json", log)
    print("code_corpus:", counts["code_corpus"], "| docstring_pairs:", counts["docstring_pairs"])
    print("estimated tokens:", tokens_est)


if __name__ == "__main__":
    main()
