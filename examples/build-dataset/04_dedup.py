#!/usr/bin/env python3
"""Stage 4: exact dedup by content hash, then near-dedup with MinHash (token 5-shingles) + banded LSH."""
import hashlib
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

SEED = 1337
NUM_PERM = 64
BANDS = 16          # 16 bands x 4 rows: P(candidate | J=0.8) = 1-(1-0.8**4)**16 > 0.999
ROWS = NUM_PERM // BANDS
SHINGLE = 5
THRESHOLD = 0.8
PRIME = (1 << 61) - 1
MASK64 = (1 << 64) - 1


def shingle_hashes(text):
    toks = common.tokens(text)
    if len(toks) < SHINGLE:
        toks = toks + [""] * (SHINGLE - len(toks))
    return {int.from_bytes(hashlib.blake2b(" ".join(toks[i:i + SHINGLE]).encode("utf-8"), digest_size=8).digest(), "big")
            for i in range(len(toks) - SHINGLE + 1)}


def make_perms(seed=SEED, n=NUM_PERM):
    rng = random.Random(seed)
    return [(rng.randrange(1, PRIME), rng.randrange(0, PRIME)) for _ in range(n)]


def minhash(hashes, perms):
    return tuple(min((a * h + b) % PRIME for h in hashes) for a, b in perms)


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a or b) else 1.0


def lsh_candidates(sigs):
    """sigs: {key: signature}. Returns sorted candidate pairs (key_a < key_b) sharing any band bucket."""
    pairs = set()
    for band in range(BANDS):
        buckets = {}
        for key in sorted(sigs):
            buckets.setdefault(sigs[key][band * ROWS:(band + 1) * ROWS], []).append(key)
        for members in buckets.values():
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    pairs.add((members[i], members[j]))
    return sorted(pairs)


def near_dup_clusters(items, threshold=THRESHOLD):
    """items: {key: text}. Returns (clusters, n_candidates). Clusters are lists of keys (size>1), sorted;
    pairs are confirmed by exact Jaccard on the shingle sets before they are merged (union-find)."""
    perms = make_perms()
    sigs = {k: minhash(shingle_hashes(t), perms) for k, t in items.items()}
    cands = lsh_candidates(sigs)
    parent = {k: k for k in items}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    confirmed = []
    for a, b in cands:
        j = jaccard(shingle_hashes(items[a]), shingle_hashes(items[b]))
        if j >= threshold:
            confirmed.append((a, b, j))
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
    groups = {}
    for k in items:
        groups.setdefault(find(k), []).append(k)
    return [sorted(g) for g in groups.values() if len(g) > 1], len(cands), confirmed


def main():
    common.cap_memory()
    recs = list(common.read_jsonl(os.path.join(common.DATA, "scrubbed.jsonl")))
    n_in = len(recs)
    recs.sort(key=lambda r: r["path"])
    seen = {}
    exact_removed = []
    survivors = []
    for r in recs:
        if r["sha256"] in seen:
            exact_removed.append({"path": r["path"], "duplicate_of": seen[r["sha256"]]})
        else:
            seen[r["sha256"]] = r["path"]
            survivors.append(r)
    items = {r["path"]: r["content"] for r in survivors}
    clusters, n_cand, confirmed = near_dup_clusters(items)
    removed = set()
    cluster_log = []
    for c in clusters:
        keep = c[0]  # lexicographically smallest path, deterministic
        removed.update(c[1:])
        js = [round(j, 3) for a, b, j in confirmed if a in c and b in c]
        cluster_log.append({"kept": keep, "removed": c[1:], "size": len(c), "pair_jaccard_min": min(js), "pair_jaccard_max": max(js)})
    final = [r for r in survivors if r["path"] not in removed]
    common.write_jsonl(os.path.join(common.DATA, "deduped.jsonl"), final)
    log = {"stage": "04_dedup", "files_in": n_in, "exact_duplicates_removed": len(exact_removed), "exact_duplicate_files": exact_removed,
           "after_exact": len(survivors),
           "minhash": {"seed": SEED, "num_perm": NUM_PERM, "bands": BANDS, "rows_per_band": ROWS, "shingle_tokens": SHINGLE, "jaccard_threshold": THRESHOLD,
                       "confirmation": "exact Jaccard on shingle sets for each LSH candidate pair"},
           "lsh_candidate_pairs": n_cand, "confirmed_pairs": len(confirmed), "near_duplicate_clusters": len(clusters),
           "near_duplicates_removed": len(removed), "clusters": sorted(cluster_log, key=lambda c: c["kept"]), "files_out": len(final)}
    common.write_log("stage_04_dedup.json", log)
    print("in", n_in, "| exact removed", len(exact_removed), "| LSH candidates", n_cand, "confirmed", len(confirmed),
          "| clusters", len(clusters), "near removed", len(removed), "| out", len(final))
    for c in cluster_log:
        print("  keep %s <- %s (J %.2f-%.2f)" % (c["kept"], ", ".join(c["removed"]), c["pair_jaccard_min"], c["pair_jaccard_max"]))


if __name__ == "__main__":
    main()
