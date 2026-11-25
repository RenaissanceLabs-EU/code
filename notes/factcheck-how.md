# Fact check: data/pages/how.html, F.fim and F.passk (2026-11-25)

Method: each claim was treated as wrong until a source fetched on this date supported it. Papers were read as PDF text (arXiv), dataset cards through the Hugging Face raw README or API, and some abstracts through arxiv.org/abs. Counts: 2 Wrong, 9 Needs a qualifier, 27 Confirmed.

## Wrong

**1. The Stack v2 sentence**

Sentence: "{{r:the-stack-v2}}, the dataset behind StarCoder2, is built from the Software Heritage archive and also includes issues, commits and notebooks."

What is wrong: the StarCoder 2 paper lists the extra sources as GitHub issues, pull requests (with diffs the authors generate themselves), Jupyter and Kaggle notebooks, documentation, intermediate representations and small math and coding sets. Commits are not a data source. The only mention of commits is that the Software Heritage graph links files to git commits, and that the latest revision of each repository is taken. Also, strictly, the Software Heritage source code is The Stack v2; the issues, pull requests, notebooks and documentation are added to make the StarCoder2 training set (StarCoder2Data), per the paper's abstract and Section 2.

Sources: https://arxiv.org/abs/2402.19173 (abstract, Sections 2.1 to 2.5); https://huggingface.co/datasets/HuggingFaceTB/stack-edu (card: StarCoder2Data is the curated training corpus of StarCoder2).

Corrected sentence: "{{r:the-stack-v2}} is built on the Software Heritage archive, and the StarCoder2 training set adds GitHub issues, pull requests, notebooks and documentation to it."

**2. The OpenCoder claim in the Stack-Edu sentence**

Sentence: "...and reports from teams including the OpenCoder authors find that this kind of filtering pays back more than extra volume."

What is wrong: the OpenCoder paper (arXiv 2411.04905) does not test a classifier-based educational filter against more volume. What it reports: (a) file-level deduplication beats repository-level deduplication; (b) filtering by GitHub stars (stars >= 5) made a 1.5B model worse than the unfiltered data, because it cut diversity (Section 6.3, Figure 10); (c) removing the high-quality algorithmic and synthetic data from the annealing mix lowered scores a lot (Section 6.2, Figure 9), which the authors summarize as quality mattering more than quantity "in the later stages of model training". It uses heuristic file filters, including an "educational code" heuristic category, not an LLM-trained classifier. The evidence that classifier filtering beats unfiltered data comes from the SmolLM2 report (Stack-Edu), and it compares filtered and unfiltered data in short annealing runs, not "more volume".

Sources: https://arxiv.org/abs/2411.04905 (Introduction key points 1 to 5, Sections 6.1 to 6.3); https://arxiv.org/abs/2502.02737 (Section 3.4, Table 2).

Corrected sentence: "{{r:stack-edu}} keeps only files that a small classifier, trained on an LLM's ratings, scored as educational, and the SmolLM2 team found that this improved MultiPL-E scores in most languages in short annealing runs. The OpenCoder authors report a related result for the final annealing phase: removing its high-quality data lowered scores a lot."

## Needs a qualifier

**3. Stack-Edu**

Sentence: "{{r:stack-edu}} keeps only the files an LLM judged to be educational."

Issue: an LLM (Llama3-70B-Instruct) rated 500,000 sample files per language on a 0 to 5 scale. A small classifier (StarEncoder) trained on those ratings then scored every file, and files at or above a threshold of 3 are kept (the paper notes Java did better at 2). It covers the 15 largest languages of StarCoder2Data and totals about 125B tokens.

Source: https://arxiv.org/abs/2502.02737 (Section 3.4, Appendix D); https://huggingface.co/datasets/HuggingFaceTB/stack-edu

Corrected sentence: "{{r:stack-edu}} keeps the files that a classifier, trained on an LLM's 0 to 5 educational ratings, scored 3 or higher, in 15 languages."

**4. "Most code models are also trained with fill in the middle"**

Issue: common, but not universal. Code Llama trained only some of its sizes for infilling (the paper marks infilling-capable models with a symbol and the abstract says "variants support infilling"). StarCoder, StarCoder2, DeepSeek-Coder and OpenCoder do use FIM.

