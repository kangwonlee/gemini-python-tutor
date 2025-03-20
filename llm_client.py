# begin llm_client.py
import logging
import time

from typing import Dict, Optional


import requests


from llm_configs import LLMConfig


class LLMAPIClient:
    """Generic client for interacting with LLM APIs using a configuration."""
    def __init__(self, config: LLMConfig, retry_delay_sec: float = 5.0,
                 max_retry_attempt: int = 3, timeout_sec: int = 60):
        self.config = config
        self.retry_delay_sec = retry_delay_sec
        self.max_retry_attempt = max_retry_attempt
        self.timeout_sec = timeout_sec
        self.logger = logging.getLogger(__name__)

    def call_api(self, question: str) -> Optional[str]:
        """Sends a question to the LLM API with retry and timeout handling."""
        headers = self.config.get_headers()
        data = self.config.format_request_data(question)
        start_time = time.monotonic()
        answer = None

        for attempt in range(self.max_retry_attempt + 1):
            if time.monotonic() - start_time > self.timeout_sec:
                self.logger.error(f"Timeout exceeded for question: {question}")
                break

            response = requests.post(
                self.config.api_url,
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                result = response.json()
                try:
                    answer = self.config.parse_response(result)
                except Exception as e:
                    self.logger.exception(f"Error parsing response: {e}")
                    break
                break
            elif response.status_code == 429:  # Rate limit
                if attempt < self.max_retry_attempt:
                    delay = self.retry_delay_sec * (2 ** attempt)
                    self.logger.warning(f"Rate limit hit. Retrying in {delay}s (Attempt {attempt + 1}/{self.max_retry_attempt})")
                    time.sleep(delay)
                else:
                    self.logger.error(f"Max retries exceeded for rate limit. Question: {question}")
            else:
                self.logger.error(f"API failed with status {response.status_code}: {response.text}")

        return answer
# end llm_client.py
