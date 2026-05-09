---
name: vibe-training
description: Broad training workflow entrypoint for turning a model-building request into task routing, current research/SOTA review, reference repository discovery, a concrete implementation plan, data/training/evaluation choices, and execution. Use when the user asks to train, fine-tune, benchmark, evaluate, or build a model across ML/CV/NLP/speech/OCR/diffusion/generative modeling/recommender/time-series/RL/LLM/VLM or other learning systems.
user-invocable: true
context: inline
allowed-tools: AskUserQuestion, WebSearch, WebFetch, Read, Write, Edit, Bash, PowerShell, Glob, Grep, TodoWrite
---

# Vibe Training

## Goal

Turn a training request into a grounded workflow that chooses the right problem family first, researches the current best open approaches when needed, and then moves from plan to implementation or execution without hiding assumptions.

## Default Behavior

First decide whether the user wants research/planning only or wants an implementation/training run.

- If the user wants implementation, training, or execution: use the project-local vibe-training control flow below before editing files or launching expensive jobs.
- If the user wants research only: use the modeling/research guidance, cite sources when current claims matter, and stop with recommendations.
- If the task is tiny and obvious: implement directly, but still keep training/evaluation verification explicit.

## Project-Local Control Flow

Do not use native `EnterPlanMode` by default. Native plan mode stores plans under the user's global Claude directory and can take over the next coding steps, which hides the vibe-training phase flow.

For non-trivial work:

1. Create or reuse a project-local workflow directory: `.claude/vibe-training/runs/<run_id>/`.
2. Keep all vibe-training artifacts in that directory, not in `~/.claude/plans`. This is a run log, not a project-level skill install.
3. Write or update `state.md` before crossing phase boundaries. It must show current phase, completed phases, next action, planned file edits, commands to run, open questions, and stop conditions.
4. Use `TodoWrite` for the visible phase checklist when implementation spans multiple steps.
5. Do not patch training code, start large downloads, run GPU jobs, or launch UI/server processes until the current `state.md` gate says what will happen next.
6. If the user explicitly asks for native plan mode, you may use it, but immediately mirror the approved plan into `.claude/vibe-training/runs/<run_id>/state.md` and continue through the vibe-training gates.

Use `AskUserQuestion` at phase gates when the next action changes cost, writes many files, downloads large/private artifacts, consumes GPU time, opens a service/UI port, or locks in a user-owned tradeoff.

## Tool Attribution

Use official tools freely, but keep the vibe-training pipeline as the owner of control flow.

- `AskUserQuestion`: record the question, answer, and resulting decision in `state.md`.
- `Read`, `Glob`, `Grep`, `WebSearch`, `WebFetch`: record important evidence in the current phase artifact.
- `Write` and `Edit`: before changing code or configs, make sure `state.md` names the current phase, intended files, reason, and verification command.
- `Bash` and `PowerShell`: after running commands, record the command, exit status, key output or log path, and next action in `state.md` or the current phase report.
- `TodoWrite`: keep the visible checklist aligned with `state.md`; do not let todos become a separate hidden workflow.

Every tool action should be attributable to exactly one current vibe-training phase. If it is not clear which phase owns the action, update `state.md` before using the tool.

## Flow

Use these phases as a checklist, not a forced waterfall:

1. planning
2. modeling
3. data
4. detail
5. preprocess
6. trainer
7. train
8. eval
9. infer

Skip, compress, or merge phases that are irrelevant to the task. A simple MNIST/CNN request should become a short plan plus runnable `train.py`/`infer.py`, not a long multi-document research package.

## Visible Phase Gates

Every phase that does real work should leave a visible checkpoint in `state.md`:

- `planning`: route, scope, success metric, next phase.
- `modeling`: selected model/framework/repo route and fallback.
- `data`: data source/version/split decision, data creation pipeline if needed, and next data command.
- `detail`: framework, distributed strategy, high-availability policy, disk/time/cost budget, model cache policy, logging, validation, and compute budget.
- `preprocess`: sample command result before full preprocessing.
- `trainer`: smoke-test command, validation-set wiring, logging backend, and files patched.
- `train`: launch/resume/status commands, disk/time/cost status, and latest metrics.
- `eval`: metric comparison or custom benchmark design, regressions, and go/no-go.
- `infer`: inference command, serving/UI command, examples, and latency notes.