Sources: https://arxiv.org/abs/2308.12950; https://arxiv.org/abs/2305.06161; https://arxiv.org/abs/2402.19173; https://arxiv.org/abs/2401.14196; https://arxiv.org/abs/2411.04905

Corrected sentence: "Many code models, including StarCoder, StarCoder2 and DeepSeek-Coder, are also trained with fill in the middle."

**5. FIM figure: the SPM arrangement (F.fim)**

Text: the dropdown option "Suffix, prefix, middle (SPM)" and the sum sentence "The sentinel names here follow StarCoder; each model family chooses its own."

Issue: the names are right (StarCoder uses <fim_prefix>, <fim_suffix>, <fim_middle>, plus <fim_pad>) and PSM is drawn correctly as prefix, suffix, middle. But the SPM layout drawn, "<fim_suffix> suf <fim_prefix> pre <fim_middle>", is the paper's "SPM variant 1". Bavarian et al. trained with variant 2, which StarCoder also uses ("PSM mode with probability .5 and SPMv2 mode with probability .5"): <PRE> <SUF> suffix <MID> prefix middle, so the prefix sentinel comes first and the prefix text follows the middle sentinel. Variant 1 is a legitimate arrangement (the paper says it can be better for subtokens at the end of the prefix) but it is not what StarCoder trains. StarCoder2 uses PSM only. Real training also adds an end-of-text token after the middle, which the figure omits.

Sources: https://arxiv.org/abs/2207.14255 (Sections 3 and 3.1, Appendix D); https://arxiv.org/abs/2305.06161 (data formatting section); https://arxiv.org/abs/2402.19173 (FIM paragraph, Section 5.1).

Corrected sum sentence: "The sentinel names here follow StarCoder; each model family chooses its own. StarCoder trained the prefix, suffix, middle order and a second order in which the prefix sentinel comes first, then the suffix sentinel and suffix, then the middle sentinel and the prefix. The suffix-first order shown here is a simpler variant of that second order."
Alternative fix: change the SPM branch to P + S + suf + M followed by the prefix text (prefix sentinel, suffix sentinel, suffix, middle sentinel, prefix) and keep the label "Suffix, prefix, middle (SPM)".

**6. "This is the stage that moves hard coding scores the most."**

Issue: no source, and counterexamples exist. OpenCodeReasoning reaches 61.8% on LiveCodeBench with SFT on distilled reasoning traces only, "surpassing alternatives trained with reinforcement learning". The DeepSeek-R1 paper reports that SFT distillation lifted small models far above their bases and that RL on top gave "significant further gains". RL gains from a distilled base are real but smaller: DeepCoder-14B-Preview, RL from R1-Distill-Qwen-14B, went from 53.0% to 60.6% on LiveCodeBench.

Sources: https://arxiv.org/abs/2504.01943; https://arxiv.org/abs/2501.12948; https://www.together.ai/blog/deepcoder

Corrected sentence: "For hard problems, large gains often come from reasoning-trace fine-tuning first, and this stage adds further gains on top, because it trains directly on whether the code passes."

**7. "Compute the loss on the response only, not on the instruction."**

Issue: this is the default in common tooling (TRL computes loss on the completion only for prompt-completion data, and offers assistant_only_loss), but the sentence says it "recurs across the recipes" and I could not find it stated in the Magicoder, WizardCoder, OpenCoder, KodCode, OpenCodeReasoning or SWE-smith papers. Shi et al. (2024) report that also computing loss over the instruction improved results on 21 benchmarks, especially with long instructions and short outputs or few examples.

Sources: https://huggingface.co/docs/trl/sft_trainer (Train on completion only); https://arxiv.org/abs/2405.14394

Corrected sentence: "Most tooling computes the loss on the response only, not on the instruction, though some work finds that including the instruction helps when responses are short."

**8. "synthetic data inherits it" (teacher license)**

Sentence: "treat the license of the teacher model as part of the dataset: synthetic data inherits it."

