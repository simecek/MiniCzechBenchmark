from __future__ import annotations

from functools import lru_cache

from datasets import load_dataset

from .schemas import Question


def _agree_question(row: dict, item_id: int) -> Question:
    return Question(
        dataset_name="agree",
        item_id=item_id,
        system_prompt=row["system_prompt"],
        user_prompt=row["user_prompt"],
        answer_key=str(int(row["answer_idx"]) + 1),
        valid_answers=["1", "2", "3", "4", "5"],
        metadata={"correct_answer_minus_1": int(row["answer_idx"])},
    )


def _czech_news_question(row: dict, item_id: int) -> Question:
    return Question(
        dataset_name="czech_news",
        item_id=item_id,
        system_prompt=row["system_prompt"],
        user_prompt=row["user_prompt"],
        answer_key=str(row["category"]),
        valid_answers=["1", "2", "3", "4", "5"],
        metadata={"correct_answer": str(row["category"])},
    )


def _klokanek_question(row: dict, item_id: int) -> Question:
    return Question(
        dataset_name="klokanek",
        item_id=item_id,
        system_prompt=row["system_prompt"],
        user_prompt=row["user_prompt"],
        answer_key=str(row["correct_answer"]).lower(),
        valid_answers=["a", "b", "c", "d", "e"],
        metadata={"correct_answer": str(row["correct_answer"]).lower()},
    )


def _ctkfacts_question(row: dict, item_id: int) -> Question:
    return Question(
        dataset_name="ctkfacts",
        item_id=item_id,
        system_prompt=row["system_prompt"],
        user_prompt=row["user_prompt"],
        answer_key=str(row["label"]),
        valid_answers=["0", "1", "2"],
        metadata={"correct_answer": str(row["label"])},
    )


QUESTION_BUILDERS = {
    "agree": _agree_question,
    "czech_news": _czech_news_question,
    "klokanek": _klokanek_question,
    "ctkfacts": _ctkfacts_question,
}


@lru_cache(maxsize=None)
def load_questions_for_dataset(dataset_name: str, dataset_path: str) -> tuple[Question, ...]:
    dataset = load_dataset(dataset_path)
    rows = dataset["train"]
    builder = QUESTION_BUILDERS[dataset_name]
    return tuple(builder(row, item_id=i) for i, row in enumerate(rows))
