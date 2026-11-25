"""Build the SFT, validation and held-out sets from nvidia/OpenCodeInstruct (CC-BY-4.0).

Run once. Streams the dataset (no full download), keeps only rows that pass strict filters,
removes overlap with HumanEval and MBPP, splits by a hash of the row id, and writes JSONL files:

  data/oci-sft-4k/train.jsonl        prompt/completion rows for TRL (conversational prompt-completion)
  data/oci-sft-4k/*_ids.txt          row ids of each split, same order
  data/oci-sft-4k/validation.jsonl   same format, used only for eval loss
  data/oci-heldout/heldout.jsonl     question, tests and reference solution, never trained on
  data/oci-rl-pool/pool.jsonl        optional pool for the stretch GRPO recipe (--rl-pool N)
  data/manifest.json                 counts, dataset revision, filter rule, seed

Usage:  python prepare_data.py --out data
"""
import argparse
import hashlib
import json
import random
import re
from pathlib import Path

DATASET = "nvidia/OpenCodeInstruct"
# Commit of the dataset repo read from the Hugging Face API on 2026-11-25.
REVISION = "8f3ba5bafe4d6e8db46082cf7ae6741bc370604d"
SEED = 42

# Programs that need the network, a terminal or the filesystem make unit tests flaky; drop them.
BAD_CODE = re.compile(
    r"\binput\s*\(|\brequests\b|\burllib\b|\bsocket\b|\bsubprocess\b|os\.system|\bopen\s*\(|"
    r"\bsleep\s*\(|random\.|datetime\.now|time\.time"
)
CODE_BLOCK = re.compile(r"```python\n(.*?)```", re.S)


def words(text):
    return re.findall(r"\w+", text.lower())


def ngrams(text, n):
    w = words(text)
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def judged_all_five(raw):
    """llm_judgement is a JSON string with three criteria, each {score, justification}."""
    try:
        j = json.loads(raw)
        return len(j) >= 3 and all(v.get("score") == 5 for v in j.values())
    except Exception:
        return False


def keep(row):
    """Filter rule. Returns the parsed tests list or None.

    1. all generated unit tests passed on the reference solution (average_test_score == 1)
    2. every entry of tests_execution_status is "pass" and there are at least 5 tests
    3. the LLM judge gave 5 out of 5 on all three criteria (OpenCodeInstruct paper, Table 4)
    4. the response has a ```python block, and the code passes the BAD_CODE screen
    5. question plus answer is at most 6000 characters (fits max_length 2048 tokens)
    """
    try:
        if float(row["average_test_score"]) != 1.0:
            return None
        tests = json.loads(row["unit_tests"])
        status = json.loads(row["tests_execution_status"])
    except Exception:
        return None
    if len(tests) < 5 or len(status) != len(tests) or any(s != "pass" for s in status):
        return None
    if not judged_all_five(row["llm_judgement"]):
        return None
    m = CODE_BLOCK.search(row["output"])
    if not m or BAD_CODE.search(m.group(1)):
        return None
    if len(row["input"]) + len(row["output"]) > 6000:
        return None
    return tests


def benchmark_ngrams(n=10):
    """Own decontamination on top of the dataset's: 10-word grams of HumanEval and MBPP."""
    from datasets import load_dataset

    grams = set()
    for r in load_dataset("openai/openai_humaneval", split="test"):
        grams |= ngrams(r["prompt"] + "\n" + r["canonical_solution"], n)
    mbpp = load_dataset("google-research-datasets/mbpp", "full")
    for split in mbpp:
        for r in mbpp[split]:
            grams |= ngrams(r["text"] + "\n" + r["code"], n)
    return grams


def bucket(row_id):
    return int(hashlib.md5(row_id.encode()).hexdigest(), 16) % 10_000


def jaccard(a, b):
    return len(a & b) / max(1, len(a | b))


