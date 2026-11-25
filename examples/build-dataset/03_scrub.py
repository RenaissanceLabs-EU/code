#!/usr/bin/env python3
"""Stage 3: regex scrubber for secrets and personal data. Logs rule hits, never the matched text."""
import ast
import ipaddress
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

# (rule name, compiled regex, replacement function or string). Order matters: longest/most specific first.
PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY(?: BLOCK)?-----.*?-----END [A-Z0-9 ]*PRIVATE KEY(?: BLOCK)?-----", re.S)
AWS_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
GITHUB_RE = re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")
PASSWORD_RE = re.compile(r"""(?i)([\w.]*(?:password|passwd|pwd|secret|api_key)\w*)(\s*=\s*)(["'])([^"'\n]{4,})\3""")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
IPV4_RE = re.compile(r"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?![\d.])")

RULE_NAMES = ["private_key_block", "aws_access_key_id", "github_token", "password_assignment", "email", "ipv4_global"]


def scrub(text, on_hit=None):
    """Return (clean_text, counts). on_hit(rule, line_number) is called per replacement."""
    counts = {r: 0 for r in RULE_NAMES}
    counts["ipv4_kept_non_global"] = 0

    def hit(rule, m):
        counts[rule] += 1
        if on_hit:
            on_hit(rule, text.count("\n", 0, m.start()) + 1)

    def sub(rule, rx, repl, s):
        def f(m):
            hit(rule, m)
            return repl(m) if callable(repl) else repl
        return rx.sub(f, s)

    # Line numbers are computed against the text as it stands before each rule runs, which is
    # good enough for a hit log (replacements may shift later lines by a few at most).
    out = text
    out = sub("private_key_block", PRIVATE_KEY_RE, "<PRIVATE_KEY>", out)
    out = sub("aws_access_key_id", AWS_RE, "<AWS_ACCESS_KEY_ID>", out)
    out = sub("github_token", GITHUB_RE, "<GITHUB_TOKEN>", out)
    out = sub("password_assignment", PASSWORD_RE, lambda m: "%s%s%s<PASSWORD>%s" % (m.group(1), m.group(2), m.group(3), m.group(3)), out)
    out = sub("email", EMAIL_RE, "<EMAIL>", out)

    def ip_repl(m):
        try:
            if not ipaddress.ip_address(m.group(0)).is_global:
                counts["ipv4_kept_non_global"] += 1  # loopback, private, documentation, unspecified: kept
                return m.group(0)
        except ValueError:
            return m.group(0)
        hit("ipv4_global", m)
        return "<IP_ADDRESS>"
    out = IPV4_RE.sub(ip_repl, out)
    return out, counts


def parses(text):
    try:
        ast.parse(text)
        return True
    except (SyntaxError, ValueError):
        return False


def main():
    common.cap_memory()
    totals = {}
    files_affected = {}
    hits_log = []
    n = changed = parse_before_ok = parse_after_ok = newly_broken = 0
    out = []
    for rec in common.read_jsonl(os.path.join(common.DATA, "filtered.jsonl")):
        n += 1
        path = rec["path"]
        clean, counts = scrub(rec["content"], on_hit=lambda rule, line, p=path: hits_log.append({"rule": rule, "path": p, "line": line}))
        for k, v in counts.items():
            totals[k] = totals.get(k, 0) + v
            if v and k in RULE_NAMES:
                files_affected[k] = files_affected.get(k, 0) + 1
        before_ok, after_ok = parses(rec["content"]), parses(clean)
        parse_before_ok += before_ok
        parse_after_ok += after_ok
        newly_broken += (before_ok and not after_ok)
        rec["source_sha256"] = rec["sha256"]
        rec["scrub_counts"] = {k: v for k, v in counts.items() if v and k in RULE_NAMES}
        if clean != rec["content"]:
            changed += 1
        rec["content"] = clean
        rec["sha256"] = common.sha256_text(clean)
        out.append(rec)
    common.write_jsonl(os.path.join(common.DATA, "scrubbed.jsonl"), out)
    hits_log.sort(key=lambda h: (h["path"], h["line"], h["rule"]))
    common.write_jsonl(os.path.join(common.LOGS, "scrub_hits.jsonl"), hits_log)
    log = {"stage": "03_scrub", "files_in": n, "files_changed": changed, "replacements_by_rule": {k: totals.get(k, 0) for k in RULE_NAMES},
           "files_affected_by_rule": {k: files_affected.get(k, 0) for k in RULE_NAMES},
           "ipv4_kept_non_global": totals.get("ipv4_kept_non_global", 0),
           "ast_parse_ok_before": parse_before_ok, "ast_parse_ok_after": parse_after_ok, "newly_unparseable_after_scrub": newly_broken,
           "hit_log": "logs/scrub_hits.jsonl (rule, path, line; no matched text)"}
    common.write_log("stage_03_scrub.json", log)
    print("files", n, "changed", changed)
    for k in RULE_NAMES:
        print("  %-22s %5d replacements in %3d files" % (k, totals.get(k, 0), files_affected.get(k, 0)))
    print("  ipv4 kept (non-global):", totals.get("ipv4_kept_non_global", 0))
    print("ast.parse ok before/after:", parse_before_ok, parse_after_ok, "| newly broken:", newly_broken)


if __name__ == "__main__":
    main()
