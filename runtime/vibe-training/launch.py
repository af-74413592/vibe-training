from __future__ import annotations

import argparse
from typing import Any, Callable

from common import RuntimePayloadError, fail, ok
from data_helper import (
  build_data,
  cache_model,
  prepare_data,
  preprocess_run,
  preprocess_sample,
  trainer_smoke,
)
from eval_helper import compare_evaluation, run_evaluation
from infer_helper import run_inference, run_inference_ui
from train_helper import resume_training, start_training, stop_training, training_status


Handler = Callable[[str | None], dict[str, Any]]


COMMANDS: dict[str, Handler] = {
  'data.prepare': prepare_data,
  'data.build': build_data,
  'model.cache': cache_model,
  'preprocess.sample': preprocess_sample,
  'preprocess.run': preprocess_run,
  'trainer.smoke': trainer_smoke,
  'train.start': start_training,
  'train.resume': resume_training,
  'train.status': training_status,
  'train.stop': stop_training,
  'eval.run': run_evaluation,
  'eval.compare': compare_evaluation,
  'infer.run': run_inference,
  'infer.ui': run_inference_ui,
}


def main() -> None:
  parser = argparse.ArgumentParser(description='Vibe training runtime')
  parser.add_argument('command', help='Command name, such as train.start or eval.run')
  parser.add_argument('--payload', help='JSON payload, or @file.json to load from disk', default='{}')
  args = parser.parse_args()

  handler = COMMANDS.get(args.command)
  if handler is None:
    fail(f'Unknown command: {args.command}')

  try:
    result = handler(args.payload)
    ok(result)
  except RuntimePayloadError as err:
    fail(err.message, err.code)
  except SystemExit:
    raise
  except Exception as err:
    fail(str(err))


if __name__ == '__main__':
  main()
