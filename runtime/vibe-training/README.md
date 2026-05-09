# Vibe Training Runtime

This directory contains the thin Python execution layer for vibe-training.

It records commands, logs, status, and artifacts. It does not contain the agent loop, model-specific training logic, or retry policy decisions.

## Entry

```bash
python launch.py train.start --payload '{"run_id":"exp-001","command":["python","train.py"],"cwd":"/path/to/project","artifact_dir":"/path/to/artifacts"}'
```

On Windows PowerShell, prefer a payload file to avoid JSON quote stripping:

```powershell
python launch.py trainer.smoke --payload '@payload.json'
```

## Commands

- `data.prepare`
- `data.build`
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

## Payload

Common fields:

- `run_id`
- `cwd`
- `artifact_dir`
- `env`
- `command`
- `timeout_seconds`
- `dry_run`
- `attempt`
- `retry_of`
- `workflow_dir`
- `phase_file`
- `model_id`
- `revision`
- `cache_dir`
- `input_path`
- `output_path`
- `sample_size`
- `model_path`
- `adapter_path`
- `example_input`
- `endpoint`
- `port`
- `ui_url`
- `visualization_path`

Comparison fields:

- `baseline_metrics_path`
- `candidate_metrics_path`

## Intended phase mapping

- `data.prepare`: source check, manifest generation, or lightweight download probe.
- `model.cache`: optional pretrained model/tokenizer/cache command. Use before trainer smoke tests or immediately before training.
- `preprocess.sample`: run preprocessing on a tiny sample and inspect schema/shape/counts.
- `preprocess.run`: run full preprocessing after the sample path passes.
- `trainer.smoke`: import/config/one-batch/one-step/tiny-epoch checks.
- `train.start`: launch the real long-running train command.
- `eval.run`: run evaluation scripts against a checkpoint, adapter, or fitted model.
- `infer.run`: run CLI, batch, or service smoke inference commands.
- `infer.ui`: run or smoke-check visualization UI commands.

## Retry metadata

The helper does not decide retry policy. Pass fields such as `attempt`, `retry_of`, `resume_from`, `model_id`, `revision`, and `cache_dir` so logs and state files explain what the agent tried.

## Result shape

```json
{"ok": true, "result": {...}}
```

Errors:

```json
{"ok": false, "error": {"code": "runtime_error", "message": "..." }}
```
