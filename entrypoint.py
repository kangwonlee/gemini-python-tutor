#!/usr/bin/env python3
# begin entrypoint.py

import logging
import os
import pathlib
import sys

from typing import Any, Dict, Tuple


sys.path.insert(
    0,
    str(pathlib.Path(__file__).parent.resolve())
)


from llm_client import LLMAPIClient
from llm_configs import ClaudeConfig, GeminiConfig, GrokConfig, NvidiaNIMConfig, PerplexityConfig

import prompt


logging.basicConfig(level=logging.INFO)


def main(b_ask:bool=True) -> None:
    # Input parsing from environment variables
    report_files = get_path_tuple(os.environ['INPUT_REPORT-FILES'])
    student_files = get_path_tuple(os.environ['INPUT_STUDENT-FILES'])
    readme_file = pathlib.Path(os.environ['INPUT_README-PATH'])
    assert readme_file.exists(), 'No README file found'

    explanation_in = os.environ.get('INPUT_EXPLANATION-IN', 'English')
    logging.info(f"Using explanation language: {explanation_in}")

    github_repo = os.environ.get('GITHUB_REPOSITORY', 'unknown/repository')
    b_fail_expected = ('true' == os.getenv('INPUT_FAIL-EXPECTED', 'false').lower())

    model, api_key = get_model_key_from_env()
    config_class = get_config_class(model)

    config_args = {'api_key': api_key}
    if model:
        config_args['model'] = model
    config = config_class(**config_args)
    client = LLMAPIClient(config)

    logging.info("Starting feedback generation process...")
    logging.info(f"Report paths: {report_files}")
    logging.info(f"Student files: {student_files}")
    logging.info(f"Readme file: {readme_file}")

    n_failed, question = prompt.engineering(report_files, student_files, readme_file, explanation_in)

    if b_ask:
        logging.info(f"Calling {model} API for feedback...")
        feedback = client.call_api(question)
        if not feedback:
            logging.error("Failed to get feedback from LLM")
            sys.exit(1)
        else:
            logging.info("Feedback received successfully")
    else:
        feedback = "Feedback not requested"

    feedback_with_context = f"Feedback for {github_repo}:\n\n{feedback}"
    print(feedback_with_context)

    # Write to GITHUB_STEP_SUMMARY with error handling for permissions
    if os.getenv('GITHUB_STEP_SUMMARY'):
        try:
            with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f:
                f.write(feedback_with_context)
        except PermissionError as e:
            logging.error(f"Failed to write to GITHUB_STEP_SUMMARY: {e}")
            sys.exit(1)

    elif b_fail_expected:
        assert n_failed > 0, 'No failed tests detected when failure was expected'


def get_startwith(key:str, dictionary:dict) -> Any:
    result = None
    for k, v in dictionary.items():
        if key.startswith(k):
            result = v
            break
    return result


def get_model_key_from_env() -> Tuple[str, str]:
    """
    Extracts the LLM model and API key from environment variables with flexible selection.
    - Uses INPUT_API-KEY if provided, especially with a specified model.
    - Falls back to model-specific API keys if INPUT_API-KEY is not set.
    - Raises ValueError if no API keys are available.
    - Prefers Gemini as default if no model is specified.
    """
    api_key_dict = get_api_key_dict_from_env()
    valid_keys_dict = {k: v for k, v in api_key_dict.items() if v and v.strip()}

    model = os.getenv('INPUT_MODEL', '').lower()
    general_api_key = os.getenv('INPUT_API-KEY', '').strip()

    # Case 1: Use INPUT_API-KEY if provided
    if general_api_key:
        selected_model = model or 'gemini'  # Default to Gemini if no model specified
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

    # Case 4: Multiple API keys available, prefer specified model
    if model:
        api_key = get_startwith(model, valid_keys_dict)
        if api_key:
            logging.info(f"Using specified model: {model}")
            return model, api_key.strip()

    # Case 5: Fallback to Gemini if available
    if 'gemini' in valid_keys_dict:
        logging.info("Falling back to Gemini model")
        return 'gemini', valid_keys_dict['gemini'].strip()

    # Case 6: No matching model or Gemini
    raise ValueError(
        f"No API key provided for specified model '{model}' and Gemini not available. "
        f"Available models: {', '.join(valid_keys_dict.keys())}"
    )


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
        'gemini': GeminiConfig,
        'grok': GrokConfig,
        'nvidia_nim': NvidiaNIMConfig,
        'perplexity': PerplexityConfig,
    }


def get_config_class(model: str) -> type:
    config_map = get_config_class_dict()
    config_class = get_startwith(model, config_map)
    if not config_class:
        raise ValueError(f"Unsupported LLM type: {model}. Use {', '.join(config_map.keys())}")
    return config_class


def get_path_tuple(paths_str: str) -> Tuple[pathlib.Path]:
    """
    Converts a comma-separated string of file paths to a tuple of pathlib.Path objects.
    """
    result_list = []
    for path in map(pathlib.Path, paths_str.split(',')):
        if path.exists():
            result_list.append(path)
        else:
            logging.warning(f"{path} does not exist")
    if not result_list:
        raise ValueError("No valid paths provided")
    return tuple(result_list)


if __name__ == "__main__":
    main()

# end entrypoint.py