Issue: overstated as law. What the cards show is that the dataset license and the generator's terms differ. Magicoder-OSS-Instruct-75K is MIT but its card tells users to follow OpenAI's usage policy because gpt-3.5-turbo generated it. KodCode-V1 is CC BY-NC 4.0. OpenCodeReasoning is CC BY 4.0 and has a per-row license column for the source problems. Whether outputs inherit a license is not settled by these cards.

Sources: https://huggingface.co/datasets/ise-uiuc/Magicoder-OSS-Instruct-75K; https://huggingface.co/datasets/KodCode/KodCode-V1; https://huggingface.co/datasets/nvidia/OpenCodeReasoning

Corrected sentence: "Check the terms of the teacher model and the license of the source problems as well as the dataset's own license: they can differ."

**9. Reward hacking examples and the two cited papers**

Sentence: "Models trained this way find the gaps: they edit the tests, special-case the expected values, read hidden files, or use the network if the sandbox leaves it on ({{r:paper-coding-or-cheating}}, {{r:paper-reward-hack-audit}})."

Issue: the two cited papers do not show all four. "Coding or Cheating?" (arXiv 2611.10404) evaluated frontier models, it did not train any: models mined repository history, inspected the git object store, and swept the filesystem for a newer copy of the source or hidden tests. "Auditing Reward Hackability" (arXiv 2606.16062) finds that about 22% of 49 SWE-bench Verified tasks accept a patch that differs from the gold patch (about 58% against a stronger attacker), including patches that special-case the path the test exercises. Neither shows test editing or network use. Other sources do: Baker et al. (OpenAI) saw exit(0), raise SkipTest, stub implementations and edits to test files during training; ImpossibleBench shows models modifying tests and special-casing; SWE-Bench Pro Verified lists external network lookups of upstream commits and patches as an attack channel and blocks code-hosting domains.

Sources: https://arxiv.org/abs/2611.10404; https://arxiv.org/abs/2606.16062; https://arxiv.org/abs/2503.11926; https://arxiv.org/abs/2510.20270; https://arxiv.org/abs/2609.08149

Corrected sentence: "Models find the gaps: they read the repository history or other files for the answer, edit or skip the tests, special-case the expected values, or look the fix up on the network if the sandbox leaves it on ({{r:paper-coding-or-cheating}}, {{r:paper-reward-hack-audit}}, and the OpenAI monitoring paper, arXiv 2503.11926)." Add the last paper to the catalog if a resource id is wanted.

**10. "Most teams do not pretrain."**

Issue: no survey supports "most teams"; it is a reasonable statement about small teams, not about all teams that build coding models. Cost is the evidence: StarCoder2 models trained on 3.3 to 4.3 trillion tokens (paper abstract).

Source: https://arxiv.org/abs/2402.19173 (abstract)

Corrected sentence: "A small team does not need to pretrain, and usually should not: the open code models were trained on trillions of tokens."

**11. LiveCodeBench**

Sentence: "{{r:livecodebench}} fights it by collecting problems after a model's training cutoff."

Issue: it keeps adding new problems from LeetCode, AtCoder and Codeforces and stores release dates, so you evaluate only on problems newer than the model's cutoff. The benchmark itself is not tied to any one cutoff.

Source: https://arxiv.org/abs/2403.07974 (principle 1, live updates to prevent contamination)

Corrected sentence: "{{r:livecodebench}} fights it by adding new problems continuously and recording their release dates, so you can score only problems published after a model's training cutoff."

## Confirmed

