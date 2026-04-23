from __future__ import annotations

import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from minicz_bench.config import DEFAULT_REASONING_EFFORT, DEFAULT_TEMPERATURE
    from minicz_bench.scoring import build_dataset_result
    from minicz_bench.schemas import (
        BenchmarkWorkflowResult,
        BenchRun,
        DatasetResult,
        LoadDatasetInput,
        Prediction,
        PredictActivityInput,
        QuestionLabel,
        RunTotals,
        SaveArtifactsInput,
        TokenUsage,
        WorkflowInput,
    )
    from minicz_bench.temporal_app.activities import (
        load_dataset_questions_activity,
        predict_answer,
        save_artifacts_activity,
    )


def _retry_policy(max_attempts: int) -> RetryPolicy:
    return RetryPolicy(
        initial_interval=timedelta(seconds=1),
        backoff_coefficient=2.0,
        maximum_interval=timedelta(seconds=30),
        maximum_attempts=max_attempts,
    )


@workflow.defn
class BenchmarkWorkflow:
    @workflow.run
    async def run(self, input_data: WorkflowInput) -> BenchmarkWorkflowResult:
        dataset_tasks = [
            self._evaluate_dataset(
                dataset_name=dataset_name,
                source_dataset=input_data.datasets[dataset_name],
                model=input_data.model,
                max_attempts=input_data.max_attempts,
                reasoning_effort=input_data.reasoning_effort,
            )
            for dataset_name in input_data.datasets
        ]
        dataset_results_list = await asyncio.gather(*dataset_tasks)
        dataset_results: dict[str, DatasetResult] = {
            result.dataset_name: result for result in dataset_results_list
        }

        metrics = {
            name: (result.validity, result.accuracy)
            for name, result in dataset_results.items()
        }
        timing_results = {
            name: result.duration_s
            for name, result in dataset_results.items()
        }
        cost_usd = {
            name: result.cost_usd
            for name, result in dataset_results.items()
        }
        token_usage = {
            name: result.token_usage.model_dump()
            for name, result in dataset_results.items()
        }

        run_finished_at = workflow.now()
        totals = RunTotals(
            duration_s=(run_finished_at - input_data.run_started_at).total_seconds(),
            cost_usd=sum(result.cost_usd for result in dataset_results.values()),
            token_usage=TokenUsage(
                prompt_tokens=sum(result.token_usage.prompt_tokens for result in dataset_results.values()),
                completion_tokens=sum(
                    result.token_usage.completion_tokens for result in dataset_results.values()
                ),
                total_tokens=sum(result.token_usage.total_tokens for result in dataset_results.values()),
            ),
        )

        bench_run = BenchRun(
            model=input_data.model,
            data_size=input_data.data_size,
            run_name=input_data.run_name,
            datasets=input_data.datasets,
            dataset_results=dataset_results,
            metrics=metrics,
            timing_results=timing_results,
            cost_usd=cost_usd,
            token_usage=token_usage,
            run_started_at=input_data.run_started_at,
            run_finished_at=run_finished_at,
            max_parallel=input_data.max_parallel,
            max_attempts=input_data.max_attempts,
            message_strategy=input_data.message_strategy,
            pipeline_type=input_data.pipeline_type,
            totals=totals,
        )

        artifact_info = await workflow.execute_activity(
            save_artifacts_activity,
            SaveArtifactsInput(bench_run=bench_run, output_dir=input_data.output_dir),
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=_retry_policy(input_data.max_attempts),
        )
        return BenchmarkWorkflowResult(bench_run=bench_run, artifact_info=artifact_info)

    async def _evaluate_dataset(
        self,
        dataset_name: str,
        source_dataset: str,
        model: str,
        max_attempts: int,
        reasoning_effort: str = DEFAULT_REASONING_EFFORT,
    ) -> DatasetResult:
        started_at = workflow.now()
        raw_labels = await workflow.execute_activity(
            load_dataset_questions_activity,
            LoadDatasetInput(dataset_name=dataset_name, dataset_path=source_dataset),
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=_retry_policy(max_attempts),
        )
        labels = [QuestionLabel.model_validate(label) for label in raw_labels]
        raw_predictions = await asyncio.gather(
            *[
                workflow.execute_activity(
                    predict_answer,
                    PredictActivityInput(
                        model=model,
                        dataset_name=dataset_name,
                        dataset_path=source_dataset,
                        item_id=label.item_id,
                        temperature=DEFAULT_TEMPERATURE,
                        reasoning_effort=reasoning_effort,
                    ),
                    start_to_close_timeout=timedelta(minutes=10),
                    retry_policy=_retry_policy(max_attempts),
                )
                for label in labels
            ]
        )
        predictions = [Prediction.model_validate(prediction) for prediction in raw_predictions]
        finished_at = workflow.now()
        return build_dataset_result(
            dataset_name=dataset_name,
            source_dataset=source_dataset,
            questions=labels,
            predictions=predictions,
            duration_s=(finished_at - started_at).total_seconds(),
        )
