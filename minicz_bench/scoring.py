from __future__ import annotations

from collections.abc import Iterable

from .schemas import DatasetResult, Prediction, Question, QuestionLabel, TokenUsage


def clean_output(raw_output: str) -> str:
    return raw_output[:3].strip().replace(")", "").replace(".", "")


def evaluate_prediction(question: Question, raw_output: str) -> tuple[str, bool, bool]:
    cleaned = clean_output(raw_output)
    candidate = cleaned.lower() if question.dataset_name == "klokanek" else cleaned
    valid = candidate in question.valid_answers
    correct = valid and candidate == question.answer_key
    return candidate, valid, correct


def _legacy_row(question: QuestionLabel, prediction: Prediction) -> dict:
    if question.dataset_name == "agree":
        row = {"correct_answer_minus_1": question.metadata["correct_answer_minus_1"]}
    else:
        row = {"correct_answer": question.metadata["correct_answer"]}

    row.update(
        {
            "item_id": question.item_id,
            "answer": prediction.cleaned_output,
            "valid": prediction.valid,
            "correct": prediction.correct,
            "raw_output": prediction.raw_output,
            "latency_ms": prediction.latency_ms,
            "prompt_tokens": prediction.prompt_tokens,
            "completion_tokens": prediction.completion_tokens,
            "total_tokens": prediction.total_tokens,
            "cost_usd": prediction.cost_usd,
        }
    )
    return row


def build_dataset_result(
    dataset_name: str,
    source_dataset: str,
    questions: Iterable[QuestionLabel],
    predictions: Iterable[Prediction],
    duration_s: float | None = None,
) -> DatasetResult:
    question_list = list(questions)
    prediction_list = list(predictions)

    rows = [_legacy_row(question, prediction) for question, prediction in zip(question_list, prediction_list, strict=True)]
    raw_outputs = [
        [
            {
                "generated_text": prediction.raw_output,
                "cleaned_output": prediction.cleaned_output,
                "finish_reason": prediction.finish_reason,
                "prompt_tokens": prediction.prompt_tokens,
                "completion_tokens": prediction.completion_tokens,
                "total_tokens": prediction.total_tokens,
                "cost_usd": prediction.cost_usd,
                "provider_model": prediction.provider_model,
            }
        ]
        for prediction in prediction_list
    ]

    validity = sum(1 for prediction in prediction_list if prediction.valid) / len(prediction_list)
    accuracy = sum(1 for prediction in prediction_list if prediction.correct) / len(prediction_list)
    measured_duration_s = duration_s
    if measured_duration_s is None:
        measured_duration_s = sum(prediction.latency_ms for prediction in prediction_list) / 1000.0
    cost_usd = sum(prediction.cost_usd or 0.0 for prediction in prediction_list)
    token_usage = TokenUsage(
        prompt_tokens=sum(prediction.prompt_tokens or 0 for prediction in prediction_list),
        completion_tokens=sum(prediction.completion_tokens or 0 for prediction in prediction_list),
        total_tokens=sum(prediction.total_tokens or 0 for prediction in prediction_list),
    )

    return DatasetResult(
        dataset_name=dataset_name,
        source_dataset=source_dataset,
        rows=rows,
        raw_outputs=raw_outputs,
        validity=validity,
        accuracy=accuracy,
        duration_s=measured_duration_s,
        cost_usd=cost_usd,
        token_usage=token_usage,
    )
