# begin llm_utils.py
"""Shared LLM utilities used by both the tutor and prompt pipeline.

Extracted from entrypoint.py to eliminate circular imports between
entrypoint.py and prompt_pipeline/entrypoint.py.
"""

import logging
import os

from typing import Any, Dict, Tuple

from llm_configs import (
    ClaudeConfig,
    GeminiConfig,
    GrokConfig,
    NvidiaNIMConfig,
    PerplexityConfig,
)


logging.basicConfig(level=logging.INFO)


def get_startwith(key: str, dictionary: dict) -> Any:
    result = None
    for k, v in dictionary.items():
        if key.startswith(k):
            result = v
            break
    return result


def get_api_key_dict_from_env() -> Dict[str, str]:
    """
    Retrieves API keys for different models from environment variables.
    Returns empty strings for unset variables.
    """
    return {
        'claude': os.getenv('INPUT_CLAUDE_API_KEY', ''),
        'gemini': os.getenv('INPUT_GEMINI-API-KEY', ''),
        'grok': os.getenv('INPUT_GROK-API-KEY', ''),
        'nvidia_nim': os.getenv('INPUT_NVIDIA-API-KEY', ''),
        'perplexity': os.getenv('INPUT_PERPLEXITY-API-KEY', ''),
    }


def get_config_class_dict() -> Dict[str, type]:
    """
    Returns a dictionary mapping model names to their respective configuration classes.
    """
    return {
        'claude': ClaudeConfig,
        'claude-sonnet-4-20250514': ClaudeConfig,  # Add specific model
        'gemini': GeminiConfig,
        'gemini-2.5-flash': GeminiConfig,
        'grok': GrokConfig,
        'grok-code-fast': GrokConfig,
        'nvidia_nim': NvidiaNIMConfig,
        'google/gemma-2-9b-it': NvidiaNIMConfig,  # Add specific model
        'perplexity': PerplexityConfig,
        'sonar': PerplexityConfig  # Add specific model
    }


def get_config_class(model: str) -> type:
    config_map = get_config_class_dict()
    config_class = get_startwith(model, config_map)
    if not config_class:
        raise ValueError(f"Unsupported LLM type: {model}. Use {', '.join(config_map.keys())}")
    return config_class


def get_model_key_from_env() -> Tuple[str, str]:
    """
    Extracts the LLM model and API key from environment variables with flexible selection.
    - Uses INPUT_API-KEY if provided, especially with a specified model.
    - Falls back to model-specific API keys if INPUT_API-KEY is not set.
    - Raises ValueError if no API keys are available.
    - Uses model-to-provider mapping for precise model IDs.
    """
    api_key_dict = get_api_key_dict_from_env()
    valid_keys_dict = {k: v for k, v in api_key_dict.items() if v and v.strip()}

    model = os.getenv('INPUT_MODEL', '').lower()
    general_api_key = os.getenv('INPUT_API-KEY', '').strip()

    # Model-to-provider mapping for precise model IDs
    model_to_provider = {
        'google/gemma-2-9b-it': 'nvidia_nim',
        'sonar': 'perplexity',
        'gemini-2.5-flash': 'gemini',
        'grok-code-fast': 'grok',
        'claude-sonnet-4-20250514': 'claude'
    }

    # Case 1: Use INPUT_API-KEY if provided
    if general_api_key:
        selected_model = model or 'gemini-2.5-flash'  # Default to specific Gemini model
        logging.info(f"Using INPUT_API-KEY for model: {selected_model}")
        return selected_model, general_api_key

    # Case 2: No INPUT_API-KEY, check model-specific keys
    if not valid_keys_dict:
        raise ValueError(
            "No API keys provided. Set at least one of:\n"
            "\tINPUT_API-KEY\n"
            "\tINPUT_CLAUDE_API_KEY\n"
            "\tINPUT_GEMINI-API-KEY\n"
            "\tINPUT_GROK-API-KEY\n"
            "\tINPUT_NVIDIA-API-KEY\n"
            "\tINPUT_PERPLEXITY-API-KEY\n"
        )

    # Case 3: Only one API key available
    if len(valid_keys_dict) == 1:
        selected_model, api_key = next(iter(valid_keys_dict.items()))
        logging.info(f"Using single available model: {selected_model}")
        return selected_model, api_key.strip()

    # Case 4: Use model-to-provider mapping for specified model
    provider = model_to_provider.get(model, None)
    if model and provider and provider in valid_keys_dict:
        logging.info(f"Using mapped model: {model} with provider: {provider}")
        return model, valid_keys_dict[provider].strip()

    # Case 5: Fallback to provider-based matching
    if model:
        api_key = get_startwith(model, valid_keys_dict)
        if api_key:
            logging.info(f"Using specified model with provider matching: {model}")
            return model, api_key.strip()

    # Case 6: Fallback to Gemini if available
    if 'gemini' in valid_keys_dict:
        logging.info("Falling back to Gemini model")
        return 'gemini-2.5-flash', valid_keys_dict['gemini'].strip()

    # Case 7: No matching model or Gemini
    raise ValueError(
        f"No API key provided for specified model '{model}' and Gemini not available. "
        f"Available models: {', '.join(valid_keys_dict.keys())}"
    )

# end llm_utils.py
