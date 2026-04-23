from __future__ import annotations

import argparse
import asyncio
import json
import re
from pathlib import Path

from .config import (
    DATASETS_BY_SIZE,
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_MAX_PARALLEL,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REASONING_EFFORT,
    slugify_model_name,
)
from .temporal_app.client import run_benchmark
from .temporal_app.worker import run_worker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="minicz-bench")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a benchmark workflow.")
    run_parser.add_argument("--model", required=True, help="OpenRouter model id, e.g. openrouter/openai/gpt-4o-mini")
    run_parser.add_argument("--data-size", choices=sorted(DATASETS_BY_SIZE), default="mini")
    run_parser.add_argument("--max-parallel", type=int, default=DEFAULT_MAX_PARALLEL)
    run_parser.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS)
    run_parser.add_argument("--reasoning-effort", default=DEFAULT_REASONING_EFFORT,
                            choices=["none", "minimal", "low", "medium", "high"])
    run_parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))

    worker_parser = subparsers.add_parser("worker", help="Run the Temporal worker.")
    worker_parser.add_argument("--max-parallel", type=int, default=DEFAULT_MAX_PARALLEL)

    list_parser = subparsers.add_parser("list-artifacts", help="List JSON sidecars in bench_runs.")
    list_parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))

    status_parser = subparsers.add_parser("status", help="Show done/pending models.")
    status_parser.add_argument("--models", required=True, help="Path to model list (.md table or plain text, one per line)")
    status_parser.add_argument("--data-size", choices=sorted(DATASETS_BY_SIZE), default="mini")
    status_parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser


async def _run_command(args: argparse.Namespace) -> int:
    result = await run_benchmark(
        model=args.model,
        data_size=args.data_size,
        max_parallel=args.max_parallel,
        max_attempts=args.max_attempts,
        reasoning_effort=args.reasoning_effort,
        output_dir=args.output_dir,
    )
    print(f"Run: {result.bench_run.run_name}")
    for dataset_name, dataset_result in result.bench_run.dataset_results.items():
        print(
            f"{dataset_name}: accuracy={dataset_result.accuracy:.3f} "
            f"validity={dataset_result.validity:.3f} "
            f"cost_usd={dataset_result.cost_usd:.6f} "
            f"duration_s={dataset_result.duration_s:.2f}"
        )
    print(
        f"total: cost_usd={result.bench_run.totals.cost_usd:.6f} "
        f"duration_s={result.bench_run.totals.duration_s:.2f}"
    )
    if result.artifact_info.pickle_path:
        print(f"pickle: {result.artifact_info.pickle_path}")
    if result.artifact_info.json_path:
        print(f"json: {result.artifact_info.json_path}")
    return 0


def _list_artifacts(output_dir: str) -> int:
    target_dir = Path(output_dir)
    if not target_dir.exists():
        print(f"No artifact directory found at {target_dir}")
        return 0

    json_files = sorted(target_dir.glob("*.json"))
    if not json_files:
        print(f"No JSON artefacts found in {target_dir}")
        return 0

    for path in json_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        totals = payload.get("totals", {})
        print(
            f"{path.name}: model={payload.get('model')} "
            f"cost_usd={totals.get('cost_usd', 0):.6f} "
            f"duration_s={totals.get('duration_s', 0):.2f}"
        )
    return 0


def _parse_model_list(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        return re.findall(r"^\|\s*`([^`]+/[^`]+)`", text, re.MULTILINE)
    return [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]


def _status_command(models_path: str, data_size: str, output_dir: str) -> int:
    model_list = _parse_model_list(Path(models_path))
    if not model_list:
        print(f"No models found in {models_path}")
        return 1

    target_dir = Path(output_dir)
    done = 0
    for model in model_list:
        slug = slugify_model_name(model)
        pattern = f"{slug}_{data_size}_*"
        matches = sorted(target_dir.glob(pattern))
        if matches:
            done += 1
            artifact = matches[-1].name
            print(f"[done]    {model:<50s} ({artifact})")
        else:
            print(f"[PENDING] {model}")

    print(f"\n{done} / {len(model_list)} done")
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        raise SystemExit(asyncio.run(_run_command(args)))
    if args.command == "worker":
        raise SystemExit(asyncio.run(run_worker(max_parallel=args.max_parallel)))
    if args.command == "list-artifacts":
        raise SystemExit(_list_artifacts(output_dir=args.output_dir))
    if args.command == "status":
        raise SystemExit(_status_command(models_path=args.models, data_size=args.data_size, output_dir=args.output_dir))

    raise SystemExit(parser.format_help())
