# begin llm_configs.py
from dataclasses import dataclass
from typing import Dict, Any


# Type alias for headers dictionary to improve code readability and type hinting
HEADER = Dict[str, str]


@dataclass
class LLMConfig:
    """Base configuration class for LLM APIs.

    This class provides a foundation for configuring API connections to various
    Large Language Model services with common attributes and methods.

    Attributes:
        api_key (str): Authentication key for the API
        api_url (str): Base URL endpoint for the API
        model (str): Specific model identifier to use
        default_headers (HEADER, optional): Default HTTP headers. Defaults to None.
    """

    api_key: str
    api_url: str
    model: str
    default_headers: HEADER = None

    def __post_init__(self):
        """Initialize default headers if not provided.

        Sets up default headers with JSON content type if none were specified
        during instantiation.
        """
        if self.default_headers is None:
            self.default_headers = {"Content-Type": "application/json"}

        if not self.api_key.strip():
            raise ValueError("API key is required")

    def get_headers(self) -> HEADER:
        """Returns headers with Authorization token by default.

        Creates a copy of default headers and adds Bearer token authorization.

        Returns:
            HEADER: Dictionary containing HTTP headers with authorization
        """
        headers = self.default_headers.copy()
        headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def format_request_data(self, question: str) -> Dict[str, Any]:
        """Default request payload formatting, suitable for OpenAI-like APIs.

        Creates a standardized request payload compatible with many LLM APIs.

        Args:
            question (str): The input prompt or question to send to the API

        Returns:
            Dict[str, Any]: Formatted request payload
        """
        return {
            "model": self.model,
            "messages": [{"role": "user", "content": question}],
            "temperature": 0.2, # Controls randomness, lower is more deterministic
            "top_p": 0.7,       # Nucleus sampling parameter
            "max_tokens": 96,   # Maximum response length
            "stream": False     # Disable streaming response
        }

    def parse_response(self, response_json: Dict) -> str:
        """Parses the API response to extract the answer.

        Args:
            response_json (Dict): Raw JSON response from API

        Returns:
            str: Extracted response text

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement parse_response()")


@dataclass
class GeminiConfig(LLMConfig):
    """
    Configuration for Google's Gemini API.

    Specialized configuration for interacting with Google's Gemini API,
    inheriting from LLMConfig with Gemini-specific defaults and formatting.

    References:
        https://ai.google.dev/gemini-api/docs/quickstart

    Attributes:
        api_url (str, optional): API endpoint URL. Defaults to None.
        model (str): Default Gemini model version. Defaults to "gemini-2.0-flash".
    """

    api_url: str = None
    model: str = "gemini-2.0-flash"

    def __post_init__(self):
        """Initialize Gemini-specific URL with API key.

        Sets up the complete API URL including the model and API key if not
        provided during instantiation.
        """
        super().__post_init__()
        if self.api_url is None:
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def get_headers(self) -> HEADER:
        """Gemini uses API key in URL, not headers.

        Returns just the default headers without Authorization token since
        Gemini handles authentication via URL parameter.

        Returns:
            HEADER: Basic HTTP headers without auth token
        """
        return self.default_headers.copy()  # No Authorization header

    def format_request_data(self, question: str) -> Dict[str, Any]:
        """Format request payload for Gemini API.

        Creates Gemini-specific request structure different from OpenAI-style.

        Args:
            question (str): Input prompt or question

        Returns:
            Dict[str, Any]: Gemini-formatted request payload
        """
        return {"contents": [{"parts": [{"text": question}]}]}

    def parse_response(self, response_json: Dict) -> str:
        """Parse Gemini API response to extract text.

        Extracts and joins text parts from Gemini's response structure.

        Args:
            response_json (Dict): Raw JSON response from Gemini API

        Returns:
            str: Concatenated response text
        """
        return '\n'.join(part['text'] for part in response_json['candidates'][0]['content']['parts'])


@dataclass
class GrokConfig(LLMConfig):
    """
    Configuration for xAI's Grok API.

    Specialized configuration for xAI's Grok API with specific defaults.

    References:
        https://docs.x.ai/docs/api-reference

    Attributes:
        model (str): Default Grok model. Defaults to "grok-2-1212".
        api_url (str): Grok API endpoint. Defaults to chat completions URL.
    """

    model: str = "grok-2-1212"
    api_url: str = "https://api.x.ai/v1/chat/completions"

    def format_request_data(self, question: str) -> Dict[str, Any]:
        """Format request payload for Grok API.

        Creates a payload compatible with xAI's Grok API specifications.

        Args:
            question (str): Input prompt or question

        Returns:
            Dict[str, Any]: Grok-formatted request payload
        """
        return {
            "messages": [{"role": "user", "content": question}],
            "model": self.model,
            "stream": False,
            "temperature": 0  # Most deterministic output
        }

    def parse_response(self, response_json: Dict) -> str:
        """Parse Grok API response to extract text.

        Extracts response content from Grok's response structure.

        Args:
            response_json (Dict): Raw JSON response from Grok API

        Returns:
            str: Response text
        """
        return response_json["choices"][0]["message"]["content"]


@dataclass
class NvidiaNIMConfig(LLMConfig):
    """
    Configuration for NVIDIA's NIM API.

    Configuration for NVIDIA's NIM API with specific model and endpoint defaults.

    References:
        https://docs.nvidia.com/nim/large-language-models/latest/api-reference.html
        https://docs.nvidia.com/nim/large-language-models/latest/models.html

    Attributes:
        model (str): Default NIM model. Defaults to "google/gemma-2-9b-it".
        api_url (str): NIM API endpoint URL.
    """

    model: str = "google/gemma-2-9b-it"  # or 'meta/llama-3.1-8b-instruct'
    api_url: str = "https://integrate.api.nvidia.com/v1/chat/completions"

    def parse_response(self, response_json: Dict) -> str:
        """Parse NVIDIA NIM API response to extract text.

        Extracts response content from NIM's response structure.

        Args:
            response_json (Dict): Raw JSON response from NIM API

        Returns:
            str: Response text
        """
        return response_json["choices"][0]["message"]["content"]


@dataclass
class ClaudeConfig(LLMConfig):
    """
    Configuration for Claude API.

    Specialized configuration for Anthropic's Claude API with custom headers.

    References:
        https://docs.anthropic.com/en/api/getting-started

    Attributes:
        api_url (str): Claude API endpoint URL
        model (str): Default Claude model version
        default_headers (HEADER, optional): Custom headers for Claude
    """

    api_url: str = "https://api.anthropic.com/v1/messages"
    model: str = "claude-3-haiku-20240307"
    default_headers: HEADER = None

    def __post_init__(self):
        """Initialize Claude-specific headers.

        Sets up Claude-specific headers including API key and version,
        with validation.

        Raises:
            ValueError: If API key is not provided in headers
        """

        if self.default_headers is None:
            self.default_headers = {
                "x-api-key": self.api_key.strip(),
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }

        if self.default_headers["x-api-key"] is None:
            raise ValueError("API key is required for Claude API")

    def parse_response(self, response_json: Dict) -> str:
        """Parse Claude API response to extract text.

        Extracts response content from Claude's response structure.

        Args:
            response_json (Dict): Raw JSON response from Claude API

        Returns:
            str: Response text
        """
        return response_json["content"][0]["text"]

    def format_request_data(self, question: str) -> Dict[str, Any]:
        '''
        Probably multiple tokens of Claude would be equivalent to 1 token of others
        '''
        result = super().format_request_data(question)
        result['max_tokens'] = 384
        result['messages'][0]['content'] = f'''tokens < {result['max_tokens']}\n''' + result['messages'][0]['content']
        return result


@dataclass
class PerplexityConfig(LLMConfig):
    """
    Configuration for Perplexity API.

    Specialized configuration for Anthropic's Perplexity API with custom headers.

    References:
        https://docs.perplexity.ai/api-reference/chat-completions

    Attributes:
        api_url (str): Perplexity API endpoint URL
        model (str): Default Perplexity model version
        default_headers (HEADER, optional): Custom headers for Perplexity
    """

    api_url: str = "https://api.perplexity.ai/chat/completions"
    model: str = "sonar"
    default_headers: HEADER = None

    def __post_init__(self):
        """Initialize Perplexity-specific headers.

        Sets up Perplexity-specific headers including API key and version,
        with validation.

        Raises:
            ValueError: If API key is not provided in headers
        """

        available = (
            'sonar-deep-research',
            'sonar-reasoning-pro',
            'sonar-reasoning',
            'sonar-pro',
            'sonar',
        )

        if self.model not in available:
            self.model = available[-1]

        if self.default_headers is None:
            self.default_headers = {
                "Authorization": f"Bearer {self.api_key.strip()}",
                "Content-Type": "application/json"
            }

        if self.default_headers["Authorization"].split()[1] is None:
            raise ValueError("API key is required for Perplexity API")

    def parse_response(self, response_json: Dict) -> str:
        """Parse Perplexity API response to extract text.

        Extracts response content from Perplexity's response structure.

        Args:
            response_json (Dict): Raw JSON response from Perplexity API

        Returns:
            str: Response text
        """
        return response_json["content"][0]["text"]

# end llm_configs.py
