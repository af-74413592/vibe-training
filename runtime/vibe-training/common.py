from __future__ import annotations

import json
import os
import shlex
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
  import psutil  # type: ignore
except Exception:  # pragma: no cover - optional dependency
  psutil = None

try:
  import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
  yaml = None


class RuntimePayloadError(Exception):
  def __init__(self, message: str, code: str = 'runtime_error') -> None:
    super().__init__(message)
    self.message = message
    self.code = code


TRACKED_PAYLOAD_FIELDS = (
  'phase',
  'workflow_dir',
  'phase_file',
  'attempt',
  'retry_of',
  'model_id',
  'model_revision',
  'revision',
  'cache_dir',
  'input_path',
  'output_path',
  'sample_size',
  'metrics_path',
  'checkpoint_path',
  'model_path',
  'adapter_path',
  'example_input',
  'endpoint',
  'port',
  'ui_url',
  'visualization_path',
  'resume_from',
)


@dataclass(frozen=True)
class TaskPaths:
  root: Path
  run_dir: Path
  state_path: Path
  log_path: Path
  result_path: Path


def emit_json(payload: dict[str, Any]) -> None:
  sys.stdout.write(json.dumps(payload, ensure_ascii=False))
  sys.stdout.write('\n')
  sys.stdout.flush()


def ok(result: Any) -> None:
  emit_json({'ok': True, 'result': result})


def fail(message: str, code: str = 'runtime_error', exit_code: int = 1) -> None:
  emit_json({'ok': False, 'error': {'code': code, 'message': message}})
  raise SystemExit(exit_code)


def now_iso() -> str:
  return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def parse_payload(raw: str | None) -> dict[str, Any]:
  if raw is None:
    return {}
  text = raw.strip()
  if not text:
    return {}
  if text.startswith('@'):
    text = Path(text[1:]).read_text(encoding='utf-8')
  parsed = json.loads(text)
  if not isinstance(parsed, dict):
    raise RuntimePayloadError('payload must be a JSON object')
  return parsed


def coerce_command(value: Any) -> list[str]:
  if isinstance(value, list):
    command = [str(part) for part in value if str(part).strip()]
    if not command:
      raise RuntimePayloadError('command list is empty')
    return command
  if isinstance(value, str):
    command = shlex.split(value)
    if not command:
      raise RuntimePayloadError('command string is empty')
    return command
  raise RuntimePayloadError('payload.command must be a string or list of strings')


def expand_path(value: Any, fallback: Path) -> Path:
  if value is None or value == '':
    return fallback
  return Path(str(value)).expanduser().resolve()


def default_artifact_root(cwd: Path | None = None) -> Path:
  base = cwd or Path.cwd()
  return (base / 'artifacts' / 'vibe-training').resolve()


def get_run_id(payload: dict[str, Any]) -> str:
  run_id = payload.get('run_id')
  if run_id:
    return str(run_id)
  return time.strftime('run-%Y%m%d-%H%M%S', time.localtime())


def make_task_paths(payload: dict[str, Any], step_name: str) -> TaskPaths:
  cwd = expand_path(payload.get('cwd'), Path.cwd())
  root = expand_path(payload.get('artifact_dir'), default_artifact_root(cwd))
  run_dir = root / 'runs' / get_run_id(payload) / step_name
  run_dir.mkdir(parents=True, exist_ok=True)
  return TaskPaths(
    root=root,
    run_dir=run_dir,
    state_path=run_dir / 'state.json',
    log_path=run_dir / 'task.log',
    result_path=run_dir / 'result.json',
  )


