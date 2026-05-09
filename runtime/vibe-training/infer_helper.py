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
  make_task_paths,
  now_iso,
  parse_payload,
  write_json,
  write_state,
)


def _run_infer(step: str, payload: dict[str, Any]) -> dict[str, Any]:
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
    state['status'] = 'planned'
    state['updated_at'] = result['updated_at']
    write_state(paths, state)
    return result

  command = coerce_command(command_value)
  cwd = Path(state['cwd'])
  env = build_env(payload)
  timeout = payload.get('timeout_seconds')
  timeout_value = float(timeout) if timeout is not None else None
  dry_run = bool(payload.get('dry_run', False))

  if dry_run:
    result = {
      'step': step,
      'status': 'dry_run',
      'run_id': state['run_id'],
      'run_dir': str(paths.run_dir),
      'state_path': str(paths.state_path),
      'log_path': str(paths.log_path),
      'command': command,
      'updated_at': now_iso(),
    }
    write_json(paths.result_path, result)
    state['status'] = 'dry_run'
    state['command'] = command
    state['updated_at'] = result['updated_at']
    write_state(paths, state)
    return result

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


def run_inference(raw_payload: str | None) -> dict[str, Any]:
  payload = parse_payload(raw_payload)
  return _run_infer('infer.run', payload)


def run_inference_ui(raw_payload: str | None) -> dict[str, Any]:
  payload = parse_payload(raw_payload)
  return _run_infer('infer.ui', payload)
