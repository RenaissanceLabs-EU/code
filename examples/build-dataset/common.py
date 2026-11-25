"""Shared helpers for the build-dataset pipeline. Python 3.9, standard library only."""
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "out")
LOGS = os.path.join(OUT, "logs")

SOURCE_TREE = "cpython-stdlib"
RETRIEVAL_DATE = os.environ.get("RETRIEVAL_DATE", "2026-11-25")
TOKEN_RE = re.compile(r"\w+|[^\w\s]")


def cap_memory(gb=3):
    """Best effort address-space cap so a bug cannot exhaust RAM (macOS may ignore it)."""
    try:
        import resource
        lim = int(gb * 1024 ** 3)
        resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
    except Exception:
        pass


def tokens(text):
    return TOKEN_RE.findall(text)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_jsonl(path):
    """Stream records one at a time."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def write_jsonl(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    n = 0
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
            n += 1
    return n


def write_log(name, obj):
    os.makedirs(LOGS, exist_ok=True)
    with open(os.path.join(LOGS, name), "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, sort_keys=True, indent=2, ensure_ascii=False)
        f.write("\n")


def read_log(name):
    with open(os.path.join(LOGS, name), encoding="utf-8") as f:
        return json.load(f)