If a phase is skipped, record why. If execution continues automatically, still update `state.md` first so the workflow remains inspectable.

## Execution Loop

After the project-local plan or phase gate is accepted, prefer this loop:

1. Create or modify the smallest useful training/evaluation scripts.
2. Run the cheapest meaningful command: smoke test, small subset, one epoch, dry run, or config validation.
3. Read the error or metric output.
4. Patch scripts/configs.
5. Run again.
6. Record only the artifacts that help reproduce the run.

This loop is more important than producing every phase artifact. Use `plan.md`, `model-choice.md`, `dataset-spec.yaml`, `training-spec.yaml`, `preprocess-report.md`, `trainer-notes.md`, `run-report.md`, `eval-report.md`, and `infer-report.md` only when they reduce ambiguity or preserve important decisions.

## Harness Contract

Treat harness as the execution contract across `preprocess`, `trainer`, `train`, and `eval`, not as a separate document-only phase.

- `data` decides where data comes from and what versioned asset should exist.
- `detail` pins the training framework, model identifier, model revision or commit, cache directory, precision, compute budget, and command shape.
- `preprocess` runs data download/conversion scripts. Always run a tiny sample first, then full preprocessing only after schema, split, and leakage checks pass.
- `trainer` materializes model loading and training code. For Hugging Face or similar model hubs, download tokenizer/config/small required files during smoke tests when possible; download full pretrained weights only when needed to validate `from_pretrained`, adapter wiring, or the first real run. Pin revision and record cache path.
- `train` launches the real run after smoke tests pass. It may perform the full pretrained checkpoint download immediately before launch if it was not already cached.
- `eval` consumes checkpoints/adapters/fitted models and run metrics. It should not silently change the trainer.
- `infer` packages the usable path: inference script, serving wrapper, visualization UI, example inputs, and latency/throughput checks.

For large downloads, paid APIs, private data, storage-heavy jobs, or long GPU jobs, ask a user-owned question before spending the resource. For routine small scripts, run first and inspect output.

For external services and secrets, record only provider, account/project names, env var names, login status, and storage/cache paths. Never write tokens, API keys, cookies, or private credentials into `state.md`, reports, logs, commands, or code.

For SSH or external-cloud execution, treat the remote machine as the execution environment and the local repo as the control surface. Record host alias, cloud/vendor, remote workdir, sync strategy, remote artifact paths, and log retrieval commands. Do not record private keys, passwords, or one-time codes.

## Retry Contract

Retries belong to the native agent loop, but each execution phase should make retry cheap and bounded:

1. Use idempotent commands with explicit output directories.
2. Write or preserve status files, logs, and checkpoints.
3. On data/script failure, patch the nearest cause and rerun the smallest command.
4. On package installation, build, or compiler failure, capture package versions, platform, CUDA/Python versions, compiler error, and the smallest fallback path before changing frameworks.
5. On large download timeout, gated-model denial, or cache corruption, preserve URL/model id/revision/cache path and decide whether to retry, resume, mirror, or ask for credentials.
6. On CUDA/OOM/runtime failure, first reduce batch, sequence length, precision, workers, or sample size; then return to `detail` only if the budget assumptions are wrong.
7. On model/data contract failure, return to `preprocess` or `trainer`, not all the way back to planning.
8. Stop retrying when the failure requires user-owned input: missing credentials, license acceptance, unavailable GPU, ambiguous labels, or a changed success target.

## Task Routing

Start by identifying the task family. Do not assume LLM/VLM fine-tuning.

Common families include:

- classic supervised ML: tabular classification/regression, ranking, calibration
- computer vision: image classification, detection, segmentation, OCR, handwriting recognition
- speech/audio: ASR, TTS, speaker ID, audio event detection
- NLP without LLM fine-tuning: text classification, retrieval, token classification, seq2seq
- LLM/VLM: SFT, LoRA/QLoRA, preference tuning, distillation, RAG, tool-use agents
- diffusion/generative modeling: image, video, audio, 3D, style transfer, restoration, controlled generation
- recommendation/search: retrieval, ranking, candidate generation, embeddings
- time series: forecasting, anomaly detection, sequence classification
- reinforcement learning/control: policy learning, simulation, offline RL
- graph/geospatial/scientific ML: domain-specific architectures and metrics
- evaluation-only/data-only: benchmark, dataset creation, labeling, execution harness, analysis
- other/unknown/emerging: route by evidence from papers, benchmarks, repositories, and user constraints

Ask only the questions needed to route correctly: input/output shape, target metric, available data, framework preference, compute budget, deployment target, and whether the user wants code execution now.

The family list is a map, not a boundary. If the task does not fit, create a new route label and explain the evidence.

## Rules

- Keep the workflow linear after routing, unless evidence shows the route is wrong.
- Define the task before model selection.
- Research practical baselines and SOTA before committing to architecture.
- Prefer discovering the right reference implementation over relying on memorized library names.
- Choose the modeling family before committing to dataset shape.
- Put training execution and evaluation in later phases.
- When a phase needs rework, step back only to the nearest blocking phase.
- Do not manage the outer agent loop from the skill. Let Claude Code inspect results, try commands, observe failures, and continue.
- Prefer the simplest strong baseline that can satisfy the target before proposing a heavyweight model.
- For current SOTA or library/model recommendations, verify with current sources when browsing/search is available. If live research is unavailable, say that the SOTA claim needs verification and use stable baseline knowledge.
- Do not spend the whole turn calling phase skills when the user asked you to build or train something.
- Do not produce phase documents instead of code unless the user explicitly asked for documents only.
- Do not let native plan mode replace the vibe-training workflow unless the user explicitly requested native plan mode.
- Do not write vibe-training run artifacts into the user's global Claude plan directory.

## Phase Skills

- `vibe-training-planning` routes the task and can draft `plan.md` when native plan mode is not being used. It should not edit training code.
- `vibe-training-modeling` researches candidate approaches and can draft `model-choice.md`. It may inspect code and write recommendation artifacts.
- `vibe-training-data` plans and may implement source/download manifests or lightweight data scripts.
- `vibe-training-detail` can draft `training-spec.yaml` and may patch config scaffolding.
- `vibe-training-preprocess` aligns raw data to the selected training interface, runs preprocessing commands, and can draft `preprocess-report.md`.
- `vibe-training-trainer` creates, patches, and debugs training scripts/configs and can draft `trainer-notes.md`.
- `vibe-training-train` launches and monitors actual training runs and can draft `run-report.md`.
- `vibe-training-eval` runs evaluation/analysis and can draft `eval-report.md`.
- `vibe-training-infer` builds or validates inference, serving, and visualization UI flows and can draft `infer-report.md`.

## Optional Artifact Convention

- `planning` -> `plan.md`
- `modeling` -> `model-choice.md`
- `data` -> `dataset-spec.yaml`
- `detail` -> `training-spec.yaml`
- `preprocess` -> `preprocess-report.md`
- `trainer` -> `trainer-notes.md`
- `train` -> `run-report.md`
- `eval` -> `eval-report.md`
- `infer` -> `infer-report.md`

These artifacts are optional support files. For implementation requests, code, commands, metrics, and fixes are the primary outputs.

Artifact paths are relative to the project-local workflow directory, for example `.claude/vibe-training/runs/20260509-handwriting/plan.md`.

## Runtime Helper

When concrete execution is needed, prefer the bundled Python helper under `${CLAUDE_SKILL_DIR}/runtime/`. Use it as a thin command runner and status collector, not as an agent-loop replacement.

Useful command names:

- `data.prepare`
- `model.cache`
- `preprocess.sample`
- `preprocess.run`
- `trainer.smoke`
- `train.start`
- `train.resume`
- `train.status`
- `train.stop`
- `eval.run`
- `eval.compare`
- `infer.run`
- `infer.ui`
