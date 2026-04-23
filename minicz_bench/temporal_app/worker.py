from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker

from minicz_bench.config import DEFAULT_MAX_PARALLEL, load_runtime_settings
from minicz_bench.temporal_app.activities import (
    load_dataset_questions_activity,
    predict_answer,
    save_artifacts_activity,
)
from minicz_bench.temporal_app.workflows import BenchmarkWorkflow


async def run_worker(max_parallel: int = DEFAULT_MAX_PARALLEL) -> None:
    settings = load_runtime_settings()
    client = await Client.connect(
        settings.temporal_address,
        namespace=settings.temporal_namespace,
        data_converter=pydantic_data_converter,
    )
    activity_executor = ThreadPoolExecutor(max_workers=max_parallel)
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[BenchmarkWorkflow],
        activities=[load_dataset_questions_activity, predict_answer, save_artifacts_activity],
        max_concurrent_activities=max_parallel,
        activity_executor=activity_executor,
    )
    try:
        await worker.run()
    finally:
        activity_executor.shutdown(wait=False, cancel_futures=True)
