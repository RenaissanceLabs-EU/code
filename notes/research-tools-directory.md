# Research notes: tools directory and setups (2026-11-25)

Files: data/tools-directory.json (54 tools, 7 roles), data/setups.json (2 setups).
Counts per role: collection 6, processing 10, tokenization 4, training 14 (includes vLLM and SGLang), tracking 5, execution 8, evaluation 7. This is above the "about 35" target because the brief listed every tool by name.

Method: versions and dates from the PyPI JSON API (upload time of the latest release) or the GitHub releases API; licenses from PyPI metadata, repository LICENSE/NOTICE files or the GitHub license field; install lines and quickstart commands from READMEs and docs fetched on 2026-11-25. Nothing was installed or run.

## Things worth knowing
- Catalog duplicates: the catalog has both fw-verl and verl, and both fw-skyrl and skyrl (old and new GitHub orgs). The directory uses verl and skyrl with the new URLs (verl-project/verl, skyrl-project/SkyRL).
- Project versions have moved a lot: transformers 5.24.1, TRL 1.18.2, peft 0.22.0, datasets 5.2.0. The local environment (transformers 4.57.3, peft 0.17.1, datasets 4.5.0) is older than TRL's floors for datasets (>=4.7.0) and peft (>=0.18.0).
- On Python 3.9.6 pip offers TRL only up to 0.24.0 (checked with pip index versions), which confirms the Python 3.11 floor.
- LLaMA-Factory (datasets<=4.0.0, peft<=0.18.1, accelerate<=1.11.0), Axolotl (exact pins) and OpenRLHF (deepspeed==0.19.6) conflict with current TRL, so the setups say one environment per framework.
- torchtune's README says it is no longer actively maintained; go-license-detector last pushed 2023-06-09; detect-secrets last release 2024-05-06; EvalPlus last release 2024-10-20; bigcode-evaluation-harness last release 2023-05-25. They are listed with that stated in "when".
- Software Heritage documentation returned HTTP 403 to a scripted browser user agent and pointed to its users ethical charter; plain curl worked for docs pages. Bulk access should follow the charter.
- Releases are null for repositories without releases or packages (bigcode-dataset, livecodebench, gh-archive, git-github-api); the entry says why.

## Not verified
- Software Heritage graph size and the vault usage limits; the scale value "cluster" for it is a judgment. swh-vault was read only through the docs navigation (cookers list), not its usage pages, so the vault sentence is limited to what cookers exist.
- gVisor, Firecracker and Apptainer install commands (install is null); their quick-start and install pages were not read. Only the READMEs and, for Apptainer, the security page were read.
- Firecracker, E2B and Modal isolation: stated as each project's own docs word it (KVM microVMs; "isolated Linux VM"; gVisor or VM runtime). No independent security assessment. SandboxFusion's docs say "secure sandbox" but give no isolation guarantee; its source shows tmpfs overlayfs and cgroups.
- E2B and Modal need accounts and API keys; pricing and quotas were not checked.
- Multi-GPU support for Unsloth (scale marked single-gpu from the README's single-GPU focus, not from a statement that multi-GPU is unsupported).
- GitHub REST API rate-limit numbers (the page was only used to confirm that primary limits depend on authentication).
- mlflow install line: the README shows uvx mlflow server; pip install mlflow is the standard PyPI name, not a README quote.
- tokenizers README says pip install --pre tokenizers; the directory uses the plain command because stable 0.23.3 is on PyPI.
- DeepSeek-Coder FIM tokens (tokenizer_config had none in added tokens; not included). Only StarCoder2 and Qwen2.5-Coder FIM tokens are listed, from their tokenizer_config.json.
- The setups were not executed (no GPUs, installs forbidden). The EvalPlus samples filename in the local setup follows the README's naming convention and may differ from what codegen writes. The Slurm scripts are condensed from the Accelerate examples. The SandboxFusion curl host (localhost:8080) is inferred from the docker -p mapping.
- Dependency compatibility of the full stack was checked by comparing declared requires_dist ranges, not by running pip's resolver; transitive pins (for example vLLM's torch pin against TRL's torch>=2.6.0) were not resolved.
- Maturity labels (established, emerging, experimental) and scale labels are editorial judgments from project age, release cadence and README statements.
