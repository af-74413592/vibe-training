---
name: vibe-training-train
description: Launch, monitor, resume, and summarize actual training or fitting runs, including GPU/server checks, logs, checkpoints, metrics, status, and failure recovery. Use after the trainer smoke test passes.
user-invocable: true
context: fork
agent: general-purpose
allowed-tools: AskUserQuestion, WebSearch, WebFetch, Read, Write, Edit, Bash, PowerShell, Glob, Grep
---

# Train

## Goal

Run the real training job in a way that is observable, resumable, and ready for evaluation.

## Artifact Location

Read and write phase artifacts under `.claude/vibe-training/runs/<run_id>/`. If no run directory is known, find the latest project-local vibe-training run or create one. Do not write to `~/.claude/plans`.

## Inputs

- Working trainer command
- Training config
- Data paths
- Server or local runtime information
- Artifact directory
- Checkpoint and resume policy

## Outputs

Write or update `run-report.md` with:

- environment checks
- launch command
- run id
- log location
- checkpoint location
- disk usage and cleanup status
- elapsed time, ETA, and cost estimate
- latest metrics
- resume command
- distributed health and recovery status, when relevant
- SSH/remote execution status, when relevant
- auth/cache/download status for model hubs and logging services, when relevant
- failure handling notes

## What To Do

1. Check runtime environment, device availability, package versions, disk space, cost-sensitive resources, and required files.
2. Launch the agreed training command when the user asked to execute.
3. Monitor logs and metrics at useful intervals.
4. If training fails, inspect the error and return to the trainer phase only for the smallest needed fix.
5. Record checkpoints, metrics, and the command needed for evaluation or resume.

## Disk Time Cost Monitoring

Before and during training:

- check free disk before downloads, preprocessing, checkpointing, and evaluation
- record expected and observed sizes for datasets, caches, checkpoints, logs, and artifacts
- keep a checkpoint retention policy active instead of letting runs fill the disk
- track elapsed time, steps/sec or samples/sec, ETA, and remaining budget
- estimate cost from runtime, GPU count/type, cloud rate, storage, and service/logging costs when known
- include data-generation API/token/media-unit costs when the run depends on generated data
- stop or ask before crossing configured disk, time, or cost limits
- after failure, inspect whether disk-full, quota, or inode exhaustion caused the issue before changing training code

## Distributed Run Reliability

For multi-GPU or multi-node training:

- run a small distributed smoke test before the full job
- verify all ranks write logs and report metrics
- check checkpoint save/load on the intended distributed format before relying on it
- capture scheduler job id, node list, rank/world size, rendezvous settings, and relevant environment variables
- monitor heartbeat, GPU utilization, dataloader stalls, NCCL/network errors, and checkpoint age
- on failure, preserve per-rank logs and resume from the latest validated checkpoint before trying a fresh run

## Download Timing

If pretrained weights were not fully cached during `trainer`, this phase may trigger the full model download immediately before the first real run. Before doing so, confirm gated/private models, large downloads, and storage-sensitive paths. Always pin revision and record cache path in `run-report.md`.

## Service Auth And Install Failures

Before long runs, verify required external tools without exposing secrets:

- Hugging Face: login status, gated-model access, `model_id`, revision, cache path, disk space, and offline/cache-only mode if needed
- Weights & Biases or similar logging: account/project/run name, online/offline mode, resume id, and local log directory
- package install/build: Python, CUDA, PyTorch, compiler versions, editable installs, custom ops, and native extension build logs
- large file downloads: timeout/resume strategy, cache integrity, mirrors/proxies, and cleanup of corrupt partial files

## SSH And External Cloud Runs

For remote execution through SSH or cloud instances:

- verify the remote host, GPU, disk, driver, Python, and project path before launch
- sync code/data/configs intentionally and record the exact git commit or transfer command
- run long jobs inside tmux, screen, nohup, systemd, Slurm, Ray, Kubernetes, or the provider scheduler instead of relying on a fragile interactive SSH session
- record the remote command, remote log path, checkpoint path, artifact path, and the command used to fetch status/logs
- use port forwarding only when needed for dashboards or UI, and record local/remote ports without exposing credentials
- after disconnects, reconnect and inspect remote status before retrying or relaunching
- when using preemptible/spot machines, confirm checkpoint cadence and artifact sync before launch

## Retry Policy

- Retry transient network/download failures only after preserving the exact error and command.
- Resume from the latest valid checkpoint when possible.
- For deterministic script bugs, return to `trainer` and rerun a smoke test before relaunching full training.
- For OOM or throughput failures, apply the smallest runtime adjustment first; revisit `detail` only if the planned budget is invalid.
- For distributed failures, distinguish transient node/network faults from deterministic config bugs; retry/resume only after recording the failure class and affected ranks.
- For auth, install, or download failures, do not keep retrying blindly; record the exact blocker and return to `detail` or ask the user when credentials, license acceptance, mirrors, or environment changes are needed.
- For SSH/cloud failures, distinguish local SSH disconnects from remote job failure; inspect remote process/log/checkpoint state before deciding to retry.
- For disk/time/cost limit failures, clean only approved artifacts, update the budget estimate, and ask before continuing if the configured cap is exceeded.

## Question Policy

Use `AskUserQuestion` before actions that depend on operational authority: which local or remote server to use, whether to consume GPU time now, where artifacts may be written, how much disk may be used, acceptable wall-clock time, cost cap, whether long jobs may run, resume vs fresh run, whether SSH/cloud credentials are available by environment or config name, and failure-handling preference. Do not ask for permission substitutes that the native tool permission UI will already handle.

## Runtime Helper

The helper is available under `${CLAUDE_SKILL_DIR}/runtime/` when this bundled skill extracts resources.

Example shape:

```bash
python ${CLAUDE_SKILL_DIR}/runtime/launch.py train.start --payload '{"run_id":"exp-001","command":["python","train.py"],"cwd":"/path/to/project","artifact_dir":"/path/to/artifacts"}'
```

On Windows PowerShell, prefer `--payload @payload.json` because native argument parsing can strip JSON quotes.

Use the helper for command execution, status files, and JSON-shaped results. Do not put agent-loop or retry policy into the helper.

Use `model.cache` before `train.start` when a large pretrained checkpoint should be fetched or verified as a separate step.

## Do Not Do

- Do not redesign the dataset.
- Do not reselect the model unless training exposes a hard model-level blocker.
- Do not make final evaluation claims.
