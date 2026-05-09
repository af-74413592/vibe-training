from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from common import (
  RuntimePayloadError,
  build_base_state,
  build_env,
  coerce_command,
  command_preview,
  load_structured_file,
  make_task_paths,
  now_iso,
  parse_payload,
  write_json,
  write_state,
)


def _run_eval(step: str, payload: dict[str, Any]) -> dict[str, Any]:
  paths = make_task_paths(payload, step)
  state = build_base_state(step, payload, paths)
  write_state(paths, state)

  command_value = payload.get('command')
  if command_value is None:
    result: dict[str, Any] = {
      'step': step,
      'status': 'planned',
      'run_id': state['run_id'],
      'run_dir': str(paths.run_dir),
      'state_path': str(paths.state_path),
      'log_path': str(paths.log_path),
      'updated_at': now_iso(),
    }
    write_json(paths.result_path, result)
    return result

  command = coerce_command(command_value)
  cwd = Path(state['cwd'])
  env = build_env(payload)
  timeout = payload.get('timeout_seconds')
  timeout_value = float(timeout) if timeout is not None else None

  with paths.log_path.open('a', encoding='utf-8') as log:
    log.write(f'[{now_iso()}] {step} start: {command_preview(command)}\n')
    proc = subprocess.run(
      command,
      cwd=str(cwd),
      env=env,
      text=True,
      capture_output=True,
      timeout=timeout_value,
      check=False,
    )
    if proc.stdout:
      log.write(proc.stdout)
      if not proc.stdout.endswith('\n'):
        log.write('\n')
    if proc.stderr:
      log.write(proc.stderr)
      if not proc.stderr.endswith('\n'):
        log.write('\n')
    log.write(f'[{now_iso()}] {step} exit_code={proc.returncode}\n')

  result = {
    'step': step,
    'status': 'completed' if proc.returncode == 0 else 'failed',
    'run_id': state['run_id'],
    'run_dir': str(paths.run_dir),
    'state_path': str(paths.state_path),
    'log_path': str(paths.log_path),
    'returncode': proc.returncode,
    'command': command,
    'updated_at': now_iso(),
  }
  write_json(paths.result_path, result)
  state['status'] = result['status']
  state['returncode'] = proc.returncode
  state['updated_at'] = result['updated_at']
  write_state(paths, state)
  if proc.returncode != 0:
    raise RuntimePayloadError(
      f'{step} failed with exit code {proc.returncode}; see log: {paths.log_path}',
    )
  return result


def run_evaluation(raw_payload: str | None) -> dict[str, Any]:
  payload = parse_payload(raw_payload)
  return _run_eval('eval.run', payload)


def compare_evaluation(raw_payload: str | None) -> dict[str, Any]:
  payload = parse_payload(raw_payload)
  baseline_path = payload.get('baseline_metrics_path')
  candidate_path = payload.get('candidate_metrics_path')
  if not baseline_path or not candidate_path:
    raise RuntimePayloadError('payload.baseline_metrics_path and payload.candidate_metrics_path are required')

  baseline = load_structured_file(Path(str(baseline_path)).expanduser().resolve())
  candidate = load_structured_file(Path(str(candidate_path)).expanduser().resolve())
  comparison = {
    'step': 'eval.compare',
    'status': 'completed',
    'run_id': payload.get('run_id'),
    'baseline_metrics_path': str(Path(str(baseline_path)).expanduser().resolve()),
    'candidate_metrics_path': str(Path(str(candidate_path)).expanduser().resolve()),
    'baseline': baseline,
    'candidate': candidate,
    'updated_at': now_iso(),
  }
  return comparison
