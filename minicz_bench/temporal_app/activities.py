from __future__ import annotations

from temporalio import activity
from temporalio.exceptions import ApplicationError

from minicz_bench.artifacts import save_artifacts
from minicz_bench.datasets import load_questions_for_dataset
from minicz_bench.llm import NonRetryableProviderError, ProviderError, generate_completion
from minicz_bench.scoring import evaluate_prediction
from minicz_bench.schemas import (
    ArtifactInfo,
    LoadDatasetInput,
    PredictActivityInput,
    Prediction,
    QuestionLabel,
    SaveArtifactsInput,
)


@activity.defn
def load_dataset_questions_activity(input_data: LoadDatasetInput) -> list[QuestionLabel]:
    activity.logger.info("Loading dataset %s", input_data.dataset_name)
    questions = load_questions_for_dataset(input_data.dataset_name, input_data.dataset_path)
    return [
        QuestionLabel(
            dataset_name=question.dataset_name,
            item_id=question.item_id,
            answer_key=question.answer_key,
            valid_answers=question.valid_answers,
            metadata=question.metadata,
        )
        for question in questions
    ]


@activity.defn
async def predict_answer(input_data: PredictActivityInput) -> Prediction:
    question = load_questions_for_dataset(input_data.dataset_name, input_data.dataset_path)[input_data.item_id]
    try:
        response = await generate_completion(
            model=input_data.model,
            question=question,
            temperature=input_data.temperature,
            reasoning_effort=input_data.reasoning_effort,
        )
    except NonRetryableProviderError as exc:
        raise ApplicationError(str(exc), non_retryable=True) from exc
    except ProviderError as exc:
        raise ApplicationError(str(exc)) from exc

    cleaned_output, valid, correct = evaluate_prediction(question, response["raw_output"])
    return Prediction(
        dataset_name=question.dataset_name,
        item_id=question.item_id,
        raw_output=response["raw_output"],
        cleaned_output=cleaned_output,
        valid=valid,
        correct=correct,
        latency_ms=response["latency_ms"],
        prompt_tokens=response["prompt_tokens"],
        completion_tokens=response["completion_tokens"],
        total_tokens=response["total_tokens"],
        cost_usd=response["cost_usd"],
        finish_reason=response["finish_reason"],
        provider_model=response["provider_model"],
    )


@activity.defn
def save_artifacts_activity(input_data: SaveArtifactsInput) -> ArtifactInfo:
    return save_artifacts(bench_run=input_data.bench_run, output_dir=input_data.output_dir)
