from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from common import (
  RuntimePayloadError,
  build_base_state,
  build_env,
  coerce_command,
  command_preview,
  expand_path,
  load_state,
  make_task_paths,
  now_iso,
  process_alive,
  parse_payload,
  read_text_tail,
  resolve_task_paths,
  terminate_process,
  write_json,
  write_state,
)


def _start_process(step: str, payload: dict[str, Any], *, resume: bool = False) -> dict[str, Any]:
  if payload.get('run_id') or payload.get('run_dir') or payload.get('state_path'):
    paths = resolve_task_paths(payload, step)
  else:
    paths = make_task_paths(payload, step)
  state = build_base_state(step, payload, paths)
  state['status'] = 'starting'
  if resume:
    state['resume_from'] = payload.get('resume_from')
  write_state(paths, state)

  command = coerce_command(payload.get('command'))
  cwd = expand_path(payload.get('cwd'), Path(state['cwd']))
  env = build_env(payload)
  env.setdefault('VIBE_TRAIN_RUN_ID', state['run_id'])
  if resume and payload.get('resume_from'):
    env.setdefault('VIBE_TRAIN_RESUME_FROM', str(payload['resume_from']))

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
    state['updated_at'] = result['updated_at']
    write_state(paths, state)
    return result

  popen_kwargs: dict[str, Any] = {
    'cwd': str(cwd),
    'env': env,
    'stdin': subprocess.DEVNULL,
    'stdout': None,
    'stderr': subprocess.STDOUT,
    'text': True,
  }
  if os.name == 'nt':
    popen_kwargs['creationflags'] = getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0)
  else:
    popen_kwargs['start_new_session'] = True

  with paths.log_path.open('a', encoding='utf-8') as log_handle:
    popen_kwargs['stdout'] = log_handle
    proc = subprocess.Popen(command, **popen_kwargs)

  state.update(
    {
      'status': 'running',
      'pid': proc.pid,
      'command': command,
      'log_path': str(paths.log_path),
      'updated_at': now_iso(),
    },
  )
  write_state(paths, state)
  result = {
    'step': step,
    'status': 'running',
    'run_id': state['run_id'],
    'run_dir': str(paths.run_dir),
    'state_path': str(paths.state_path),
    'log_path': str(paths.log_path),
    'pid': proc.pid,
    'command': command,
    'updated_at': state['updated_at'],
  }
  write_json(paths.result_path, result)
  return result


def start_training(raw_payload: str | None) -> dict[str, Any]:
  payload = parse_payload(raw_payload)
  return _start_process('train.start', payload)


def resume_training(raw_payload: str | None) -> dict[str, Any]:
  payload = parse_payload(raw_payload)
  if payload.get('resume_from') is None:
    raise RuntimePayloadError('payload.resume_from is required for train.resume')
  return _start_process('train.resume', payload, resume=True)


def training_status(raw_payload: str | None) -> dict[str, Any]:
  payload = parse_payload(raw_payload)
  paths = resolve_task_paths(payload, 'train.start')
  state = load_state(paths)
  pid = state.get('pid')
  alive = process_alive(int(pid)) if pid is not None else False
  status = str(state.get('status') or 'unknown')
  if not alive and status == 'running':
    status = 'finished'
    state['status'] = status
    state['updated_at'] = now_iso()
    write_state(paths, state)

  result = {
    'step': 'train.status',
    'run_id': state.get('run_id'),
    'status': status,
    'pid': pid,
    'alive': alive,
    'run_dir': str(paths.run_dir),
    'state_path': str(paths.state_path),
    'log_path': str(paths.log_path),
    'log_tail': read_text_tail(paths.log_path),
    'updated_at': now_iso(),
  }
  write_json(paths.result_path, result)
  return result


def stop_training(raw_payload: str | None) -> dict[str, Any]:
  payload = parse_payload(raw_payload)
  paths = resolve_task_paths(payload, 'train.start')
  state = load_state(paths)
  pid = state.get('pid')
  if pid is None:
    return {
      'step': 'train.stop',
      'run_id': state.get('run_id'),
      'status': 'not_running',
      'run_dir': str(paths.run_dir),
      'state_path': str(paths.state_path),
      'log_path': str(paths.log_path),
      'updated_at': now_iso(),
    }
  stopped = terminate_process(int(pid))
  state['status'] = 'stopped' if stopped else 'unknown'
  state['updated_at'] = now_iso()
  write_state(paths, state)
  result = {
    'step': 'train.stop',
    'run_id': state.get('run_id'),
    'status': state['status'],
    'pid': pid,
    'stopped': stopped,
    'run_dir': str(paths.run_dir),
    'state_path': str(paths.state_path),
    'log_path': str(paths.log_path),
    'updated_at': state['updated_at'],
  }
  write_json(paths.result_path, result)
  return result
