from __future__ import annotations

import gzip
import json
import pickle
from pathlib import Path

import pandas as pd

from .schemas import ArtifactInfo, BenchRun


def _legacy_payload(bench_run: BenchRun) -> dict:
    dataset_results = bench_run.dataset_results
    return {
        "model": bench_run.model,
        "datasets": bench_run.datasets,
        "raw_outputs": {name: result.raw_outputs for name, result in dataset_results.items()},
        "dfs": {name: pd.DataFrame(result.rows) for name, result in dataset_results.items()},
        "metrics": bench_run.metrics,
        "timing_results": bench_run.timing_results,
        "cost_usd": {
            **bench_run.cost_usd,
            "total": bench_run.totals.cost_usd,
        },
        "token_usage": {
            **bench_run.token_usage,
            "total": bench_run.totals.token_usage.model_dump(),
        },
        "run_started_at": bench_run.run_started_at.isoformat(),
        "run_finished_at": bench_run.run_finished_at.isoformat(),
        "max_parallel": bench_run.max_parallel,
        "max_attempts": bench_run.max_attempts,
        "message_strategy": bench_run.message_strategy,
        "pipeline_type": bench_run.pipeline_type,
    }


def _json_payload(bench_run: BenchRun) -> dict:
    return {
        "model": bench_run.model,
        "data_size": bench_run.data_size,
        "run_name": bench_run.run_name,
        "datasets": bench_run.datasets,
        "metrics": {
            name: {
                "validity": result.validity,
                "accuracy": result.accuracy,
                "duration_s": result.duration_s,
                "cost_usd": result.cost_usd,
                "token_usage": result.token_usage.model_dump(),
            }
            for name, result in bench_run.dataset_results.items()
        },
        "totals": {
            "duration_s": bench_run.totals.duration_s,
            "cost_usd": bench_run.totals.cost_usd,
            "token_usage": bench_run.totals.token_usage.model_dump(),
        },
        "run_started_at": bench_run.run_started_at.isoformat(),
        "run_finished_at": bench_run.run_finished_at.isoformat(),
        "max_parallel": bench_run.max_parallel,
        "max_attempts": bench_run.max_attempts,
    }


def save_artifacts(bench_run: BenchRun, output_dir: str | None) -> ArtifactInfo:
    if not output_dir:
        return ArtifactInfo()

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    pickle_path = target_dir / f"{bench_run.run_name}.pkl.gz"
    json_path = target_dir / f"{bench_run.run_name}.json"

    with gzip.open(pickle_path, "wb") as file:
        pickle.dump(_legacy_payload(bench_run), file)

    json_path.write_text(json.dumps(_json_payload(bench_run), indent=2, sort_keys=True), encoding="utf-8")

    return ArtifactInfo(pickle_path=str(pickle_path), json_path=str(json_path))
