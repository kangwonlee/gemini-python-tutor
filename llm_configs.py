# begin llm_configs.py
from dataclasses import dataclass
from typing import Dict, Any


# Type hint
HEADER = Dict[str, str]


@dataclass
class LLMConfig:
    """Base configuration class for LLM APIs."""

    api_key: str
    api_url: str
    model: str
    default_headers: HEADER = None

    def __post_init__(self):
        if self.default_headers is None:
            self.default_headers = {"Content-Type": "application/json"}

    def get_headers(self) -> HEADER:
        """Returns headers with Authorization token by default."""
        headers = self.default_headers.copy()
        headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def format_request_data(self, question: str) -> Dict[str, Any]:
        """Default request payload formatting, suitable for OpenAI-like APIs."""
        return {
            "model": self.model,
            "messages": [{"role": "user", "content": question}],
            "temperature": 0.2,
            "top_p": 0.7,
            "max_tokens": 1024,
            "stream": False
        }

    def parse_response(self, response_json: Dict) -> str:
        """Parses the API response to extract the answer."""
        raise NotImplementedError("Subclasses must implement parse_response()")


@dataclass
class GeminiConfig(LLMConfig):
    """
    Configuration for Google's Gemini API.
    References:
        https://ai.google.dev/gemini-api/docs/quickstart
    """

    model: str = "gemini-2.0-flash"

    def __post_init__(self):
        super().__post_init__()
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def get_headers(self) -> HEADER:
        """Gemini uses API key in URL, not headers."""
        return self.default_headers.copy()  # No Authorization header

    def format_request_data(self, question: str) -> Dict[str, Any]:
        return {"contents": [{"parts": [{"text": question}]}]}

    def parse_response(self, response_json: Dict) -> str:
        return '\n'.join(part['text'] for part in response_json['candidates'][0]['content']['parts'])


@dataclass
class GrokConfig(LLMConfig):
    """
    Configuration for xAI's Grok API.
    References:
        https://docs.x.ai/docs/api-reference
    """

    model: str = "grok-2-latest"
    api_url: str = "https://api.x.ai/v1/chat/completions"

    def format_request_data(self, question: str) -> Dict[str, Any]:
        return {
            "messages": [{"role": "user", "content": question}],
            "model": self.model,
            "stream": False,
            "temperature": 0
        }

    def parse_response(self, response_json: Dict) -> str:
        return response_json["choices"][0]["message"]["content"]


@dataclass
class NvidiaNIMConfig(LLMConfig):
    """
    Configuration for NVIDIA's NIM API.
    References:
        https://docs.nvidia.com/nim/large-language-models/latest/api-reference.html
        https://docs.nvidia.com/nim/large-language-models/latest/models.html
    """

    model: str = "google/gemma-2-9b-it" # or 'meta/llama-3.1-8b-instruct
    api_url: str = "https://integrate.api.nvidia.com/v1/chat/completions"

    def parse_response(self, response_json: Dict) -> str:
        return response_json["choices"][0]["message"]["content"]

# end llm_configs.py
