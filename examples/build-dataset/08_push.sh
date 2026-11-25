#!/bin/bash
# Stage 8: publish out/ to the Hugging Face Hub as a dataset repo and tag the version.
# NOT RUN as part of this example. It refuses to do anything until you set REPO_ID and CONFIRM_PUSH=yes.
#
# Command names checked 2026-11-25 against huggingface_hub 0.36.0 installed here (`hf repo create`, `hf repo tag create`,
# `hf upload`; --help output read) and against the current CLI guide https://huggingface.co/docs/huggingface_hub/guides/cli,
# which spells the group `hf repos` (`hf repos create`, `hf repos tag create`). Use whichever your installed version has;
# the legacy `huggingface-cli` entry point still ships in 0.36 but the `hf` CLI is the documented one.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ID="${REPO_ID:?set REPO_ID, for example your-org/cpython-stdlib-example}"
VERSION="${VERSION:-v0.1.0}"
[ "${CONFIRM_PUSH:-no}" = "yes" ] || { echo "Dry run only. Set CONFIRM_PUSH=yes to push $REPO_ID at $VERSION."; exit 0; }
[ -f out/README.md ] && [ -f out/SHA256SUMS ] || { echo "run ./run_all.sh first"; exit 1; }
( cd out && shasum -a 256 -c SHA256SUMS )   # refuse to upload files that changed since the run

hf auth login                                                     # or: export HF_TOKEN=... (needs write access)
hf repos create "$REPO_ID" --repo-type dataset --private --exist-ok  # start private; flip to public in the repo settings after review
hf upload "$REPO_ID" out . --repo-type dataset --commit-message "Dataset $VERSION: CPython 3.9.6 stdlib example"
hf repos tag create "$REPO_ID" "$VERSION" --repo-type dataset -m "Dataset $VERSION"

# Equivalent Python (huggingface_hub 0.36 signatures read from the installed package):
#   from huggingface_hub import HfApi
#   api = HfApi()
#   api.create_repo(repo_id=REPO_ID, repo_type="dataset", private=True, exist_ok=True)
#   api.upload_folder(repo_id=REPO_ID, repo_type="dataset", folder_path="out", commit_message="Dataset v0.1.0")
#   api.create_tag(repo_id=REPO_ID, tag="v0.1.0", repo_type="dataset", tag_message="Dataset v0.1.0")
# Consumers pin the version with: load_dataset(REPO_ID, "docstring_pairs", revision="v0.1.0")
