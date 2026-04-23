from __future__ import annotations

import time
from dataclasses import dataclass

import litellm
from litellm import acompletion

from .config import (
    DEFAULT_REASONING_EFFORT,
    DEFAULT_TEMPERATURE,
    NVIDIA_NIM_API_BASE,
    OPENROUTER_API_BASE,
    load_runtime_settings,
)
from .schemas import Question


litellm.drop_params = True
litellm.suppress_debug_info = True


class ProviderError(RuntimeError):
    """Base error for provider requests."""


class NonRetryableProviderError(ProviderError):
    """Errors that should not be retried by Temporal."""


@dataclass(frozen=True)
class ProviderRequest:
    model: str
    api_key: str
    api_base: str | None = None


def _resolve_provider_request(model: str) -> ProviderRequest:
    settings = load_runtime_settings()

    if model.startswith("openrouter/"):
        if not settings.openrouter_api_key:
            raise NonRetryableProviderError(
                "Model explicitly requires OpenRouter, but OPENROUTER_API_KEY is missing."
            )
        return ProviderRequest(
            model=model,
            api_key=settings.openrouter_api_key,
            api_base=OPENROUTER_API_BASE,
        )

    if model.startswith("openai/"):
        direct_model = model.split("/", 1)[1]
        if not settings.openai_api_key:
            raise NonRetryableProviderError(
                "Model explicitly targets OpenAI, but OPENAI_API_KEY is missing."
            )
        return ProviderRequest(model=direct_model, api_key=settings.openai_api_key)

    if model.startswith("anthropic/"):
        direct_model = model.split("/", 1)[1]
        if not settings.anthropic_api_key:
            raise NonRetryableProviderError(
                "Model explicitly targets Anthropic, but ANTHROPIC_API_KEY is missing."
            )
        return ProviderRequest(model=direct_model, api_key=settings.anthropic_api_key)

    if model.startswith("nvidia_nim/"):
        if not settings.nvidia_api_key:
            raise NonRetryableProviderError(
                "Model explicitly targets NVIDIA NIM, but NVIDIA_API_KEY is missing."
            )
        return ProviderRequest(
            model=model,
            api_key=settings.nvidia_api_key,
            api_base=NVIDIA_NIM_API_BASE,
        )

    if model.startswith("nvidia/"):
        if not settings.nvidia_api_key:
            raise NonRetryableProviderError(
                "Model explicitly targets NVIDIA NIM, but NVIDIA_API_KEY is missing."
            )
        return ProviderRequest(
            model=f"nvidia_nim/{model.split('/', 1)[1]}",
            api_key=settings.nvidia_api_key,
            api_base=NVIDIA_NIM_API_BASE,
        )

    if model.startswith(("gpt-", "o1", "o3", "o4", "chatgpt-")):
        if settings.openai_api_key:
            return ProviderRequest(model=model, api_key=settings.openai_api_key)
        if settings.openrouter_api_key:
            return ProviderRequest(
                model=f"openrouter/openai/{model}",
                api_key=settings.openrouter_api_key,
                api_base=OPENROUTER_API_BASE,
            )
        raise NonRetryableProviderError(
            f"No provider key available for OpenAI model '{model}'. Set OPENAI_API_KEY or OPENROUTER_API_KEY."
        )

    if model.startswith("claude-"):
        if settings.anthropic_api_key:
            return ProviderRequest(model=model, api_key=settings.anthropic_api_key)
        if settings.openrouter_api_key:
            return ProviderRequest(
                model=f"openrouter/anthropic/{model}",
                api_key=settings.openrouter_api_key,
                api_base=OPENROUTER_API_BASE,
            )
        raise NonRetryableProviderError(
            f"No provider key available for Anthropic model '{model}'. Set ANTHROPIC_API_KEY or OPENROUTER_API_KEY."
        )

    if settings.openrouter_api_key:
        return ProviderRequest(
            model=model if model.startswith("openrouter/") else f"openrouter/{model}",
            api_key=settings.openrouter_api_key,
            api_base=OPENROUTER_API_BASE,
        )

    raise NonRetryableProviderError(
        f"Could not route model '{model}'. Provide a matching direct provider key or OPENROUTER_API_KEY."
    )


async def generate_completion(
    model: str,
    question: Question,
    temperature: float = DEFAULT_TEMPERATURE,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
) -> dict:
    provider_request = _resolve_provider_request(model)

    messages = [
        {"role": "system", "content": question.system_prompt},
        {"role": "user", "content": question.user_prompt},
    ]

    started = time.perf_counter()
    try:
        response = await acompletion(
            model=provider_request.model,
            messages=messages,
            api_key=provider_request.api_key,
            api_base=provider_request.api_base,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
            num_retries=0,
        )
    except Exception as exc:  # pragma: no cover - provider exceptions vary by version
        status_code = getattr(exc, "status_code", None)
        if status_code in {400, 401, 403, 404}:
            raise NonRetryableProviderError(str(exc)) from exc
        raise ProviderError(str(exc)) from exc

    latency_ms = (time.perf_counter() - started) * 1000.0
    choice = response.choices[0]
    message = choice.message
    usage = getattr(response, "usage", None)

    hidden_params = getattr(response, "_hidden_params", {}) or {}
    response_cost = hidden_params.get("response_cost")
    if response_cost is None:
        response_cost = hidden_params.get("additional_headers", {}).get(
            "llm_provider-x-litellm-response-cost"
        )

    cost_usd = float(response_cost) if response_cost is not None else None
    if cost_usd is None:
        try:
            cost_usd = float(
                litellm.completion_cost(
                    completion_response=response,
                    model=provider_request.model,
                )
            )
        except Exception:  # pragma: no cover - pricing coverage depends on provider metadata
            cost_usd = None

    return {
        "raw_output": message.content or "",
        "finish_reason": getattr(choice, "finish_reason", None),
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
        "cost_usd": cost_usd,
        "provider_model": getattr(response, "model", None),
        "latency_ms": latency_ms,
    }
