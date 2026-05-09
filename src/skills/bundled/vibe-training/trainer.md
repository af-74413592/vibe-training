---
name: vibe-training-trainer
description: Implement, patch, and debug training scripts, configs, dataloaders, losses, checkpoints, logging, and smoke tests for the selected framework. Use after preprocessing alignment and before launching real training.
user-invocable: true
context: fork
agent: general-purpose
allowed-tools: AskUserQuestion, WebSearch, WebFetch, Read, Write, Edit, Bash, PowerShell, Glob, Grep
---

# Trainer

## Goal

Make the training code runnable and debuggable before spending serious compute.

## Artifact Location

Read and write phase artifacts under `.claude/vibe-training/runs/<run_id>/`. If no run directory is known, find the latest project-local vibe-training run or create one. Do not write to `~/.claude/plans`.

## Inputs

- `training-spec.yaml`
- Preprocessed sample data
- Selected reference repository or framework
- Existing project code, if any
- Target command shape

## Outputs

Write or update `trainer-notes.md` only when it helps reproduce debugging. Prefer working scripts, configs, and passing smoke tests when the user asked for implementation.

Include:

- entrypoint command
- config files
- model/target alignment notes
- external framework clone/patch notes, if applicable
- smoke-test command
- fixed errors
- unresolved blockers
- validation-set behavior
- checkpoint/logging behavior, including local logs plus Weights & Biases, TensorBoard, MLflow, CSV, JSONL, or the user's preferred backend

## What To Do

1. Create or patch the smallest useful trainer entrypoint.
2. Wire the training dataset, validation dataset, model, optimizer, scheduler, loss, metrics, checkpointing, and logging.
3. Run cheap checks: import test, config parse, one batch, one optimizer step, tiny epoch, or dry run.
4. Confirm validation is not accidentally using the train split and that validation metrics are emitted at the configured cadence.
5. Confirm logging works before long training: terminal progress plus at least one durable backend such as TensorBoard, Weights & Biases, MLflow, CSV, or JSONL.
6. Read errors and patch the code/config.
7. Stop when the trainer is ready for the train phase command.

## Model/Target Alignment

If the selected model does not exactly match the training target, adapt the architecture deliberately:

- replace or add task heads for classification, regression, detection, segmentation, ranking, value/reward modeling, sequence labeling, or generation
- train adapters, LoRA modules, projection layers, probes, control modules, or lightweight heads when full fine-tuning is unnecessary or risky
- add side encoders or auxiliary components when the task needs missing modalities or representations, such as CLIP image/text encoders, VAE encoders/decoders, audio encoders, retrieval encoders, graph encoders, or domain feature towers
- freeze/unfreeze components intentionally and record trainable parameter counts
- validate tensor shapes, loss targets, label semantics, and gradient flow with one batch before long training
- if a paper implementation requires nontrivial formulas or component rewrites, derive the needed equations in `trainer-notes.md`, map symbols to tensors/config fields, implement the smallest testable component, and add shape/unit checks before integrating it into the full trainer
- if alignment requires changing the model family or objective, return to `detail` or `modeling` instead of patching blindly

## Cloned Framework Adaptation

When using a cloned complex framework:

- pin the upstream commit and record local patch files in `trainer-notes.md`
- prefer config overrides, plugins, callbacks, adapters, and small wrapper modules before editing core framework files
- when source patches are necessary, keep them minimal, explain why config is insufficient, and add a smoke test that exercises the patched path
- do not silently overwrite upstream files or remove example configs; preserve a clear diff for review
- if install/build issues block smoke tests, capture the package, compiler, CUDA/PyTorch/Python versions, and the smallest workaround before continuing

## Pretrained Model Timing

If the route uses Hugging Face or a similar model hub:

1. Use the `model_id`, revision, auth requirement, and cache directory from `training-spec.yaml`.
2. Prefer tokenizer/config/processor downloads during early smoke tests when they are enough to validate preprocessing.
3. Download full weights in this phase only when needed to validate model construction, LoRA/adapter wiring, quantization, device placement, or a one-step smoke test.
4. If full weights are large, private, gated, or likely to consume paid bandwidth/storage, ask before downloading.
5. Record the exact command or API path used for repeatability.

## Retry Policy

- For import/config/shape errors, patch trainer code and rerun the same tiny command.
- For OOM, reduce batch size, sequence/image size, precision, workers, or sample size before changing architecture.
- For incompatible model/data contracts, return to `preprocess` for data shape fixes or `detail` for framework/model assumptions.
- For objective/model mismatch, first consider heads, adapters, projection layers, or side encoders; return to `modeling` only when the selected route is conceptually wrong.

## Runtime Helper

When using the bundled helper, prefer:

- `model.cache` for explicit tokenizer/config/full-weight cache commands.
- `trainer.smoke` for import, config, one-batch, one-step, or tiny-epoch checks.

## Question Policy

Use `AskUserQuestion` when trainer behavior depends on user-owned tradeoffs: framework compatibility, validation split ownership, checkpoint format, logging backend such as wandb or TensorBoard, Hugging Face/wandb login choice, whether to adapt a reference repo directly, package installation, or whether a smoke test may write artifacts.

## Do Not Do

- Do not launch long training.
- Do not rewrite the data plan unless the trainer exposes a hard data-contract mismatch.
- Do not report final model quality from smoke tests.
