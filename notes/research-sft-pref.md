# Research notes: code SFT, reasoning traces, synthetic and preference data (checked 2026-11-24)

Output: data/resources/sft-reasoning-preference.json (58 entries, all kind dataset).

## Dropped or not included, and why
- BIRD (xlangai/BIRD, bird-bench/bird_sql_dev), microsoft/CodeReviewer, bigcode/starcoder2-self-align, inclusionAI/Ling-Coder-SyntheticQA-sft, Code-Preference/Code-Preference-Pairs, PlatinumCode/Code-Preference, Nex-N1, NousResearch/hermes-agent-reasoning-traces, nvidia/Nemotron-Post-Training-Dataset-v3: HF API returned 401 (id guessed wrong or private). Not verified, so dropped. BIRD and CodeReviewer are host elsewhere (Zenodo or the BIRD site) and should be added by a follow-up pass that checks those primary sources.
- Nemotron-Post-Training-Dataset-v2: gated (auto), license cc-by-4.0, not read in detail; omitted rather than describe it blind.
- Nemotron-Pretraining-Code-v2: pretraining data, gated, out of scope here.
- allenai/tulu-3-sft-personas-code, Dolci-Think-SFT-7B, smoltalk2, R2EGym-SFT-Trajectories, OpenThoughts-Agent-v1-RL as standalone entries: no license tag in the API and little verified detail; Tulu code parts are covered inside the Tulu 3 mixture entry.
- Salesforce xlam-function-calling-60k (gated auto) and NousResearch hermes-function-calling-v1: tool-use sets, license verified via API but not described from card; left for the tool-use topic owner.
- Vezora Tested-143k-Python-Alpaca, ajibawa Code-290k-ShareGPT: exist, but provenance not read; skipped.
- Skywork-OR1-RL-Data and Mixture-of-Thoughts and smoltalk kept, but license is unspecified in API tags; flagged in caveats.
- WizardLM_evol_instruct_V2_196k: general not code-specific; skipped.
- Unverified claims removed: model sizes and sample counts only appear when seen in a card or dataset_info. HF datasets that were rate-limited (HTTP 429) during the final link sweep were each confirmed earlier through huggingface.co/api/datasets (HTTP 200 JSON).

## Licensing patterns (read these before mixing)
- Labeled permissive does not mean free of teacher terms. Cards that name OpenAI outputs: Magicoder OSS-Instruct (gpt-3.5-turbo-1106), Code-Feedback and CodeFeedback-Filtered (GPT-4/3.5, explicit usage-policy warning), Evol-CodeAlpaca (gpt-4-0314/0613), KodCode (gpt-4o-0513, plus CC-BY-NC), AceCode-87K (GPT-4o-mini rewrites), AceCode-V2 (o1-mini rewrites), CodeUltraFeedback (GPT-3.5 judge, GPT-4 responses).
- Anthropic outputs: SWE-smith trajectories (Claude 3.7 Sonnet).
- DeepSeek-R1 / R1-0528 teachers: OpenCodeReasoning v1 and v2, Nemotron Competitive Programming v2, Nemotron-Cascade-SFT-SWE and Nemotron SWE v2 agentless, Open-R1 CodeForces-CoTs and Mixture-of-Thoughts, OpenThoughts-114k, SYNTHETIC-1, Bespoke-Stratos, KodCode-V1-SFT-R1.
- Qwen teachers: OpenCodeInstruct (Qwen2.5-Coder-32B-Instruct per paper), OpenThoughts3 (QwQ-32B), Nemotron OpenCode and SWE v2 trajectories (Qwen3-Coder-480B), Magpie Coder (Qwen2.5-Coder-32B), nebius OpenHands (Qwen3-Coder-480B). Llama-derived: nebius SWE-agent-trajectories (Llama 3.1 license note).
- Teacher-free or self-generated options: StarCoder2 self-oss-instruct (SelfCodeAlign, base model generates everything), CommitPackFT/EditPackFT (human commits), Spider.
- Non-commercial: KodCode family (CC-BY-NC-4.0), Evol-Instruct-Code-80k (CC-BY-NC-SA). Tulu 3 mixture states some subsets are non-commercial.
- Missing license tag in HF API: Skywork-OR1-RL-Data, smoltalk, Mixture-of-Thoughts, Sky-T1 data card minimal, SWE-Gym OpenHands trajectories. Treat as unknown.

