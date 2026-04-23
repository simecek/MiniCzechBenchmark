from __future__ import annotations

import gzip
import pickle
from pathlib import Path

from minicz_bench.scoring import build_dataset_result, evaluate_prediction
from minicz_bench.schemas import Prediction, Question


FIXTURE_PATH = Path("bench_runs/Mistral-7B-Instruct-v0.3_mini_simplemessages_noSampling.pkl.gz")


def _question_from_legacy_row(dataset_name: str, row: dict, item_id: int) -> Question:
    if dataset_name == "agree":
        answer_key = str(int(row["correct_answer_minus_1"]) + 1)
        metadata = {"correct_answer_minus_1": int(row["correct_answer_minus_1"])}
        valid_answers = ["1", "2", "3", "4", "5"]
    elif dataset_name == "klokanek":
        answer_key = str(row["correct_answer"]).lower()
        metadata = {"correct_answer": str(row["correct_answer"]).lower()}
        valid_answers = ["a", "b", "c", "d", "e"]
    elif dataset_name == "ctkfacts":
        answer_key = str(row["correct_answer"])
        metadata = {"correct_answer": str(row["correct_answer"])}
        valid_answers = ["0", "1", "2"]
    else:
        answer_key = str(row["correct_answer"])
        metadata = {"correct_answer": str(row["correct_answer"])}
        valid_answers = ["1", "2", "3", "4", "5"]

    return Question(
        dataset_name=dataset_name,
        item_id=item_id,
        system_prompt="",
        user_prompt="",
        answer_key=answer_key,
        valid_answers=valid_answers,
        metadata=metadata,
    )


def test_scoring_matches_legacy_artifact() -> None:
    with gzip.open(FIXTURE_PATH, "rb") as file:
        artifact = pickle.load(file)

    for dataset_name, dataframe in artifact["dfs"].items():
        records = dataframe.to_dict(orient="records")
        raw_outputs = artifact["raw_outputs"][dataset_name]
        questions = []
        predictions = []

        for item_id, (record, raw_output) in enumerate(zip(records, raw_outputs, strict=True)):
            question = _question_from_legacy_row(dataset_name, record, item_id)
            generated_text = raw_output[0]["generated_text"]
            cleaned_output, valid, correct = evaluate_prediction(question, generated_text)
            expected_answer = (
                str(record["answer"]).lower()
                if dataset_name == "klokanek"
                else str(record["answer"])
            )
            assert cleaned_output == expected_answer
            assert valid == bool(record["valid"])
            assert correct == bool(record["correct"])

            questions.append(question)
            predictions.append(
                Prediction(
                    dataset_name=dataset_name,
                    item_id=item_id,
                    raw_output=generated_text,
                    cleaned_output=cleaned_output,
                    valid=valid,
                    correct=correct,
                    latency_ms=0.0,
                )
            )

        dataset_result = build_dataset_result(
            dataset_name=dataset_name,
            source_dataset=artifact["datasets"][dataset_name],
            questions=questions,
            predictions=predictions,
        )
        validity, accuracy = artifact["metrics"][dataset_name]
        assert dataset_result.validity == validity
        assert dataset_result.accuracy == accuracy
