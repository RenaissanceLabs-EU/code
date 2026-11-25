#!/usr/bin/env python3
"""Stage 1: walk the source tree, record provenance per file, write data/raw.jsonl."""
import hashlib
import os
import re
import sys
import sysconfig

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

MAX_BYTES = 200_000
SKIP_DIRS = {"site-packages", "__pycache__"}
LICENSE_PAGE = "https://docs.python.org/3/license.html"

# Header patterns, checked on the first 6000 characters. Order matters only for reporting.
HEADER_PATTERNS = [
    ("Apache-2.0", re.compile(r"licen[sc]ed under the apache license,? version 2\.0|also licen[sc]ed under the apache license, 2\.0")),
    ("MIT", re.compile(r"licen[sc]ed under the mit license|permission is hereby granted, free of charge")),
    ("LicenseRef-HPND-style", re.compile(r"permission to use, copy, modify,? and distribute this software")),
    ("LicenseRef-BSD-style", re.compile(r"redistribution and use in source and binary forms")),
]


def detect_header_license(text):
    head = text[:6000].lower()
    found = [name for name, rx in HEADER_PATTERNS if rx.search(head)]
    if not found:
        return None
    if "MIT" in found and "Apache-2.0" in found:
        return "MIT OR Apache-2.0"
    return found[0]


def main():
    common.cap_memory()
    stdlib = os.environ.get("STDLIB_DIR") or sysconfig.get_paths()["stdlib"]
    version = "%d.%d.%d" % sys.version_info[:3]
    lic_path = os.path.join(stdlib, "LICENSE.txt")
    log = {"stage": "01_collect", "source_tree": common.SOURCE_TREE, "source_version": version,
           "retrieval_date": common.RETRIEVAL_DATE, "max_bytes": MAX_BYTES}

    if os.path.isfile(lic_path):
        with open(lic_path, "rb") as f:
            lic_bytes = f.read()
        lic_text = lic_bytes.decode("utf-8")
        assert "PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2" in lic_text, "unexpected license text"
        lic_sha = hashlib.sha256(lic_bytes).hexdigest()
        log.update(license_file="LICENSE.txt", license_file_sha256=lic_sha,
                   license_verified="LICENSE.txt contains 'PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2'",
                   license_identifier="PSF-2.0")
        os.makedirs(common.OUT, exist_ok=True)
        with open(os.path.join(common.OUT, "LICENSE"), "wb") as f:  # redistributed verbatim with the data
            f.write(lic_bytes)
    else:  # fallback described in the brief; not used on this machine
        lic_sha = None
        log.update(license_file=None, license_file_sha256=None, license_identifier="PSF-2.0",
                   license_verified="license file absent; provenance is sys.copyright and " + LICENSE_PAGE)

    has_top_test = os.path.isdir(os.path.join(stdlib, "test"))
    log["top_level_test_dir_present"] = has_top_test

    seen = non_utf8 = too_large = 0
    sibling_test_dirs = []
    records = []
    for root, dirs, files in os.walk(stdlib):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        rel_root = os.path.relpath(root, stdlib)
        for d in dirs:
            if d in ("test", "tests", "idle_test"):
                sibling_test_dirs.append(os.path.normpath(os.path.join(rel_root, d)))
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            seen += 1
            full = os.path.join(root, name)
            rel = os.path.relpath(full, stdlib).replace(os.sep, "/")
            raw = open(full, "rb").read()
            if len(raw) > MAX_BYTES:
                too_large += 1
                continue
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                non_utf8 += 1
                continue
            text = text.replace("\r\n", "\n")
            header = detect_header_license(text)
            records.append({
                "path": rel,
                "source_tree": common.SOURCE_TREE,
                "source_version": version,
                "license": header or "PSF-2.0",
                "license_source": "file-header-regex" if header else "tree-default",
                "license_file": "LICENSE.txt",
                "license_file_sha256": lic_sha,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "size": len(raw),
                "retrieval_date": common.RETRIEVAL_DATE,
                "content": text,
            })
    records.sort(key=lambda r: r["path"])
    n = common.write_jsonl(os.path.join(common.DATA, "raw.jsonl"), records)
    lic_counts = {}
    for r in records:
        lic_counts[r["license"]] = lic_counts.get(r["license"], 0) + 1
    log.update(files_seen=seen, skipped_non_utf8=non_utf8, skipped_too_large=too_large, files_kept=n,
               license_counts=dict(sorted(lic_counts.items())),
               test_dirs_inside_packages=sorted(sibling_test_dirs),
               excluded_dir_names=sorted(SKIP_DIRS))
    common.write_log("stage_01_collect.json", log)
    print("files seen %d, non-UTF-8 %d, over %d bytes %d, kept %d" % (seen, non_utf8, MAX_BYTES, too_large, n))
    print("licenses:", log["license_counts"])
    print("top-level test dir present:", has_top_test, "| test dirs inside packages:", sorted(sibling_test_dirs))


if __name__ == "__main__":
    main()