## What moved benchmarks, per the papers (abstracts and cards read today)
- OpenCodeReasoning (arXiv 2504.01943 abstract): SFT only reached 61.8 on LiveCodeBench and 24.6 on CodeContests for its best distilled model. Authors report execution filtering hurt benchmark accuracy, so they favored instruction diversity over solution correctness. This runs against the common assumption that only test-passing traces should be kept.
- OpenThoughts (arXiv 2506.04178 abstract): 1,000+ controlled experiments over pipeline steps; OpenThoughts3-7B reaches 51% on LiveCodeBench with QwQ-32B as teacher and 1.2M examples. Takeaway there is that recipe choices (question sourcing, teacher, filtering) matter and can be tested empirically.
- SelfCodeAlign (arXiv 2410.24198 abstract): 74K self-generated, execution-validated pairs from CodeQwen1.5-7B gave 67.1 HumanEval+ pass@1, above CodeLlama-70B-Instruct. Strong evidence that small, validated, self-generated data competes with larger distilled data.
- Magicoder (arXiv 2312.02120 abstract): 75K OSS-Instruct pairs beat larger code models; OSS-Instruct and Evol-Instruct are orthogonal and combine (MagicoderS).
- OctoPack (arXiv 2308.07124 abstract): commit-based instruction tuning reached 46.2 HumanEval Python pass@1 on StarCoder-16B among models not trained on OpenAI outputs. The only large-scale route here with no LLM teacher.
- SWE-smith (arXiv 2504.21798 abstract and trajectories card): 5,017 Claude 3.7 trajectories fine-tuned Qwen 2.5 Coder; paper abstract reports 40.2% Pass@1 on SWE-bench Verified for SWE-agent-LM-32B. Small trajectory sets can matter a lot.
- Bespoke-Stratos card: ~17K R1 traces, about $800 of generation. Cheap reasoning distillation works at small scale.
- AceCoder (arXiv 2502.01718 abstract): test-case-derived preference pairs trained reward models giving ~10-point average best-of-32 gains for Llama-3.1-8B-Instruct and ~5 for Qwen2.5-Coder-7B-Instruct; RL with these tests improved HumanEval, MBPP, BigCodeBench, LiveCodeBench.
- OpenCodeInstruct (arXiv 2504.04030): paper ablates generation algorithm, seed type, scale, and notes the solution-generating model's own benchmark strength propagates to the student.
- Nemotron-Cascade-SFT-SWE card: SWE data upsampled 3x in the Stage-2 SFT blend; 37.2 and 43.1 resolve rates for 8B and 14B after SFT and RL (card figures).

## Practical insights
1. For competitive-programming reasoning, the proven path is large R1/QwQ distillation (OpenCodeReasoning, OpenThoughts3, rStar-Coder, Nemotron CP v2). Diversity of problems beats verifying every trace.
2. For general code SFT quality over quantity: SelfCodeAlign and Magicoder show tens of thousands of well-seeded examples are competitive. OpenCodeInstruct gives per-row test scores so you can cut 5M down to the best slice.
3. Agentic data is scarcest and most valuable: SWE-smith trajectories, Nemotron SWE v2 (~46K OpenHands trajectories), nebius sets, OpenThoughts-Agent. Match the harness format (SWE-agent, OpenHands, OpenCode, Terminus-2) you will deploy with.
4. Preference data: the only test-grounded public sets are AceCode-derived, Ling-Coder-DPO (CodeContests, pass rate plus reward model), and zake7749 rejection-sampling pairs. CodeUltraFeedback is LLM-judge based, good for style, not correctness. Vezora pairs are synthetic bug injection. Building on-policy pairs from your own model plus tests (RS or pass-rate pairing) is likely better than any public set; AceCode-V2 and rStar-Coder testcase configs provide the tests.
5. Many RL-oriented sets double as SFT seeds; stage tags in the JSON reflect that.

## Surprises
- Execution filtering lowered scores in OpenCodeReasoning's analysis.
- Nemotron now ships agent data for a specific CLI (OpenCode) with synthetic agent skills, with questions from GPT OSS 120B and traces from Qwen3-Coder-480B.
- Several 2025-2026 sets are generated by Qwen3-Coder or GLM-4.6 rather than R1, shifting teacher licensing from DeepSeek to Qwen/Zhipu terms.
- SWE-smith's maintainers stopped updating the monorepo dataset (card note, 12/14/2025) and moved to per-language sets.
- A web-search summary mentioned datasets claiming frontier proprietary teachers on third-party uploads; not verified and not included.
