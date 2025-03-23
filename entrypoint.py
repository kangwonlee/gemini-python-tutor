#!/usr/bin/env python3
# begin entrypoint.py

import logging
import os
import pathlib
import sys

from typing import Tuple

from llm_client import LLMAPIClient
from llm_configs import GeminiConfig, GrokConfig, NvidiaNIMConfig

import ai_tutor  # Assuming ai_tutor.py was renamed to prompt.py as discussed


logging.basicConfig(level=logging.INFO)


def main() -> None:
    # Input parsing from environment variables
    report_files_str = os.environ['INPUT_REPORT-FILES']
    report_files = get_path_tuple(report_files_str)

    student_files_str = os.environ['INPUT_STUDENT-FILES']
    student_files = get_path_tuple(student_files_str)

    readme_file_str = os.environ['INPUT_README-PATH']
    readme_file = pathlib.Path(readme_file_str)
    assert readme_file.exists(), 'No README file found'

    llm_type = os.environ['INPUT_LLM'].lower()
    api_keys = {
        'gemini': os.environ.get('INPUT_GEMINI-API-KEY', '').strip(),
        'grok': os.environ.get('INPUT_GROK-API-KEY', '').strip(),
        'nvidia_nim': os.environ.get('INPUT_NVIDIA-API-KEY', '').strip()
    }

    # Select API key based on LLM type
    api_key = api_keys.get(llm_type)
    assert api_key, f"No API key provided for {llm_type}. Check INPUT_{llm_type.upper()}-API-KEY"

    model = os.getenv('INPUT_MODEL', '')  # Default set in config if empty
    explanation_in = os.environ.get('INPUT_EXPLANATION-IN', 'English')
    github_repo = os.environ.get('GITHUB_REPOSITORY', 'unknown/repository')

    b_fail_expected = ('true' == os.getenv('INPUT_FAIL-EXPECTED', 'false').lower())

    # Configure LLM client
    config_map = {
        'gemini': GeminiConfig,
        'grok': GrokConfig,
        'nvidia_nim': NvidiaNIMConfig
    }
    config_class = config_map.get(llm_type)
    if not config_class:
        raise ValueError(f"Unsupported LLM type: {llm_type}. Use 'gemini', 'grok', or 'nvidia_nim'")
    
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
    logging.info(f"Using LLM: {llm_type} for repository: {github_repo}")
    
    n_failed, question = prompt.engineering(report_files, student_files, readme_file, explanation_in)
    
    # Get feedback from LLM
    feedback = client.call_api(question)
    if not feedback:
        logging.error("Failed to get feedback from LLM")
        sys.exit(1)

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
