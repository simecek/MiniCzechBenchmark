from __future__ import annotations

from datetime import datetime, timezone

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from minicz_bench.config import (
    DEFAULT_MESSAGE_STRATEGY,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PIPELINE_TYPE,
    DEFAULT_REASONING_EFFORT,
    build_run_name,
    get_datasets_for_size,
    load_runtime_settings,
)
from minicz_bench.schemas import BenchmarkWorkflowResult, WorkflowInput
from minicz_bench.temporal_app.workflows import BenchmarkWorkflow


async def run_benchmark(
    model: str,
    data_size: str,
    max_parallel: int,
    max_attempts: int,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
    output_dir: str | None = str(DEFAULT_OUTPUT_DIR),
) -> BenchmarkWorkflowResult:
    settings = load_runtime_settings()
    datasets = get_datasets_for_size(data_size)
    run_name = build_run_name(model=model, data_size=data_size)
    run_started_at = datetime.now(timezone.utc)

    client = await Client.connect(
        settings.temporal_address,
        namespace=settings.temporal_namespace,
        data_converter=pydantic_data_converter,
    )
    workflow_input = WorkflowInput(
        model=model,
        data_size=data_size,
        datasets=datasets,
        run_name=run_name,
        output_dir=output_dir,
        run_started_at=run_started_at,
        max_parallel=max_parallel,
        max_attempts=max_attempts,
        reasoning_effort=reasoning_effort,
        message_strategy=DEFAULT_MESSAGE_STRATEGY,
        pipeline_type=DEFAULT_PIPELINE_TYPE,
    )
    handle = await client.start_workflow(
        BenchmarkWorkflow.run,
        workflow_input,
        id=f"minicz-bench-{run_name}-{int(run_started_at.timestamp())}",
        task_queue=settings.temporal_task_queue,
    )
    return await handle.result()