def main():
    from datasets import load_dataset

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data")
    ap.add_argument("--n-train", type=int, default=4000)
    ap.add_argument("--n-val", type=int, default=200)
    ap.add_argument("--n-heldout", type=int, default=300)
    ap.add_argument("--rl-pool", type=int, default=0, help="extra rows for the stretch recipe")
    ap.add_argument("--max-scan", type=int, default=400_000, help="stop after this many streamed rows")
    a = ap.parse_args()

    want = a.n_train + a.n_val + a.n_heldout + a.rl_pool
    bench = benchmark_ngrams()
    stream = load_dataset(DATASET, split="train", streaming=True, revision=REVISION)
    # shuffle() reorders the shards and uses a buffer over up to 10 shards at a time (datasets docs),
    # which mixes the "generic" and "algorithmic" domains that are stored in separate blocks.
    stream = stream.shuffle(seed=SEED, buffer_size=20_000)

    kept, seen_inputs, scanned = [], set(), 0
    stats = {"scanned": 0, "filtered_out": 0, "contaminated": 0, "duplicate": 0}
    for row in stream:
        scanned += 1
        if scanned > a.max_scan or len(kept) >= want:
            break
        tests = keep(row)
        if tests is None:
            stats["filtered_out"] += 1
            continue
        key = re.sub(r"\s+", " ", row["input"].strip().lower())
        if key in seen_inputs:
            stats["duplicate"] += 1
            continue
        if ngrams(row["input"] + "\n" + row["output"], 10) & bench:
            stats["contaminated"] += 1
            continue
        seen_inputs.add(key)
        kept.append({"id": row["id"], "input": row["input"], "output": row["output"],
                     "domain": row["domain"], "tests": tests})
    stats["scanned"] = scanned
    print("kept", len(kept), stats)

    # Deterministic split by hash of id: first held-out, then validation, then train, then RL pool.
    kept.sort(key=lambda r: bucket(r["id"]))
    heldout = kept[:a.n_heldout]
    val = kept[a.n_heldout:a.n_heldout + a.n_val]
    train = kept[a.n_heldout + a.n_val:a.n_heldout + a.n_val + a.n_train]
    pool = kept[a.n_heldout + a.n_val + a.n_train:]

    # Leakage guard: instructions in this dataset are evolved from shared seeds, so drop held-out and
    # validation rows whose 5-word shingles overlap a training row (Jaccard > 0.5).
    train_sh = [ngrams(r["input"], 5) for r in train]

    def clean(rows):
        out = []
        for r in rows:
            sh = ngrams(r["input"], 5)
            if all(jaccard(sh, t) <= 0.5 for t in train_sh):
                out.append(r)
        return out

    heldout_c, val_c = clean(heldout), clean(val)
    print("near-duplicates dropped: heldout", len(heldout) - len(heldout_c), "val", len(val) - len(val_c))

    out = Path(a.out)
    for d in ("oci-sft-4k", "oci-heldout", "oci-rl-pool"):
        (out / d).mkdir(parents=True, exist_ok=True)

    def write(path, rows):
        with open(path, "w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    def sft(r):
        return {"prompt": [{"role": "user", "content": r["input"]}],
                "completion": [{"role": "assistant", "content": r["output"]}]}

    # ids live in separate files so the JSONL has only the columns TRL needs
    (out / "oci-sft-4k" / "train_ids.txt").write_text("\n".join(r["id"] for r in train))
    (out / "oci-sft-4k" / "validation_ids.txt").write_text("\n".join(r["id"] for r in val_c))
    write(out / "oci-sft-4k" / "train.jsonl", [sft(r) for r in train])
    write(out / "oci-sft-4k" / "validation.jsonl", [sft(r) for r in val_c])
    write(out / "oci-heldout" / "heldout.jsonl",
          [{"id": r["id"], "input": r["input"], "tests": r["tests"], "reference_output": r["output"]}
           for r in heldout_c])
    if pool:
        rng = random.Random(SEED)
        rows = []
        for r in pool:
            t = list(r["tests"])
            rng.shuffle(t)  # 6 tests drive the reward, the rest stay hidden to detect reward hacking
            rows.append({"id": r["id"], "prompt": [{"role": "user", "content": r["input"]}],
                         "reward_tests": t[:6], "holdout_tests": t[6:]})
        write(out / "oci-rl-pool" / "pool.jsonl", rows)

    manifest = {"dataset": DATASET, "revision": REVISION, "seed": SEED, "stats": stats,
                "counts": {"train": len(train), "validation": len(val_c),
                           "heldout": len(heldout_c), "rl_pool": len(pool) if pool else 0},
                "filter": keep.__doc__}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
