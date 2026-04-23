from __future__ import annotations

from minicz_bench.config import load_runtime_settings
from minicz_bench.llm import _resolve_provider_request


def test_openai_models_prefer_direct_provider(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-key")
    load_runtime_settings.cache_clear()

    request = _resolve_provider_request("gpt-4.1-nano")

    assert request.model == "gpt-4.1-nano"
    assert request.api_base is None
    assert request.api_key == "openai-key"


def test_anthropic_models_fall_back_to_openrouter(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-key")
    load_runtime_settings.cache_clear()

    request = _resolve_provider_request("claude-3-5-sonnet-20241022")

    assert request.model == "openrouter/anthropic/claude-3-5-sonnet-20241022"
    assert request.api_key == "openrouter-key"


def test_nvidia_alias_routes_to_nvidia_nim(monkeypatch) -> None:
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-key")
    load_runtime_settings.cache_clear()

    request = _resolve_provider_request("nvidia/meta/llama-3.1-8b-instruct")

    assert request.model == "nvidia_nim/meta/llama-3.1-8b-instruct"
    assert request.api_key == "nvapi-key"
    assert request.api_base == "https://integrate.api.nvidia.com/v1"
