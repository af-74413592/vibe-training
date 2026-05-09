---
name: vibe-training-infer
description: Build, validate, or package inference flows after training or evaluation, including checkpoint loading, prediction scripts, serving wrappers, latency/throughput checks, examples, and visualization UI such as Gradio, Streamlit, web UI, notebook, or CLI demos.
user-invocable: true
context: fork
agent: general-purpose
allowed-tools: AskUserQuestion, WebSearch, WebFetch, Read, Write, Edit, Bash, PowerShell, Glob, Grep
---

# Infer

## Goal

Turn a trained or selected model into a usable inference path with clear examples, reproducible loading, and an inspectable visualization or UI when useful.

## Artifact Location

Read and write phase artifacts under `.claude/vibe-training/runs/<run_id>/`. If no run directory is known, find the latest project-local vibe-training run or create one. Do not write to `~/.claude/plans`.

## Inputs

- Checkpoint, adapter, fitted model, or pretrained model path
- `training-spec.yaml`
- `eval-report.md`, when available
- Example inputs and expected outputs
- Deployment or demo target

## Outputs

Write or update `infer-report.md` only when it helps reproducibility. Prefer working inference scripts, serving wrappers, and UI demos when the user asked for implementation.

Include:

- checkpoint/model path
- preprocessing and postprocessing used at inference time
- CLI or batch inference command
- serving command, if relevant
- UI command or notebook path, if relevant
- example inputs and outputs
- latency, throughput, device, and memory notes
- known inference risks

## What To Do

1. Implement or patch the smallest useful inference entrypoint.
2. Reuse the exact preprocessing contract from training unless inference requires a documented difference.
3. Load checkpoints/adapters with pinned model IDs, revisions, and cache paths.
4. Run sample predictions and inspect outputs qualitatively.
5. Add visualization when it helps the user inspect results: Gradio, Streamlit, notebook widgets, local web UI, image overlays, audio playback, confusion examples, ranked lists, or task-specific plots.
6. For service-style use, define request/response schema, batching, streaming, timeout, device placement, and error handling.
7. Measure a small latency/throughput smoke test before claiming the inference path is usable.

## Framework Selection

Choose the inference framework by task and deployment shape, not habit:

- CLI/batch scripts for research and offline scoring.
- Gradio or Streamlit for fast visual demos.
- FastAPI or similar HTTP service for integration tests.
- vLLM, TGI, llama.cpp, ONNX Runtime, TensorRT, OpenVINO, or task-specific runtimes when serving performance or hardware portability matters.
- Custom visualization for CV/OCR/audio/diffusion/RL tasks when generic text output is not enough.

Verify current inference framework recommendations with search when performance, current model support, or deployment compatibility matters.

## Runtime Helper

When using the bundled helper, prefer:

- `infer.run` for CLI, batch, or service smoke commands.
- `infer.ui` for visualization UI launch or smoke checks.

## Question Policy

Use `AskUserQuestion` when inference depends on user-owned choices: CLI vs UI vs service, local vs server deployment, acceptable latency, batch size, visualization style, public/private demo, exposed port, model quantization, or whether a long-running UI may be launched.

## Do Not Do

- Do not retrain the model.
- Do not silently change evaluation metrics.
- Do not claim production readiness from a demo-only UI.
