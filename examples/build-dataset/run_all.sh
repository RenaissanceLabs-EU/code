#!/bin/bash
# Run the whole pipeline from scratch. Usage: ./run_all.sh   (set RETRIEVAL_DATE to override the recorded date)
# Per-stage wall time and peak memory (macOS /usr/bin/time -l) go to timings/, outside out/, so out/ stays deterministic.
set -euo pipefail
cd "$(dirname "$0")"
export RETRIEVAL_DATE="${RETRIEVAL_DATE:-2026-11-25}"
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
PY=${PYTHON:-python3}
rm -rf data out timings
mkdir -p data out timings

run() {  # run <name> <command...>
  local name=$1; shift
  echo "== $name"
  /usr/bin/time -l "$@" 2> "timings/$name.txt" | tee "timings/$name.out"
  grep -E "real|maximum resident" "timings/$name.txt" | sed 's/^/   /'
}

run 01_collect   $PY 01_collect.py
run 02_filter    $PY 02_filter.py
run 03_scrub     $PY 03_scrub.py
run 04_dedup     $PY 04_dedup.py
run 05_split     $PY 05_split.py
run decontaminate $PY decontaminate.py --eval eval_probe.jsonl --input data/split.jsonl --output data/split_decon.jsonl --report out/logs/decontamination.json
run 06_format    $PY 06_format.py
run 07_card      $PY 07_card.py

# checksums of every released file (and of the intermediates) for the determinism check
( cd out && find . -type f ! -name SHA256SUMS | sort | xargs shasum -a 256 > SHA256SUMS )
( cd data && find . -type f | sort | xargs shasum -a 256 ) > timings/data_sha256.txt
echo "== done. out size:"; du -sk out | awk '{printf "   %.1f MB\n", $1/1024}'
