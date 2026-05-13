---
name: vibe-training-detail
description: Turn a routed model and dataset plan into concrete training-framework choices, algorithm parameters, preprocessing contract, memory/compute estimates, and execution budget. Use before preprocessing alignment, trainer implementation, and training execution.
user-invocable: true
context: fork
agent: general-purpose
allowed-tools: AskUserQuestion, WebSearch, WebFetch, Read, Write, Edit, Bash, PowerShell, Glob, Grep
---

# Detail

## Goal

Translate the chosen route into engineering specifications for the training framework, preprocessing contract, training or fitting parameters, and evaluation.

## Artifact Location

Read and write phase artifacts under `.claude/vibe-training/runs/<run_id>/`. If no run directory is known, find the latest project-local vibe-training run or create one. Do not write to `~/.claude/plans`.

## Inputs

- `plan.md`
- `model-choice.md`
- `dataset-spec.yaml`
- Target GPU
- Target CPU or accelerator
- Training budget

## Outputs

Write or update `training-spec.yaml` with:

- preprocessing spec
- input preprocessing and augmentation
- model-specific data policy, such as tokenizer/sequence length for text or image size/normalization for vision
- training framework or library
- hyperparameter or algorithm parameter starting point
- memory/compute estimate
- disk usage estimate and cleanup policy
- duration estimate and timeout/checkpoint cadence
- cost estimate and budget stop condition
- parallelism or batching strategy
- distributed launcher, scheduler, or framework, if multi-GPU or multi-node is needed
- high-availability and recovery policy for distributed runs
- external repository integration plan, if cloning a complex training framework
- Hugging Face, Weights & Biases, dataset hub, or private registry authentication plan
- package installation and build-risk plan
- SSH/external-cloud execution plan, if training is not on the local machine
- expected artifacts
- pretrained model download policy, if the route uses a model hub

## What To Do

1. Define preprocessing for the routed task family: tokenization for text, image resizing/normalization/augmentation for vision, feature engineering for tabular, windowing for time series, spectrogram/audio transforms for speech, or environment setup for RL.
2. Define model or algorithm parameters: batch size, learning rate, epochs, regularization, optimizer, scheduler, precision, checkpoint interval, seed, tree depth, ranking loss, or other family-specific knobs.
3. Estimate CPU/GPU/accelerator memory, disk usage, runtime, throughput, and cost.
4. Decide whether framework changes are needed.
5. If multi-GPU or multi-node training is needed, define distributed strategy: single-node DDP/FSDP, DeepSpeed, Accelerate, Ray, Lightning, torchrun, Slurm/Kubernetes launcher, parameter sharding, data sharding, checkpoint format, fault tolerance, and networking assumptions.
6. Define artifact paths and logging requirements for preprocessing, trainer debugging, and training execution.
7. If using Hugging Face or a similar hub, pin `model_id`, revision, license/auth requirement, cache directory, expected disk size, and whether full weights should be downloaded during `trainer` smoke tests or deferred to `train`.

## Disk Time Cost Budget

Before execution, define:

- disk budget: dataset size, raw/intermediate/processed data, model cache, package cache, logs, checkpoints, evaluation artifacts, and reserved free space
- cleanup policy: what can be deleted, what must be preserved, checkpoint retention count, cache reuse policy, and corrupt partial download cleanup
- duration estimate: setup time, download time, preprocessing time, smoke-test time, training time per epoch/step, evaluation time, and expected wall-clock range
- timeout and stop conditions: max run time, max idle time, max failed retries, metric plateau, cost cap, and manual approval threshold
- cost estimate: GPU hourly rate or cloud quote, storage cost, egress/download cost, logging/service cost, and whether spot/preemptible pricing changes the risk
- data-generation cost estimate: API/token/media-unit cost, validation/judge calls, retry allowance, and expected accepted-sample yield
- update rule: after the first smoke test or first training interval, revise time/cost estimates from observed throughput

## External Framework And Auth Plan

When the route depends on a cloned framework or external service, specify:

- Git repository URL, branch/tag/commit, clone location, whether it is used read-only, forked, vendored, or patched in-place
- install command, Python/CUDA/PyTorch/compiler constraints, requirements.txt, editable install needs, and fallback if native extensions fail to build
- which changes should be done through configs/plugins/adapters versus direct source patches
- Hugging Face auth needs: gated model/dataset, `HF_TOKEN`, cache directory, offline mode, revision pinning, and license acceptance
- Weights & Biases or logging auth needs: `WANDB_API_KEY`, entity/project/name, online/offline/disabled mode, and where logs are stored
- download plan for large models/data: expected size, timeout/resume behavior, cache validation, mirror/proxy option, and disk quota

## SSH And External Cloud Plan

When execution happens on a remote SSH host or external cloud instance, specify:

- host alias, cloud/vendor, region/zone if relevant, GPU type/count, disk size, image/OS, and whether the machine is persistent or ephemeral
- remote workdir, artifact directory, dataset/cache locations, and cleanup policy
- code sync strategy: git branch/commit, rsync/scp, remote clone, mounted volume, or object storage handoff
- environment setup: conda/venv/container/module system, CUDA/driver versions, Python version, and package install location
- authentication surfaces by name only: SSH key alias, cloud profile, Hugging Face token env var, wandb env var, object storage credentials; never record secret values
- remote command wrapper: ssh command shape, tmux/screen/nohup/systemd/scheduler usage, port forwarding needs, and how logs/status will be fetched
- disconnect/reconnect behavior, checkpoint location, and what survives instance stop/reboot/preemption

## Distributed Reliability

For complex multi-GPU or multi-node frameworks, define high-availability and customization knobs before launch:

- launcher and scheduler: Ray, Slurm, Kubernetes, torchrun, Accelerate, DeepSpeed, Lightning, or framework-specific launchers
- node/GPU topology, rendezvous backend, ports, environment variables, NCCL settings, timeouts, and placement constraints
- checkpoint cadence, atomic checkpoint writing, sharded checkpoint format, retention policy, and resume validation
- data sharding, deterministic seeding, worker restart behavior, and partial failure handling
- logging and monitoring: per-rank logs, aggregated metrics, heartbeat/status checks, and failure alerts
- tunable parameters: batch/grad accumulation, sequence length, precision, ZeRO/FSDP stage, activation checkpointing, offload, dataloader workers, prefetch, and network-related settings

If the distributed framework itself is a major part of the task, verify current official docs or maintained examples before locking the spec.

## Question Policy

Use `AskUserQuestion` when engineering details depend on preference or resource ownership: framework choice, acceptable training time, target hardware, disk budget, cost cap, precision/quality tradeoffs, checkpoint frequency, reproducibility strictness, distributed scheduler, cluster access, SSH host/cloud account choice, failure tolerance, private/gated model access, wandb/Hugging Face account choice, and deployment packaging. Prefer making standard defaults explicit instead of asking routine hyperparameter questions.

## Do Not Do

- Do not run the training job.
- Do not make final evaluation conclusions.
- Do not redo model selection unless a hard blocker is found.
