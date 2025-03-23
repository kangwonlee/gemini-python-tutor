#!/usr/bin/env python3
# begin entrypoint.py

import logging
import os
import pathlib
import sys

from typing import Any, Tuple

from llm_client import LLMAPIClient
from llm_configs import GeminiConfig, GrokConfig, NvidiaNIMConfig

import prompt


logging.basicConfig(level=logging.INFO)


def main(b_ask:bool) -> None:
    # Input parsing from environment variables
    report_files_str = os.environ['INPUT_REPORT-FILES']
    report_files = get_path_tuple(report_files_str)

    student_files_str = os.environ['INPUT_STUDENT-FILES']
    student_files = get_path_tuple(student_files_str)

    readme_file_str = os.environ['INPUT_README-PATH']
    readme_file = pathlib.Path(readme_file_str)
    assert readme_file.exists(), 'No README file found'

    model, api_key = get_model_key_from_env()

    explanation_in = os.environ.get('INPUT_EXPLANATION-IN', 'English')
    github_repo = os.environ.get('GITHUB_REPOSITORY', 'unknown/repository')

    b_fail_expected = ('true' == os.getenv('INPUT_FAIL-EXPECTED', 'false').lower())

    config_class = get_config_class(model)

    config_args = {'api_key': api_key}
    if model:
        config_args['model'] = model
    config = config_class(**config_args)
    client = LLMAPIClient(config)

    # Generate prompt
    logging.info("Starting feedback generation process...")
    logging.info(f"Report paths: {report_files}")
    logging.info(f"Student files: {student_files}")
    logging.info(f"Readme file: {readme_file}")
    logging.info(f"Using LLM: {model} for repository: {github_repo}")

    n_failed, question = prompt.engineering(report_files, student_files, readme_file, explanation_in)

    if b_ask:
        logging.info(f"Calling {model} API for feedback...")
        # Get feedback from LLM
        feedback = client.call_api(question)
        if not feedback:
            logging.error("Failed to get feedback from LLM")
            sys.exit(1)
        else:
            logging.info("Feedback received successfully")
    else:
        feedback = "Feedback not requested"

    # Enhance feedback with repository context
    feedback_with_context = f"Feedback for {github_repo}:\n\n{feedback}"
    print(feedback_with_context)

    # Write to GITHUB_STEP_SUMMARY if available (GitHub Action context)
    if os.getenv('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f:
            f.write(feedback_with_context)
    elif b_fail_expected:
        assert n_failed > 0, 'No failed tests detected when failure was expected'
    else:
        assert n_failed == 0, 'Unexpected test failures detected'


def get_startwith(key:Any, dictionary:dict) -> Any:
    result = None

    for k, v in dictionary.items():
        if key.startswith(k):
            result = v
            break

    return result


def get_model_key_from_env() -> Tuple[str, str]:
    """
    Extracts the LLM model and API key from environment variables.
    """
    model = os.environ['INPUT_MODEL'].lower()
    api_key_dict = {
        'gemini': os.getenv('INPUT_GEMINI-API-KEY', '').strip(),
        'grok': os.getenv('INPUT_GROK-API-KEY', '').strip(),
        'nvidia_nim': os.getenv('INPUT_NVIDIA-API-KEY', '').strip()
    }

    api_key = get_startwith(model, api_key_dict)

    if not api_key:
        raise ValueError(
            (
                f"No API key provided for {model}.\n"
                f"Keys available for models : {', '.join(api_key_dict.keys())}\n"
            )
        )

    assert api_key, f"No API key provided for {model}. Check INPUT_{model.upper()}-API-KEY"
    return model, api_key


def get_config_class(model: str) -> type:

    # Configure LLM client
    config_map = {
        'gemini': GeminiConfig,
        'grok': GrokConfig,
        'nvidia_nim': NvidiaNIMConfig
    }

    config_class = get_startwith(model, config_map)

    if not config_class:
        raise ValueError(f"Unsupported LLM type: {model}. Use 'gemini', 'grok', or 'nvidia_nim'")

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
