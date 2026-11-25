#!/usr/bin/env python3
"""Remove train examples that share a token 13-gram with any evaluation example.

Usage: decontaminate.py --eval eval_probe.jsonl --input data/split.jsonl --output data/split_decon.jsonl --report out/logs/decontamination.json

Only the train split is filtered (a file is dropped whole if any of its 13-grams matches). Validation and
test files are reported but kept, because they are never trained on. Eval text = every string value in each eval record
except the 'id' and 'note' fields.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

N = 13
SKIP_FIELDS = {"id", "note"}


def ngrams(toks, n=N):
    return zip(*[toks[i:] for i in range(n)])


def eval_index(eval_path, n=N):
    """{13-gram tuple: eval id of the first record that contains it}"""
    idx = {}
    for rec in common.read_jsonl(eval_path):
        text = "\n".join(str(v) for k, v in sorted(rec.items()) if k not in SKIP_FIELDS and isinstance(v, str))
        for g in ngrams(common.tokens(text), n):
            idx.setdefault(g, rec["id"])
    return idx


def overlap(text, idx, n=N):
    """Return (count of overlapping 13-grams, sorted eval ids matched, example gram as a string or None)."""
    hits = 0
    ids = set()
    example = None
    for g in ngrams(common.tokens(text), n):
        if g in idx:
            hits += 1
            ids.add(idx[g])
            if example is None:
                example = " ".join(g)
    return hits, sorted(ids), example


def main():
    common.cap_memory()
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--n", type=int, default=N)
    a = ap.parse_args()
    idx = eval_index(a.eval, a.n)
    n_eval = len({v for v in idx.values()})
    kept, removed, informational, per_split_in, per_split_out = [], [], [], {}, {}
    for rec in common.read_jsonl(a.input):
        per_split_in[rec["split"]] = per_split_in.get(rec["split"], 0) + 1
        hits, ids, ex = overlap(rec["content"], idx, a.n)
        if hits and rec["split"] == "train":
            removed.append({"path": rec["path"], "overlapping_ngrams": hits, "eval_ids": ids, "example_ngram": ex})
            continue
        if hits:
            informational.append({"path": rec["path"], "split": rec["split"], "overlapping_ngrams": hits, "eval_ids": ids})
        per_split_out[rec["split"]] = per_split_out.get(rec["split"], 0) + 1
        kept.append(rec)
    common.write_jsonl(a.output, kept)
    report = {"stage": "decontaminate", "ngram_tokens": a.n, "eval_file": os.path.basename(a.eval), "eval_ngrams_indexed": len(idx),
              "eval_ids_with_ngrams": sorted(set(idx.values())), "files_in_by_split": per_split_in, "files_out_by_split": per_split_out,
              "train_files_removed": len(removed), "removed": removed, "overlap_in_validation_or_test_kept": informational}
    os.makedirs(os.path.dirname(a.report), exist_ok=True)
    with open(a.report, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, sort_keys=True, indent=2)
        f.write("\n")
    print("eval 13-grams indexed: %d | train files removed: %d" % (len(idx), len(removed)))
    for r in removed:
        print("  removed %s: %d overlapping 13-grams with %s" % (r["path"], r["overlapping_ngrams"], r["eval_ids"]))
    for r in informational:
        print("  note: %s file %s overlaps %s (kept)" % (r["split"], r["path"], r["eval_ids"]))


if __name__ == "__main__":
    main()
