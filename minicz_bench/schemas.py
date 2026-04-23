from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Question(BaseModel):
    dataset_name: str
    item_id: int
    system_prompt: str
    user_prompt: str
    answer_key: str
    valid_answers: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)


class QuestionLabel(BaseModel):
    dataset_name: str
    item_id: int
    answer_key: str
    valid_answers: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)


class Prediction(BaseModel):
    dataset_name: str
    item_id: int
    raw_output: str
    cleaned_output: str
    valid: bool
    correct: bool
    latency_ms: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    cost_usd: float | None = None
    finish_reason: str | None = None
    provider_model: str | None = None


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class DatasetResult(BaseModel):
    dataset_name: str
    source_dataset: str
    rows: list[dict[str, Any]]
    raw_outputs: list[list[dict[str, Any]]]
    validity: float
    accuracy: float
    duration_s: float
    cost_usd: float
    token_usage: TokenUsage


class RunTotals(BaseModel):
    duration_s: float
    cost_usd: float
    token_usage: TokenUsage


class BenchRun(BaseModel):
    model: str
    data_size: str
    run_name: str
    datasets: dict[str, str]
    dataset_results: dict[str, DatasetResult]
    metrics: dict[str, tuple[float, float]]
    timing_results: dict[str, float]
    cost_usd: dict[str, float]
    token_usage: dict[str, dict[str, int]]
    run_started_at: datetime
    run_finished_at: datetime
    max_parallel: int
    max_attempts: int
    message_strategy: str
    pipeline_type: str
    totals: RunTotals


class LoadDatasetInput(BaseModel):
    dataset_name: str
    dataset_path: str


class PredictActivityInput(BaseModel):
    model: str
    dataset_name: str
    dataset_path: str
    item_id: int
    temperature: float = 0.0
    reasoning_effort: str = "medium"


class WorkflowInput(BaseModel):
    model: str
    data_size: str
    datasets: dict[str, str]
    run_name: str
    output_dir: str | None
    run_started_at: datetime
    max_parallel: int
    max_attempts: int
    reasoning_effort: str = "medium"
    message_strategy: str = "simplemessages"
    pipeline_type: str = "openrouter"


class SaveArtifactsInput(BaseModel):
    bench_run: BenchRun
    output_dir: str | None


class ArtifactInfo(BaseModel):
    pickle_path: str | None = None
    json_path: str | None = None


class BenchmarkWorkflowResult(BaseModel):
    bench_run: BenchRun
    artifact_info: ArtifactInfo