def resolve_task_paths(payload: dict[str, Any], step_name: str) -> TaskPaths:
  cwd = expand_path(payload.get('cwd'), Path.cwd())
  root = expand_path(payload.get('artifact_dir'), default_artifact_root(cwd))
  run_id = payload.get('run_id')
  state_path = payload.get('state_path')
  run_dir = payload.get('run_dir')

  if state_path:
    state_file = Path(str(state_path)).expanduser().resolve()
    resolved_run_dir = state_file.parent
    return TaskPaths(
      root=root,
      run_dir=resolved_run_dir,
      state_path=state_file,
      log_path=resolved_run_dir / 'task.log',
      result_path=resolved_run_dir / 'result.json',
    )

  if run_dir:
    resolved_run_dir = Path(str(run_dir)).expanduser().resolve()
    return TaskPaths(
      root=root,
      run_dir=resolved_run_dir,
      state_path=resolved_run_dir / 'state.json',
      log_path=resolved_run_dir / 'task.log',
      result_path=resolved_run_dir / 'result.json',
    )

  if not run_id:
    raise RuntimePayloadError(
      'payload.run_id, payload.run_dir, or payload.state_path is required',
    )

  resolved_run_dir = root / 'runs' / str(run_id) / step_name
  return TaskPaths(
    root=root,
    run_dir=resolved_run_dir,
    state_path=resolved_run_dir / 'state.json',
    log_path=resolved_run_dir / 'task.log',
    result_path=resolved_run_dir / 'result.json',
  )


def ensure_parent(path: Path) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: Any) -> None:
  ensure_parent(path)
  path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def read_json(path: Path, default: Any = None) -> Any:
  if not path.exists():
    return default
  return json.loads(path.read_text(encoding='utf-8'))


def load_structured_file(path: Path) -> Any:
  text = path.read_text(encoding='utf-8')
  if path.suffix.lower() in {'.yml', '.yaml'}:
    if yaml is None:
      raise RuntimePayloadError('PyYAML is required to read YAML files')
    return yaml.safe_load(text)
  return json.loads(text)


def write_state(paths: TaskPaths, state: dict[str, Any]) -> None:
  write_json(paths.state_path, state)


def load_state(paths: TaskPaths) -> dict[str, Any]:
  state = read_json(paths.state_path, {})
  if not isinstance(state, dict):
    raise RuntimePayloadError('task state file is invalid')
  return state


def build_base_state(step: str, payload: dict[str, Any], paths: TaskPaths) -> dict[str, Any]:
  cwd = expand_path(payload.get('cwd'), Path.cwd())
  state = {
    'step': step,
    'run_id': get_run_id(payload),
    'cwd': str(cwd),
    'artifact_dir': str(paths.root),
    'created_at': now_iso(),
    'updated_at': now_iso(),
  }
  metadata = {
    key: payload[key]
    for key in TRACKED_PAYLOAD_FIELDS
    if key in payload and payload[key] is not None
  }
  if metadata:
    state['metadata'] = metadata
  return state


def build_env(payload: dict[str, Any]) -> dict[str, str]:
  env = dict(os.environ)
  extra = payload.get('env')
  if isinstance(extra, dict):
    for key, value in extra.items():
      env[str(key)] = str(value)
  return env


def process_alive(pid: int | None) -> bool:
  if pid is None or pid <= 0:
    return False
  if psutil is not None:
    try:
      proc = psutil.Process(pid)
      return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
    except Exception:
      return False
  try:
    os.kill(pid, 0)
    return True
  except Exception:
    return False


def terminate_process(pid: int | None) -> bool:
  if pid is None or pid <= 0:
    return False
  if psutil is not None:
    try:
      proc = psutil.Process(pid)
      children = proc.children(recursive=True)
      for child in children:
        try:
          child.terminate()
        except Exception:
          pass
      proc.terminate()
      gone, alive = psutil.wait_procs([proc, *children], timeout=5)
      for still_alive in alive:
        try:
          still_alive.kill()
        except Exception:
          pass
      return True
    except Exception:
      return False
  try:
    if os.name == 'nt':
      subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], check=False, capture_output=True)
    else:
      os.kill(pid, signal.SIGTERM)
    return True
  except Exception:
    return False


def command_preview(command: list[str]) -> str:
  return ' '.join(shlex.quote(part) for part in command)


def read_text_tail(path: Path, max_chars: int = 4000) -> str:
  if not path.exists():
    return ''
  with path.open('rb') as handle:
    handle.seek(0, os.SEEK_END)
    size = handle.tell()
    handle.seek(max(0, size - max_chars))
    data = handle.read()
  return data.decode('utf-8', errors='replace')
