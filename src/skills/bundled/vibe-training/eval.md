---
name: vibe-training-eval
description: Evaluate a training run, compare against baseline, inspect failures, assess regressions, and propose the next iteration. Use after a train run, checkpoint, adapter, or fitted model exists.
user-invocable: true
context: fork
agent: general-purpose
allowed-tools: AskUserQuestion, WebSearch, WebFetch, Read, Write, Edit, Bash, PowerShell, Glob, Grep
---

# Eval

## Goal

Decide whether the training run created real, usable improvement.

## Artifact Location

Read and write phase artifacts under `.claude/vibe-training/runs/<run_id>/`. If no run directory is known, find the latest project-local vibe-training run or create one. Do not write to `~/.claude/plans`.

## Inputs

- `run-report.md`
- Checkpoint or adapter path
- Baseline model or metrics
- Evaluation set
- Target metrics
- Benchmark design, if no suitable metric exists

## Outputs

Write or update `eval-report.md` with:

- metric comparison
- qualitative examples
- failure cases
- regression risks
- deployment recommendation
- next iteration proposal

## What To Do

1. Run offline evaluation when the user asks to execute.
2. Compare candidate metrics against baseline metrics.
3. Inspect both wins and failures.
4. Identify regressions and leakage risks.
5. Recommend continue, rollback, data iteration, hyperparameter iteration, or deployment trial.

## No Suitable Metric Or Benchmark

If no accepted metric or benchmark fits the task, create a benchmark instead of reporting a misleading score:

- define user-facing success criteria and failure categories
- create a small gold set with representative, adversarial, and edge-case examples
- define scoring rubrics, tolerance rules, and qualitative review protocol
- include baseline outputs from a simple model, previous checkpoint, heuristic, or human reference when possible
- separate benchmark construction data from training data and data-generation prompts
- add task-specific metrics or judges only when their limitations are documented
- version the benchmark and record how new cases may be added without contaminating past results

For current domain benchmarks or metrics, search maintained benchmark pages, papers, official tasks, and reference repositories before deciding to build your own.

## Question Policy

Use `AskUserQuestion` when evaluation depends on acceptance criteria: primary metric, minimum lift, regression tolerance, qualitative review needs, deployment threshold, baseline choice, whether to create a custom benchmark, and whether failures should drive data iteration or model iteration. Do not ask the user to bless results before presenting evidence.

## Do Not Do

- Do not change the training pipeline.
- Do not add new data pipeline work unless the report recommends a next iteration.
- Do not reselect the model unless evaluation shows a model-level blocker.
