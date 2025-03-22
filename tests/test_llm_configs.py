# begin tests/test_llm_configs.py
import pathlib
import sys
from typing import Dict, Tuple, Type

import pytest


# Adjust sys.path to import from project root
test_folder = pathlib.Path(__file__).parent.resolve()
project_folder = test_folder.parent.resolve()
sys.path.insert(0, str(project_folder))

from llm_configs import LLMConfig, GeminiConfig, GrokConfig, NvidiaNIMConfig


# Type hint
HEADER = Dict[str, str]


# Fixtures
@pytest.fixture
def sample_api_key() -> str:
    return "test_api_key"


@pytest.fixture
def sample_question() -> str:
    return "What is the meaning of life?"


# Model-in-URL Config Fixture
@pytest.fixture(params=[
    ("gemini-2.0-flash", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=test_api_key"),
    ("gemini-1.5-pro", "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=test_api_key")
])
def model_in_url_config(request, sample_api_key: str) -> Tuple[GeminiConfig, str, str]:
    model, expected_url = request.param
    config = GeminiConfig(api_key=sample_api_key, model=model)
    return config, model, expected_url


# Model-in-Data Config Fixture
@pytest.fixture(params=[
    (GrokConfig, "grok-2-latest", "https://api.x.ai/v1/chat/completions"),
    (GrokConfig, "grok-1.0", "https://api.x.ai/v1/chat/completions"),
    (NvidiaNIMConfig, "google/gemma-2-9b-it", "https://integrate.api.nvidia.com/v1/chat/completions"),
    (NvidiaNIMConfig, "meta/llama-3.1-8b-instruct", "https://integrate.api.nvidia.com/v1/chat/completions")
])
def model_in_data_config(request, sample_api_key: str) -> Tuple[LLMConfig, Type[LLMConfig], str, str]:
    config_class, model, expected_url = request.param
    config = config_class(api_key=sample_api_key, model=model)
    return config, config_class, model, expected_url


# Base LLMConfig Tests
def test_llm_config_default_headers(sample_api_key: str):
    """Test that LLMConfig initializes with default headers."""
    config = LLMConfig(api_key=sample_api_key, api_url="http://example.com", model="test_model")
    assert config.default_headers == {"Content-Type": "application/json"}


def test_llm_config_get_headers(sample_api_key: str):
    """Test that get_headers adds Authorization without modifying defaults."""
    config = LLMConfig(api_key=sample_api_key, api_url="http://example.com", model="test_model")
    headers = config.get_headers()
    assert headers["Authorization"] == f"Bearer {sample_api_key}"
    assert "Authorization" not in config.default_headers


def test_llm_config_parse_response_raises(sample_api_key: str):
    """Test that base parse_response raises NotImplementedError."""
    config = LLMConfig(api_key=sample_api_key, api_url="http://example.com", model="test_model")
    with pytest.raises(NotImplementedError):
        config.parse_response({})


# Model-in-URL Tests
def test__model_in_url__config_init(model_in_url_config: Tuple[GeminiConfig, str, str], sample_api_key: str):
    """Test that model-in-URL configs correctly set model and URL."""
    config, expected_model, expected_url = model_in_url_config
    assert config.model == expected_model
    assert config.api_url == expected_url
    assert "Authorization" not in config.get_headers()  # Gemini-specific


def test__model_in_url__format_request_data(model_in_url_config: Tuple[GeminiConfig, str, str], sample_question: str):
    """Test that model-in-URL configs format request data without model."""
    config, _, _ = model_in_url_config
    data = config.format_request_data(sample_question)
    assert data["contents"][0]["parts"][0]["text"] == sample_question
    assert "model" not in data  # Model is in URL, not data


def test__model_in_url__parse_response(model_in_url_config: Tuple[GeminiConfig, str, str]):
    """Test that model-in-URL configs parse Gemini-style responses."""
    config, _, _ = model_in_url_config
    response = {"candidates": [{"content": {"parts": [{"text": "Answer"}]}}]}
    assert config.parse_response(response) == "Answer"


# Model-in-Data Tests
def test__model_in_data__config_init(model_in_data_config: Tuple[LLMConfig, Type[LLMConfig], str, str], sample_api_key: str):
    """Test that model-in-data configs correctly set model and static URL."""
    config, _, expected_model, expected_url = model_in_data_config
    assert config.model == expected_model
    assert config.api_url == expected_url
    headers = config.get_headers()
    assert headers["Authorization"] == f"Bearer {sample_api_key}"


@pytest.mark.parametrize("response_json, expected_answer", [
    ({"choices": [{"message": {"content": "Grok answer"}}]}, "Grok answer"),  # Grok
    ({"choices": [{"message": {"content": "NIM answer"}}]}, "NIM answer")     # Nvidia NIM
])
def test__model_in_data__parse_response(model_in_data_config: Tuple[LLMConfig, Type[LLMConfig], str, str], response_json: Dict, expected_answer: str):
    """Test that model-in-data configs parse OpenAI-style responses."""
    config, _, _, _ = model_in_data_config
    assert config.parse_response(response_json) == expected_answer


def test__model_in_data__format_request_data(model_in_data_config: Tuple[LLMConfig, Type[LLMConfig], str, str], sample_question: str):
    """Test that model-in-data configs include model in request data."""
    config, _, expected_model, _ = model_in_data_config
    data = config.format_request_data(sample_question)
    assert data["model"] == expected_model
    assert data["messages"][0]["content"] == sample_question

if __name__ == "__main__":
    pytest.main(["--verbose", __file__])

# end tests/test_llm_configs.py
