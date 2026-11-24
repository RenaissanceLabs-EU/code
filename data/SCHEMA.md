# Resource entry schema (data/resources/<topic>.json = JSON array of objects)

Every entry MUST be verified against a primary source (HF API, GitHub API, paper, official docs) fetched on the date below. Never invent. If a field cannot be verified, use null and say so in `caveats`. 

{
  "id": "kebab-slug-unique",
  "name": "Display name",
  "kind": "dataset | benchmark | environment | tool | model | recipe | paper",
  "url": "primary link (HF dataset/model page, GitHub repo, or paper). Must resolve (HTTP 200).",
  "extra_links": [{"label": "Paper", "url": "..."}],
  "license": "SPDX-ish or exact wording from the source, e.g. 'Apache-2.0', 'MIT', 'CC-BY-4.0', 'per-file permissive licenses (see card)', 'gated: BigCode OpenRAIL-M terms'",
  "size": "as stated by source, e.g. '67.5 TB, 600+ languages' or '19k tasks'. Say what the unit is.",
  "summary": "1-2 plain sentences: what it is and what it is for. American English, no em dashes.",
  "stages": ["pretrain","midtrain","sft","preference","rl","eval","tooling"],   // pick all that apply
  "languages": ["python","multi", ...],   // programming languages covered; "multi" = many; "sql", "lean", "bash" allowed
  "tasks": ["completion","generation","repair","agentic","review","testing","sql","reasoning","tool-use","formal","terminal","repo-level","competitive"],
  "difficulty": "intro | intermediate | hard | frontier | null",
  "how_to_use": "1-3 sentences of practical advice: when to include it, mixing ratio hints ONLY if sourced, how to load.",
  "caveats": "Honest limits: contamination, license issues, noisy labels, saturation, synthetic-from-proprietary-model terms of use, size, required infra.",
  "load_snippet": "optional, copy-paste Python or shell that you have VERIFIED is correct for the dataset id/columns (e.g. datasets.load_dataset(...)); null if unsure",
  "released": "YYYY or YYYY-MM or null",
  "checked": "2026-11-24",
  "evidence": "which API/page confirmed license+size (e.g. 'huggingface.co/api/datasets/bigcode/the-stack-v2 cardData.license')"
}

Rules: American English. No em dashes (use commas or colons). Scores: only include numbers you saw in a primary source, and say which source and date in `caveats` or `summary`. Prefer fewer, correct entries over many uncertain ones. Aim 25-45 entries per topic.
