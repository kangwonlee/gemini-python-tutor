# begin tests/test_llm_client.py
import logging
import pathlib
import sys
import time

from typing import Dict


import pytest
from unittest.mock import Mock, patch


# Adjust sys.path to import from project root
test_folder = pathlib.Path(__file__).parent.resolve()
project_folder = test_folder.parent.resolve()
sys.path.insert(0, str(project_folder))


from llm_client import LLMAPIClient
from llm_configs import LLMConfig


# Fixtures
@pytest.fixture
def mock_config() -> LLMConfig:
    """Mock LLMConfig with simple behavior."""
    config = Mock(spec=LLMConfig)
    config.api_key = "test_key"
    config.api_url = "http://mock.api/v1"
    config.model = "mock_model"
    config.get_headers.return_value = {"Content-Type": "application/json", "Authorization": "Bearer test_key"}
    config.format_request_data.side_effect = lambda q: {"question": q}
    config.parse_response.side_effect = lambda r: r["answer"]
    return config


@pytest.fixture
def client(mock_config: LLMConfig) -> LLMAPIClient:
    """LLMAPIClient instance with default settings."""
    return LLMAPIClient(mock_config, retry_delay_sec=0.1, max_retry_attempt=2, timeout_sec=1)


@pytest.fixture
def sample_question() -> str:
    return "What is 2 + 2?"


# Tests
def test_init(client: LLMAPIClient, mock_config: LLMConfig):
    """Test client initialization."""
    assert client.config == mock_config
    assert client.retry_delay_sec == 0.1
    assert client.max_retry_attempt == 2
    assert client.timeout_sec == 1
    assert isinstance(client.logger, logging.Logger)


@patch("llm_client.requests.post")
def test_call_api_success(mock_post: Mock, client: LLMAPIClient, sample_question: str):
    """Test successful API call."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"answer": "4"}
    mock_post.return_value = mock_response

    result = client.call_api(sample_question)
    assert result == "4"
    mock_post.assert_called_once_with(
        client.config.api_url,
        headers=client.config.get_headers(),
        json={"question": sample_question}
    )


@patch("llm_client.requests.post")
def test_call_api_rate_limit_success(mock_post: Mock, client: LLMAPIClient, sample_question: str):
    """Test rate limit retry leading to success."""
    mock_response_429 = Mock(status_code=429)
    mock_response_200 = Mock(status_code=200)
    mock_response_200.json.return_value = {"answer": "4"}
    mock_post.side_effect = [mock_response_429, mock_response_200]

    result = client.call_api(sample_question)
    assert result == "4"
    assert mock_post.call_count == 2  # Retried once
    client.logger.warning.assert_called_once()  # Rate limit warning logged


@patch("llm_client.requests.post")
@patch("llm_client.time.sleep")  # Mock sleep to avoid delays
def test_call_api_rate_limit_exhausted(mock_sleep: Mock, mock_post: Mock, client: LLMAPIClient, sample_question: str):
    """Test exceeding max retries on rate limit."""
    mock_response = Mock(status_code=429)
    mock_post.return_value = mock_response

    result = client.call_api(sample_question)
    assert result is None
    assert mock_post.call_count == 3  # 2 retries + 1 initial
    assert mock_sleep.call_args_list == [((0.1,),), ((0.2,),)]  # Exponential backoff
    client.logger.error.assert_called_once_with(f"Max retries exceeded for rate limit. Question: {sample_question}")


@patch("llm_client.requests.post")
def test_call_api_timeout(mock_post: Mock, client: LLMAPIClient, sample_question: str):
    """Test timeout exceeded."""
    # Simulate a long delay by mocking time.monotonic
    with patch("llm_client.time.monotonic") as mock_time:
        mock_time.side_effect = [0, 0, 2]  # Start at 0, exceed timeout (1s) on second call
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"answer": "4"}
        mock_post.return_value = mock_response

        result = client.call_api(sample_question)
        assert result is None
        mock_post.assert_called_once()  # Only one attempt before timeout
        client.logger.error.assert_called_once_with(f"Timeout exceeded for question: {sample_question}")


@patch("llm_client.requests.post")
def test_call_api_parse_error(mock_post: Mock, client: LLMAPIClient, sample_question: str):
    """Test handling of parsing errors."""
    mock_response = Mock(status_code=200)
    mock_response.json.return_value = {"invalid": "data"}
    mock_post.return_value = mock_response
    client.config.parse_response.side_effect = KeyError("Invalid response format")

    result = client.call_api(sample_question)
    assert result is None
    client.logger.exception.assert_called_once()
    mock_post.assert_called_once()


@patch("llm_client.requests.post")
def test_call_api_unexpected_status(mock_post: Mock, client: LLMAPIClient, sample_question: str):
    """Test handling of unexpected status codes."""
    mock_response = Mock(status_code=500)
    mock_response.text = "Server error"
    mock_post.return_value = mock_response

    result = client.call_api(sample_question)
    assert result is None
    client.logger.error.assert_called_once_with("API failed with status 500: Server error")
    mock_post.assert_called_once()


if __name__ == "__main__":
    pytest.main(["--verbose", __file__])
# end tests/test_llm_client.py
