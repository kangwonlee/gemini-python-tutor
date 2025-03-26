# begin llm_client.py
import logging
import time
from typing import Optional

import requests

from llm_configs import LLMConfig


class LLMAPIClient:
    """Generic client for interacting with LLM APIs using a configuration.
 
    This class provides a robust interface for making API calls to various
    Large Language Model services, handling retries, timeouts, and errors
    in a standardized way.
 
    Attributes:
        config (LLMConfig): Configuration object containing API-specific details
        retry_delay_sec (float): Base delay between retry attempts in seconds
        max_retry_attempt (int): Maximum number of retry attempts
        timeout_sec (int): Request timeout duration in seconds
        logger (logging.Logger): Logger instance for tracking operations
    """

    def __init__(self, config: LLMConfig, retry_delay_sec: float = 5.0,
                 max_retry_attempt: int = 3, timeout_sec: int = 60):
        """Initialize the LLM API client with retry and timeout settings.

        Args:
            config (LLMConfig): Configuration object containing API endpoint, key, and model details
            retry_delay_sec (float, optional): Base delay between retries in seconds. Defaults to 5.0
            max_retry_attempt (int, optional): Maximum number of retry attempts. Defaults to 3
            timeout_sec (int, optional): Maximum time allowed per request in seconds. Defaults to 60

        Raises:
            ValueError: If retry_delay_sec or timeout_sec is not positive, or max_retry_attempt is negative
        """
        # Validate input parameters
        if retry_delay_sec <= 0:
            raise ValueError("retry_delay_sec must be a positive number")
        if max_retry_attempt < 0:
            raise ValueError("max_retry_attempt must be a non-negative integer")
        if timeout_sec <= 0:
            raise ValueError("timeout_sec must be a positive integer")

        # Assign instance variables
        self.config = config
        self.retry_delay_sec = retry_delay_sec
        self.max_retry_attempt = max_retry_attempt
        self.timeout_sec = timeout_sec
        self.logger = logging.getLogger(__name__)  # Logger for this module

    def call_api(self, question: str) -> Optional[str]:
        """Send a question to the LLM API with retry and timeout handling.

        Implements a robust API calling mechanism with:
        - Exponential backoff for rate limit (429) retries
        - Timeout handling
        - Network error handling
        - Response parsing with error logging

        Args:
            question (str): The input prompt or question to send to the API

        Returns:
            Optional[str]: The parsed answer from the API, or None if the request fails after all retries

        Notes:
            - Retries only on HTTP 429 (Too Many Requests) with exponential backoff
            - Logs detailed errors for debugging and monitoring
            - Returns None for any unrecoverable error (timeout, network, parsing, etc.)
        """
        # Prepare request components from config
        headers = self.config.get_headers()
        data = self.config.format_request_data(question)

        # Retry loop for handling rate limits and transient failures
        for attempt in range(self.max_retry_attempt + 1):
            try:
                # Make the POST request with timeout
                response = requests.post(
                    self.config.api_url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout_sec
                )
            except requests.Timeout:
                # Log timeout errors and fail immediately
                self.logger.error(f"Request timed out after {self.timeout_sec}s for question: {question}")
                return None
            except requests.RequestException as e:
                # Log general network errors (connection issues, etc.) and fail
                self.logger.error(f"Network error occurred for question '{question}': {str(e)}")
                return None

            # Handle successful response
            if response.status_code == 200:
                try:
                    # Parse JSON and extract response using config-specific method
                    result = response.json()
                    return self.config.parse_response(result)
                except (ValueError, KeyError) as e:
                    # Log parsing errors (invalid JSON or unexpected structure)
                    self.logger.exception(f"Failed to parse API response for question '{question}': {str(e)}")
                    return None
            elif response.status_code == 429:  # Rate limit exceeded
                if attempt < self.max_retry_attempt:
                    # Calculate exponential backoff delay: base_delay * 2^attempt
                    delay = self.retry_delay_sec * (2 ** attempt)
                    self.logger.warning(
                        f"Rate limit (429) hit. Retrying in {delay:.1f}s "
                        f"(attempt {attempt + 1}/{self.max_retry_attempt})"
                    )
                    time.sleep(delay)
                    continue  # Retry the request
                else:
                    # Log final failure after exhausting retries
                    self.logger.error(f"Max retries ({self.max_retry_attempt}) exceeded for rate limit on question: {question}")
                    return None
            else:
                # Log unexpected status codes with response details
                self.logger.error(
                    f"API request failed with status {response.status_code} "
                    f"{response.text}"
                )
                return None

        # This line is theoretically unreachable due to the loop structure,
        # but included for completeness and static analysis tools
        return None

# end llm_client.py
