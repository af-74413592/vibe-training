---
name: vibe-training-preprocess
description: Align raw or sourced data to the selected training interface by implementing or validating preprocessing, conversion, split files, schema checks, leakage checks, and small sample sanity tests. Use after dataset-spec.yaml and training-spec.yaml exist, before trainer debugging.
user-invocable: true
context: fork
agent: general-purpose
allowed-tools: AskUserQuestion, Read, Write, Edit, Bash, PowerShell, Glob, Grep
---

# Preprocess

## Goal

Turn the planned data asset into train-ready inputs that match the model, tokenizer, processor, feature schema, or dataset API chosen in the detail phase.

## Artifact Location

Read and write phase artifacts under `.claude/vibe-training/runs/<run_id>/`. If no run directory is known, find the latest project-local vibe-training run or create one. Do not write to `~/.claude/plans`.

## Inputs

- `dataset-spec.yaml`
- `training-spec.yaml`
- Raw data or source paths
- Expected model input/output contract
- Split policy and leakage constraints

## Outputs

Write or update `preprocess-report.md` only when it helps reproducibility. Prefer actual preprocessing scripts, configs, and sanity-check outputs when the user asked for implementation.

Include:

- source paths and output paths
- conversion or normalization steps
- cleaning and secondary alignment steps
- split counts
- schema or shape checks
- sample inspection notes
- known data risks

## What To Do

1. Implement or patch preprocessing code that converts raw data into the training format.
2. Apply planned cleaning and secondary alignment rules when needed.
3. Validate a tiny sample before processing the full dataset.
4. Check schema, label space, tensor shapes, tokenizer fields, image sizes, audio lengths, or feature columns.
5. Verify train/validation/test splits and leakage guards.
6. Produce small artifacts that the trainer phase can consume immediately.
7. Run full preprocessing only after the sample path passes, unless the dataset is already tiny.

## Cleaning And Alignment Checks

When cleaning or secondary alignment is used:

- report before/after counts, rejection reasons, class balance changes, and split counts
- preserve raw-to-cleaned/aligned traceability through ids or manifests
- run sample inspection on accepted and rejected examples
- validate label remaps and multimodal pairings with small deterministic checks
- stop and return to `data` when cleaning rules change the task definition or discard too much useful data

## Retry Policy

- If a data command fails, inspect the exact error and rerun the smallest failing sample command after patching.
- If output already exists, prefer checksum/count/schema validation before overwriting.
- If the failure is missing credentials, license acceptance, private data access, or ambiguous labels, ask the user instead of guessing.

## Runtime Helper

When using the bundled helper, prefer:

- `preprocess.sample` for tiny sample conversion and schema checks.
- `preprocess.run` for full conversion after sample validation passes.

## Question Policy

Use `AskUserQuestion` when preprocessing depends on user-owned decisions: data location, license/privacy constraints, label policy, split policy, ambiguous labels, destructive overwrite, or whether expensive preprocessing may run now.

## Do Not Do

- Do not choose a new model family unless preprocessing proves the selected route impossible.
- Do not run a full training job.
- Do not make final evaluation claims.
