# begin tests/test_llm_client.py
import logging
import pathlib
import sys
from unittest.mock import Mock, patch

import pytest
import requests

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
def mock_logger():
    """Mock logger for testing logging calls."""
    return Mock(spec=logging.Logger)


@pytest.fixture
def client(mock_config: LLMConfig, mock_logger: Mock) -> LLMAPIClient:
    """LLMAPIClient instance with mocked logger and default settings."""
    client = LLMAPIClient(mock_config, retry_delay_sec=0.1, max_retry_attempt=2, timeout_sec=1)
    client.logger = mock_logger  # Override real logger with mock
    return client


@pytest.fixture
def sample_question() -> str:
    return "What is 2 + 2?"


# Tests
def test_init(client: LLMAPIClient, mock_config: LLMConfig, mock_logger: Mock):
    """Test client initialization with valid parameters."""
    assert client.config == mock_config
    assert client.retry_delay_sec == 0.1
    assert client.max_retry_attempt == 2
    assert client.timeout_sec == 1
    assert client.logger == mock_logger


def test_init_invalid_params(mock_config: LLMConfig, mock_logger: Mock):
    """Test that invalid initialization parameters raise appropriate exceptions."""
    with pytest.raises(ValueError, match="retry_delay_sec must be a positive number"):
        LLMAPIClient(mock_config, retry_delay_sec=-1, max_retry_attempt=2, timeout_sec=1)
    with pytest.raises(ValueError, match="max_retry_attempt must be a non-negative integer"):
        LLMAPIClient(mock_config, retry_delay_sec=0.1, max_retry_attempt=-1, timeout_sec=1)
    with pytest.raises(ValueError, match="timeout_sec must be a positive integer"):
        LLMAPIClient(mock_config, retry_delay_sec=0.1, max_retry_attempt=2, timeout_sec=0)


@patch("llm_client.requests.post")
def test_call_api_success(mock_post: Mock, client: LLMAPIClient, sample_question: str):
    """Test successful API call returns the expected answer."""
    mock_response = Mock(status_code=200)
    mock_response.json.return_value = {"answer": "4"}
    mock_post.return_value = mock_response

    result = client.call_api(sample_question)
    assert result == "4"
    mock_post.assert_called_once_with(
        client.config.api_url,
        headers=client.config.get_headers(),
        json={"question": sample_question},
        timeout=client.timeout_sec
    )


@patch("llm_client.requests.post")
def test_call_api_rate_limit_success(mock_post: Mock, client: LLMAPIClient, sample_question: str):
    """Test that a rate limit (429) retry succeeds on the second attempt."""
    mock_response_429 = Mock(status_code=429)
    mock_response_200 = Mock(status_code=200)
    mock_response_200.json.return_value = {"answer": "4"}
    mock_post.side_effect = [mock_response_429, mock_response_200]

    result = client.call_api(sample_question)
    assert result == "4"
    assert mock_post.call_count == 2  # Initial + 1 retry

    # Robust check: ensure called once, then verify key parts
    client.logger.warning.assert_called_once()
    log_msg = client.logger.warning.call_args[0][0]
    assert "Rate limit (429) hit" in log_msg
    assert "Retrying in 0.1s" in log_msg  # Delay is dynamic but fixed in this test (attempt 0 -> 0.1s)
    assert "(attempt 1/2)" in log_msg


@patch("llm_client.time.sleep")
@patch("llm_client.requests.post")
def test_call_api_rate_limit_exhausted(mock_post: Mock, mock_sleep: Mock, client: LLMAPIClient, sample_question: str):
    """Test that max retries are exhausted on 429 status, with exponential backoff.
    Verifies the client gives up after max_retry_attempt (2), logging the failure.
    """
    mock_response = Mock(status_code=429)
    mock_post.return_value = mock_response

    result = client.call_api(sample_question)
    assert result is None
    assert mock_post.call_count == 3  # Initial + 2 retries
    assert mock_sleep.call_args_list == [((0.1,),), ((0.2,),)]  # Exponential backoff
    client.logger.error.assert_called_once_with(f"Max retries ({mock_post.call_count-1}) exceeded for rate limit. Question: {sample_question}")


@patch("llm_client.requests.post")
def test_call_api_timeout(mock_post: Mock, client: LLMAPIClient, sample_question: str):
    """Test that a request timeout returns None and logs an error.
    Ensures the client aborts on slow or unresponsive APIs.
    """
    mock_post.side_effect = requests.Timeout("Request timed out")

    result = client.call_api(sample_question)
    assert result is None
    mock_post.assert_called_once()
    client.logger.error.assert_called_once_with(f"Timeout exceeded for question: {sample_question}")


@patch("llm_client.requests.post")
def test_call_api_network_error(mock_post: Mock, client: LLMAPIClient, sample_question: str):
    """Test that a network error (e.g., connection failure) returns None and logs an error."""
    mock_post.side_effect = requests.ConnectionError("Network unreachable")

    result = client.call_api(sample_question)
    assert result is None
    mock_post.assert_called_once()
    client.logger.error.assert_called_once_with(f"Network error for question: {sample_question}: Network unreachable")


@patch("llm_client.requests.post")
def test_call_api_parse_error(mock_post: Mock, client: LLMAPIClient, sample_question: str):
    """Test that a parsing error in the response returns None and logs the exception."""
    mock_response = Mock(status_code=200)
    mock_response.json.return_value = {"invalid": "data"}
    mock_post.return_value = mock_response
    client.config.parse_response.side_effect = KeyError("Invalid response format")

    result = client.call_api(sample_question)
    assert result is None
    client.logger.exception.assert_called_once_with("Error parsing response: 'Invalid response format'")
    mock_post.assert_called_once()


@patch("llm_client.requests.post")
def test_call_api_unexpected_status(mock_post: Mock, client: LLMAPIClient, sample_question: str):
    """Test that an unexpected status code (e.g., 500) returns None without retries."""
    mock_response = Mock(status_code=500)
    mock_response.text = "Server error"
    mock_post.return_value = mock_response

    result = client.call_api(sample_question)
    assert result is None
    mock_post.assert_called_once()  # No retries for non-429 status
    client.logger.error.assert_called_once_with("API failed with status 500: Server error")


@patch("llm_client.requests.post")
def test_call_api_invalid_json(mock_post: Mock, client: LLMAPIClient, sample_question: str):
    """Test that invalid JSON in a 200 response returns None and logs an error."""
    mock_response = Mock(status_code=200)
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_post.return_value = mock_response

    result = client.call_api(sample_question)
    assert result is None

    # Check that logger was called with a message containing key elements
    call_args = client.logger.exception.call_args
    assert call_args is not None
    error_msg = call_args[0][0]
    assert "Failed to parse API response" in error_msg
    assert "Invalid JSON" in error_msg
    assert sample_question[:10] in error_msg if len(sample_question) > 100 else sample_question in error_msg

    mock_post.assert_called_once()


@patch("llm_client.requests.post")
def test_call_api_empty_question(mock_post: Mock, client: LLMAPIClient):
    """Test that an empty question still triggers a request and handles the response."""
    mock_response = Mock(status_code=200)
    mock_response.json.return_value = {"answer": "No question provided"}
    mock_post.return_value = mock_response

    result = client.call_api("")
    assert result == "No question provided"
    mock_post.assert_called_once_with(
        client.config.api_url,
        headers=client.config.get_headers(),
        json={"question": ""},
        timeout=client.timeout_sec
    )

if __name__ == "__main__":
    pytest.main(["--verbose", __file__])
# end tests/test_llm_client.py
