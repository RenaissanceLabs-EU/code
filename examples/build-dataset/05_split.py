#!/usr/bin/env python3
"""Stage 5: split by repository group (top-level package or module) using a stable hash of the group name."""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

SALT = "build-dataset-v1"
BUCKETS = {"train": range(0, 80), "validation": range(80, 90), "test": range(90, 100)}


def group_of(path):
    """Top-level package directory, or the module name for a top-level file. Stands in for a repository."""
    first = path.split("/")[0]
    return first[:-3] if first.endswith(".py") else first


def split_of(group, salt=SALT):
    b = int(hashlib.sha256((salt + ":" + group).encode("utf-8")).hexdigest(), 16) % 100
    for name, rng in BUCKETS.items():
        if b in rng:
            return name


def check_no_group_overlap(records):
    """Return (ok, offending_groups). A group is offending if it appears in more than one split."""
    seen = {}
    for r in records:
        seen.setdefault(r["repo"], set()).add(r["split"])
    bad = sorted(g for g, s in seen.items() if len(s) > 1)
    return (not bad), bad


def main():
    common.cap_memory()
    recs = []
    for r in common.read_jsonl(os.path.join(common.DATA, "deduped.jsonl")):
        r["repo"] = group_of(r["path"])
        r["split"] = split_of(r["repo"])
        recs.append(r)
    ok, bad = check_no_group_overlap(recs)
    assert ok, bad
    common.write_jsonl(os.path.join(common.DATA, "split.jsonl"), recs)
    per = {s: {"files": 0, "groups": set()} for s in BUCKETS}
    for r in recs:
        per[r["split"]]["files"] += 1
        per[r["split"]]["groups"].add(r["repo"])
    groups_by_split = {s: sorted(v["groups"]) for s, v in per.items()}
    all_sets = [set(g) for g in groups_by_split.values()]
    pairwise_overlap = sum(len(all_sets[i] & all_sets[j]) for i in range(3) for j in range(i + 1, 3))
    check = {"rule": "split = stable hash of group name (sha256 of salt:group) mod 100: <80 train, 80-89 validation, 90-99 test",
             "salt": SALT, "group_definition": "top-level package directory, or module name for a top-level .py file",
             "files_by_split": {s: v["files"] for s, v in per.items()}, "groups_by_split": {s: len(v["groups"]) for s, v in per.items()},
             "groups_in_more_than_one_split": bad, "pairwise_group_overlap_count": pairwise_overlap, "no_group_overlap": ok and pairwise_overlap == 0,
             "largest_groups": sorted(({"group": g, "files": sum(1 for r in recs if r["repo"] == g), "split": split_of(g)} for g in {r["repo"] for r in recs}),
                                      key=lambda d: (-d["files"], d["group"]))[:8]}
    common.write_log("stage_05_split.json", check)
    with open(os.path.join(common.OUT, "split_check.json"), "w", encoding="utf-8", newline="\n") as f:
        import json
        json.dump(dict(check, groups_by_split_names=groups_by_split), f, sort_keys=True, indent=2)
        f.write("\n")
    print("files by split:", check["files_by_split"], "| groups:", check["groups_by_split"])
    print("group overlap between splits:", pairwise_overlap, "| check passed:", check["no_group_overlap"])
    print("largest groups:", check["largest_groups"])


if __name__ == "__main__":
    main()
