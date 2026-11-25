#!/usr/bin/env python3
"""OPTIONAL final check (uses the `datasets` library): load out/ through its README configs and compare counts. Not part of run_all.sh."""
import os
import tempfile
import warnings
warnings.filterwarnings("ignore")
from datasets import load_dataset

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
for cfg in ("code_corpus", "docstring_pairs"):
    ds = load_dataset(out, cfg, cache_dir=tempfile.mkdtemp())
    print(cfg, {k: len(v) for k, v in ds.items()}, "columns:", ds["train"].column_names)