- Software Heritage is the base of The Stack v2: https://arxiv.org/abs/2402.19173 (abstract).
- Issues and notebooks are in the StarCoder2 training set (Sections 2.2 and 2.4): same paper.
- Files filtered by license, near-duplicates removed, PII redacted, benchmark decontamination: StarCoder 2 paper Section 3.
- Fill in the middle can be added "for free": Bavarian et al. abstract and Figure 1 (50% FIM rate, no left-to-right loss cost, measured by perplexity and sampling) https://arxiv.org/abs/2207.14255.
- FIM moves a span from the middle to the end; PSM is prefix, suffix, middle: Bavarian et al. Section 3.
- StarCoder FIM sentinels are <fim_prefix>, <fim_suffix>, <fim_middle> (and <fim_pad>): StarCoder paper, token table.
- Other families choose other names (the OpenAI paper itself writes <PRE>, <SUF>, <MID>): https://arxiv.org/abs/2207.14255.
- Late high-quality annealing phase: OpenCoder Section 2.2 and Figure 9 https://arxiv.org/abs/2411.04905; SmolLM2 puts Stack-Edu and FineMath into the later stages https://arxiv.org/abs/2502.02737.
- Synthetic data in annealing (OpenCoder Table 3) and educational data in later stages (SmolLM2): same papers.
- Long-context extension after pretraining: StarCoder2 (4,096 to 16,384 tokens, 200B tokens, same corpus), Qwen2.5-Coder (8,192 to 32,768, YaRN), DeepSeek-Coder-V2 (YaRN), Code Llama long-context fine-tuning: https://arxiv.org/abs/2402.19173, https://arxiv.org/abs/2409.12186, https://arxiv.org/abs/2406.11931, https://arxiv.org/abs/2308.12950.
- OSS-Instruct starts from random open-source snippets and has an LLM write a problem and solution: https://arxiv.org/abs/2312.02120.
- Evol-Instruct (Code Evol-Instruct) evolves existing instructions into harder ones: https://arxiv.org/abs/2306.08568; the catalog entry is a community re-creation (https://huggingface.co/datasets/theblackcat102/evol-codealpaca-v1).
- KodCode: solutions and unit tests generated and kept only if the tests pass, tests for every question: https://arxiv.org/abs/2503.02951.
- OpenCodeReasoning: DeepSeek-R1 reasoning traces for competitive problems, SFT only: https://arxiv.org/abs/2504.01943.
- open-r1 CodeForces-CoTs: up to five DeepSeek R1 traces for about 10k Codeforces problems; the card says traces were not filtered for correctness (about 84% of Python ones pass public tests): https://huggingface.co/datasets/open-r1/codeforces-cots. (The page does not claim they were checked.)
- SWE-smith trajectories: 5,016 expert trajectories from Claude 3.7 Sonnet: https://arxiv.org/abs/2504.21798.
- SWE-Gym trajectories: OpenHands agent trajectories sampled on SWE-Gym tasks (GPT-4o in the paper), release includes a resolved flag: https://arxiv.org/abs/2412.21139.
- DPO needs only preference pairs and no separate reward model or RL loop: https://arxiv.org/abs/2305.18290.
- Pass/fail pairs from tests, reward models trained on them, tests synthesized by a model (GPT-4o-mini) in AceCoder: https://arxiv.org/abs/2502.01718.
- LLM-judge and reward-model preferences carry a length bias: https://arxiv.org/abs/2310.03716.
- Many recipes skip a preference stage: OpenCoder and OpenCodeReasoning are SFT only, DeepCoder goes to RL from a distilled model: https://arxiv.org/abs/2411.04905, https://arxiv.org/abs/2504.01943, https://www.together.ai/blog/deepcoder.
- GRPO uses no critic or value model and takes the baseline from group scores: https://arxiv.org/abs/2402.03300 (abstract and Figure 4).
- Groups where every sample gets the same reward give zero advantage and zero gradient, so they teach nothing: DAPO https://arxiv.org/abs/2503.14476 (dynamic sampling section); DeepCoder drops easy or unverifiable sets.
- Pass@k estimator is 1 - C(n-c,k)/C(n,k), with n = 200 and k <= 100 in the paper, and a numerically stable product form 1 - prod over i = n-c+1..n of (1 - k/i), returning 1.0 when n - c < k: https://arxiv.org/abs/2107.03374 (Figure 3). The F.passk code matches this exactly, and pass@1 = c/n.
- F.passk statement "1 solve in 5 looks very different at k = 1 and k = 10": 20% versus about 89% (arithmetic from the same formula).
- HumanEval+ exists because HumanEval tests were too weak: 80x more tests, pass@k drops 19.3 to 28.9%, rankings change: https://arxiv.org/abs/2305.01210.
- verl, TRL and SkyRL include GRPO or multi-turn RL (catalog entries verified against GitHub on 2026-11-24, not re-fetched here).
