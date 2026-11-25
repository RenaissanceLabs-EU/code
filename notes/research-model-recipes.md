# Research notes: model recipes (checked 2026-11-25)

Outputs: data/model-recipes.json (18 models), data/recipe-patterns.json (8 patterns).
Method: for 14 models I downloaded the arXiv PDF into a scratch folder and read the text (abstract, data, training, post-training and results sections). For DeepCoder, DeepSWE, Qwen3-Coder and SmolLM3 I read the full blog text. HF API was used only for release dates, license and base_model fields. Nothing was copied from the catalog.

## Models dropped and why
- Devstral (Small 2 and 2): the Mistral announcement (devstral, May 21, 2025) has no training detail (no data, tokens, method or reward). No technical report found. Dropped.
- OpenHands LM 32B: the blog (March 31, 2025) gives only a few sentences (fine-tuned from Qwen Coder 2.5 Instruct 32B on OpenHands-generated data via SWE-Gym, 128K context). Too thin for the stage table. Dropped.
- Codestral-22B, GLM-5.3, DeepSeek-V3.2/V4, Kimi K3.1, Nemotron 3 Ultra, Nemotron-Cascade, gpt-oss, Qwen3.8, Qwen3-Coder-Next, Qwen3-Coder-30B-A3B, Devstral 2, Open-R1: not read in this pass (no report or card with stage detail opened), so not included. Qwen3-Coder 30B-A3B and Next share the Qwen3-Coder row only if the blog said so; it did not, so only the 480B-A35B entry is listed.
- Cap of 18 reached; the others above were lower priority, not rejected on quality.

## Entries that differ from the catalog list
- deepseek-coder (v1) has no model entry in the catalog (only paper-deepseek-coder), so the id is a slug.
- DeepCoder: the catalog recipe URL is a Notion page; I read the Together AI blog with the same title and text. Authors, date (2025-04-08) and numbers are from that page.
- Qwen2.5-Coder, Code Llama and the other multi-size families are listed as one row; where a field differs by size it is stated per size.

## Conventions
- "released" is the earliest dated artifact I fetched (arXiv ID month, blog date, or HF repo createdAt). HF createdAt may precede public release, so treat it as approximate. DeepSeek-Coder uses the HF date (2023-10-28) while its report is January 2024; Granite uses the HF date (2024-04-21) while its report is May 2024; Seed-Coder uses the HF date (2025-04-27) while its report is June 2025; Kimi-Dev uses the HF date (2025-06-16) while its report is September 2025.
- "base" says "no earlier checkpoint named" for StarCoder2, Seed-Coder, Olmo 3 and SmolLM3. I did not read an explicit "from scratch" statement for those, so I did not write it. "from scratch" is used only where the report says it (DeepSeek-Coder, OpenCoder, Granite).
- Code share is null where the report gives no code percentage; for fine-tuned-from-base models the pretrain block is null.
- "open" levels: "weights, data and code" only where the source states data and code are released (OpenCoder, Skywork-OR1, SWE-smith, DeepCoder, DeepSWE, Olmo 3, SmolLM3 blog says "fully open"). Others are "weights" (or "weights and data" for StarCoder2 via SWHIDs and OpenCodeReasoning via its dataset).
- Olmo 3 and SmolLM3 are general-purpose models; code is one domain. Marked in the evidence field.

## Not verified
- Token counts for post-training stages not stated in the source are null (for example DeepCoder and DeepSWE give steps and hardware, not tokens).
- Kimi-Dev's "about 150B" mid-training total: the three listed components (50B, 20B, 20B upsampled 4 times) do not obviously sum to 150B in the text I read; I wrote the figures as stated.
- Seed-Coder reasoning reward: the report mentions correctness and a format reward but I did not find a precise definition of the code reward.
- Qwen3-Coder: base model, SFT data, RL algorithm and language count are not stated in the blog; no technical report was found or read. Language count and base are null.
- Qwen2.5-Coder: SFT teacher model not named in the sections read (null). Qwen2.5-Coder 23.5T total shown in the OpenCoder table was not used.
- OpenCoder: the share of code in the 2.5T pretraining stream is not stated as a single percentage; I gave RefineCode Table 2 shares instead. No FIM statement for pretraining was read.
- Code Llama language count and Instruct RL details (beyond Llama 2's RLHF V5 set) not read; "released" is the arXiv v1 month (Aug 2023), eval sentence is from v3 (Jan 2024).
- StarCoder2 "open" level: SWHIDs and the Stack v2 are released per the abstract; whether training code is released was not checked.
- Benchmarks marked "report vN" are the PDF versions I downloaded, which may have been revised since the first release.
- AceReason, Skywork-OR1 and OpenCodeReasoning appendix tables and hyperparameter sections were read only in part.
- Hugging Face comments on the SmolLM3 blog and any other page text addressed to readers were ignored.
