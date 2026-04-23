from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "bench_runs"
DEFAULT_RESULTS_FILE = PROJECT_ROOT / "RESULTS.md"
DEFAULT_MAX_PARALLEL = 20
DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_TEMPERATURE = 0.0
DEFAULT_REASONING_EFFORT = "medium"
DEFAULT_MESSAGE_STRATEGY = "simplemessages"
DEFAULT_PIPELINE_TYPE = "api"
DEFAULT_TEMPORAL_ADDRESS = "localhost:7233"
DEFAULT_TEMPORAL_NAMESPACE = "default"
DEFAULT_TEMPORAL_TASK_QUEUE = "minicz-bench"
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
NVIDIA_NIM_API_BASE = "https://integrate.api.nvidia.com/v1"

DATASETS_BY_SIZE = {
    "full": {
        "agree": "simecek/agree",
        "czech_news": "simecek/czech_news",
        "klokanek": "simecek/klokanek",
        "ctkfacts": "simecek/ctkfacts",
    },
    "mini": {
        "agree": "simecek/mini_agree",
        "czech_news": "simecek/mini_czech_news",
        "klokanek": "simecek/mini_klokanek",
        "ctkfacts": "simecek/mini_ctkfacts",
    },
}


class RuntimeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openrouter_api_key: str | None = None
    nvidia_api_key: str | None = None
    temporal_address: str = DEFAULT_TEMPORAL_ADDRESS
    temporal_namespace: str = DEFAULT_TEMPORAL_NAMESPACE
    temporal_task_queue: str = DEFAULT_TEMPORAL_TASK_QUEUE
    logfire_token: str | None = None


@lru_cache(maxsize=1)
def load_runtime_settings() -> RuntimeSettings:
    return RuntimeSettings()


def get_datasets_for_size(data_size: str) -> dict[str, str]:
    try:
        return DATASETS_BY_SIZE[data_size]
    except KeyError as exc:
        allowed = ", ".join(sorted(DATASETS_BY_SIZE))
        raise ValueError(f"Unsupported data size '{data_size}'. Choose one of: {allowed}.") from exc


def slugify_model_name(model: str) -> str:
    if "/" in model:
        model = model.split("/")[-1]
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", model).strip("-")
    return slug or "model"


def build_run_name(
    model: str,
    data_size: str,
    message_strategy: str = DEFAULT_MESSAGE_STRATEGY,
    pipeline_type: str = DEFAULT_PIPELINE_TYPE,
) -> str:
    return f"{slugify_model_name(model)}_{data_size}_{message_strategy}_{pipeline_type}"
