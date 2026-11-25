"""Unit tests for the key pipeline behaviors. Run: python3 -m unittest discover -s tests -v"""
import importlib.util
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)


def load(name):
    spec = importlib.util.spec_from_file_location("stage_" + name.replace(".py", ""), os.path.join(ROOT, name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


scrub = load("03_scrub.py")
dedup = load("04_dedup.py")
split = load("05_split.py")
decon = load("decontaminate.py")
filt = load("02_filter.py")
collect = load("01_collect.py")

# Fake secrets built by concatenation so that this file itself does not look like a leak.
FAKE_AWS = "AKIA" + "ABCDEFGHIJKLMNOP"
FAKE_GH = "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8"
FAKE_KEY = "-----BEGIN RSA " + "PRIVATE KEY-----\nMIIEfake\nlines\n-----END RSA " + "PRIVATE KEY-----"


class ScrubberTests(unittest.TestCase):
    def test_planted_secrets_are_removed_and_counted(self):
        src = 'aws = "%s"\ntok = "%s"\nkey = """%s"""\ndb_password = "hunter2hunter2"\nmail = "jane.doe@example.org"\nhost = "8.8.8.8"\n' % (FAKE_AWS, FAKE_GH, FAKE_KEY)
        hits = []
        out, counts = scrub.scrub(src, on_hit=lambda r, l: hits.append(r))
        for secret in (FAKE_AWS, FAKE_GH, "MIIEfake", "hunter2hunter2", "jane.doe@example.org", "8.8.8.8"):
            self.assertNotIn(secret, out)
        for rule in scrub.RULE_NAMES:
            self.assertEqual(counts[rule], 1, rule)
        self.assertEqual(sorted(hits), sorted(scrub.RULE_NAMES))
        self.assertIn("db_password = \"<PASSWORD>\"", out)
        compile(out, "<scrubbed>", "exec")  # scrubbed code still parses

    def test_non_global_ips_and_version_strings_are_kept(self):
        src = 'a = "127.0.0.1"\nb = "192.168.1.5"\nv = "1.2.3.4.5"\n'
        out, counts = scrub.scrub(src)
        self.assertEqual(out, src)
        self.assertEqual(counts["ipv4_global"], 0)
        self.assertEqual(counts["ipv4_kept_non_global"], 2)

    def test_clean_text_unchanged(self):
        src = "def f(x):\n    return x + 1\n"
        self.assertEqual(scrub.scrub(src)[0], src)


BASE = "\n".join("def func_%d(a, b):\n    total = a + b * %d\n    if total > %d:\n        return total - a\n    return total + b" % (i, i, i * 3) for i in range(40))


class MinHashTests(unittest.TestCase):
    def test_near_duplicate_found_and_distinct_file_not(self):
        near = BASE.replace("func_7", "renamed_seven")  # 1 of 40 functions changed: Jaccard well above 0.8
        other = "\n".join("class Widget%d:\n    def paint(self, canvas):\n        canvas.draw_line(%d, %d)\n        return canvas" % (i, i, i + 9) for i in range(40))
        clusters, n_cand, confirmed = dedup.near_dup_clusters({"a.py": BASE, "b.py": near, "c.py": other})
        self.assertEqual(clusters, [["a.py", "b.py"]])
        self.assertTrue(confirmed[0][2] >= dedup.THRESHOLD)

    def test_signature_is_deterministic(self):
        perms = dedup.make_perms()
        h = dedup.shingle_hashes(BASE)
        self.assertEqual(dedup.minhash(h, perms), dedup.minhash(h, dedup.make_perms()))

    def test_dissimilar_pair_below_threshold(self):
        half = "\n".join(BASE.split("\n")[:100]) + "\n" + "\n".join("def other_%d(q):\n    return q ** %d - q // 3" % (i, i) for i in range(60))
        j = dedup.jaccard(dedup.shingle_hashes(BASE), dedup.shingle_hashes(half))
        self.assertLess(j, dedup.THRESHOLD)


class SplitTests(unittest.TestCase):
    def test_group_of(self):
        self.assertEqual(split.group_of("email/mime/text.py"), "email")
        self.assertEqual(split.group_of("bisect.py"), "bisect")

    def test_same_group_same_split_and_stable(self):
        paths = ["email/a.py", "email/mime/b.py", "email/c.py", "json/x.py", "json/tool.py"]
        recs = [{"path": p, "repo": split.group_of(p), "split": split.split_of(split.group_of(p))} for p in paths]
        ok, bad = split.check_no_group_overlap(recs)
        self.assertTrue(ok, bad)
        self.assertEqual(split.split_of("email"), split.split_of("email"))

    def test_leak_detector_catches_a_straddling_group(self):
        recs = [{"repo": "email", "split": "train"}, {"repo": "email", "split": "test"}, {"repo": "json", "split": "train"}]
        ok, bad = split.check_no_group_overlap(recs)
        self.assertFalse(ok)
        self.assertEqual(bad, ["email"])

    def test_all_three_splits_reachable(self):
        got = {split.split_of("g%d" % i) for i in range(500)}
        self.assertEqual(got, {"train", "validation", "test"})


class DecontaminationTests(unittest.TestCase):
    def test_planted_overlap_detected_and_clean_code_passes(self):
        idx = decon.eval_index(os.path.join(ROOT, "eval_probe.jsonl"))
        planted = "import os\n\ndef rgb_to_hsv(r, g, b):\n    maxc = max(r, g, b)\n    minc = min(r, g, b)\n    v = maxc\n    if minc == maxc:\n        return 0.0, 0.0, v\n    s = (maxc-minc) / maxc\n"
        hits, ids, _ = decon.overlap(planted, idx)
        self.assertGreater(hits, 0)
        self.assertEqual(ids, ["probe-02"])
        clean = "def add(a, b):\n    return a + b\n" * 10
        self.assertEqual(decon.overlap(clean, idx)[0], 0)

    def test_twelve_token_overlap_is_not_flagged(self):
        eval_toks = " ".join("t%d" % i for i in range(30))
        idx = {g: "e1" for g in decon.ngrams(eval_toks.split(), 13)}
        text = " ".join("t%d" % i for i in range(12)) + " zzz"
        self.assertEqual(decon.overlap(text, idx)[0], 0)


class FilterAndLicenseTests(unittest.TestCase):
    def test_license_gate_expression(self):
        allowed = {"PSF-2.0", "MIT"}
        self.assertTrue(filt.license_allowed("PSF-2.0", allowed))
        self.assertTrue(filt.license_allowed("MIT OR Apache-2.0", allowed))
        self.assertFalse(filt.license_allowed("LicenseRef-HPND-style", allowed))
        self.assertFalse(filt.license_allowed("GPL-3.0-only", allowed))

    def test_quality_rules(self):
        long_line = "x = '" + "a" * 1200 + "'\n" * 1
        self.assertTrue(filt.rule_hits(long_line, 2000)["max_line_length"])
        self.assertTrue(filt.rule_hits("# auto-generated by foo\nx = 1\n" * 3, 500)["autogenerated_header"])
        self.assertTrue(filt.rule_hits("x=1\n", 4)["min_size"])
        self.assertFalse(any(filt.rule_hits("def f():\n    return 1\n" * 20, 400).values()))

    def test_header_license_detection(self):
        self.assertEqual(collect.detect_header_license("# Licensed under the Apache License, Version 2.0 (the \"License\");"), "Apache-2.0")
        self.assertEqual(collect.detect_header_license("# Permission to use, copy, modify, and distribute this software for any"), "LicenseRef-HPND-style")
        self.assertIsNone(collect.detect_header_license("# Copyright (c) Python Software Foundation"))


if __name__ == "__main__":
    unittest.main()
