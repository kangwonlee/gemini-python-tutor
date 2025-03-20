# begin tests/test_llm_configs.py
import pathlib
import sys

from typing import Dict


import pytest


# Type hint
HEADER = Dict[str, str]


test_folder = pathlib.Path(__file__).parent.resolve()
project_folder = test_folder.parent.resolve()
sys.path.insert(0, str(project_folder))


from llm_configs import LLMConfig, GeminiConfig, GrokConfig, NvidiaNIMConfig


# Fixtures
@pytest.fixture
def sample_api_key() -> str:
    return "test_api_key"


@pytest.fixture
def sample_url() -> str:
    return "http://example.com"


@pytest.fixture
def sample_model() -> str:
    return "test_model"


@pytest.fixture
def sample_headers() -> HEADER:
    return {"X-Custom": "value"}


@pytest.fixture
def sample_question() -> str:
    return "What is the meaning of life?"


@pytest.fixture
def llm_config(sample_api_key: str, sample_url: str, sample_model: str) -> LLMConfig:
    return LLMConfig(api_key=sample_api_key, api_url=sample_url, model=sample_model)


@pytest.fixture
def gemini_config(sample_api_key: str, sample_url: str) -> GeminiConfig:
    return GeminiConfig(api_key=sample_api_key, api_url=sample_url)


@pytest.fixture
def grok_config(sample_api_key: str) -> GrokConfig:
    return GrokConfig(api_key=sample_api_key)


@pytest.fixture
def nvidia_nim_config(sample_api_key: str) -> NvidiaNIMConfig:
    return NvidiaNIMConfig(api_key=sample_api_key)


# LLMConfig Tests
def test_llm_config_init(llm_config: LLMConfig, sample_api_key: str, sample_url: str, sample_model: str):
    assert llm_config.api_key == sample_api_key
    assert llm_config.api_url == sample_url
    assert llm_config.model == sample_model
    assert llm_config.default_headers == {"Content-Type": "application/json"}


def test_llm_config_get_headers(llm_config: LLMConfig, sample_api_key: str):
    headers = llm_config.get_headers()
    assert headers["Authorization"] == f"Bearer {sample_api_key}"
    assert "Authorization" not in llm_config.default_headers  # Original unchanged


def test_llm_config_format_request_data(llm_config: LLMConfig, sample_question: str, sample_model: str):
    data = llm_config.format_request_data(sample_question)
    assert data["model"] == sample_model
    assert data["messages"][0]["content"] == sample_question


def test_llm_config_parse_response_raises(llm_config: LLMConfig):
    with pytest.raises(NotImplementedError):
        llm_config.parse_response({})


# GeminiConfig Tests
def test_gemini_config_init(gemini_config: GeminiConfig, sample_api_key: str):
    assert gemini_config.api_url == f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={sample_api_key}"
    assert "Authorization" not in gemini_config.get_headers()


def test_gemini_config_format_request_data(gemini_config: GeminiConfig, sample_question: str):
    data = gemini_config.format_request_data(sample_question)
    assert data["contents"][0]["parts"][0]["text"] == sample_question


def test_gemini_config_parse_response(gemini_config: GeminiConfig):
    response = {"candidates": [{"content": {"parts": [{"text": "Answer"}]}}]}
    assert gemini_config.parse_response(response) == "Answer"


# GrokConfig Tests
def test_grok_config_init(grok_config: GrokConfig, sample_api_key: str):
    assert grok_config.api_url == "https://api.x.ai/v1/chat/completions"
    assert grok_config.model == "grok-2-latest"


def test_grok_config_format_request_data(grok_config: GrokConfig, sample_question: str):
    data = grok_config.format_request_data(sample_question)
    assert data["messages"][0]["content"] == sample_question


def test_grok_config_parse_response(grok_config: GrokConfig):
    response = {"choices": [{"message": {"content": "Grok answer"}}]}
    assert grok_config.parse_response(response) == "Grok answer"


# NvidiaNIMConfig Tests
def test_nvidia_nim_config_init(nvidia_nim_config: NvidiaNIMConfig, sample_api_key: str):
    assert nvidia_nim_config.api_url == "https://integrate.api.nvidia.com/v1/chat/completions"
    assert nvidia_nim_config.model == "google/gemma-2-9b-it"


def test_nvidia_nim_config_parse_response(nvidia_nim_config: NvidiaNIMConfig):
    response = {"choices": [{"message": {"content": "NIM answer"}}]}
    assert nvidia_nim_config.parse_response(response) == "NIM answer"


if __name__ == "__main__":
    pytest.main(["--verbose", __file__])
# end tests/test_llm_configs.py
