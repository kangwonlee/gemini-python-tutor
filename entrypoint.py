#!/usr/bin/env python3
# begin entrypoint.py

import json
import logging
import os
import pathlib
import sys

from typing import Any, Dict, Optional, Tuple


sys.path.insert(
    0,
    str(pathlib.Path(__file__).parent.resolve())
)


from llm_client import LLMAPIClient
from llm_utils import get_config_class, get_model_key_from_env

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

    # Write token usage to artifact directory if available
    output_dir = os.getenv('INPUT_OUTPUT-DIR', '')
    if output_dir and b_ask:
        write_token_usage(client, model, pathlib.Path(output_dir))


def extract_token_usage(raw_response: Optional[dict]) -> Dict[str, Any]:
    """Extract token usage from LLM API response (best-effort, multi-provider).

    Different providers return usage in different structures:
      Gemini:     usageMetadata.promptTokenCount / candidatesTokenCount
      Claude:     usage.input_tokens / output_tokens
      OpenAI-like: usage.prompt_tokens / completion_tokens (Grok, NVIDIA, Perplexity)

    Returns dict with input_tokens, output_tokens, total_tokens (None if unavailable).
    """
    if not raw_response or not isinstance(raw_response, dict):
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None}

    # Gemini format
    usage = raw_response.get("usageMetadata", {})
    if usage:
        return {
            "input_tokens": usage.get("promptTokenCount"),
            "output_tokens": usage.get("candidatesTokenCount"),
            "total_tokens": usage.get("totalTokenCount"),
        }

    # Claude / OpenAI-compatible format
    usage = raw_response.get("usage", {})
    if usage:
        input_t = usage.get("input_tokens") or usage.get("prompt_tokens")
        output_t = usage.get("output_tokens") or usage.get("completion_tokens")
        total_t = usage.get("total_tokens")
        if total_t is None and input_t is not None and output_t is not None:
            total_t = input_t + output_t
        return {
            "input_tokens": input_t,
            "output_tokens": output_t,
            "total_tokens": total_t,
        }

    return {"input_tokens": None, "output_tokens": None, "total_tokens": None}


def write_token_usage(
    client: 'LLMAPIClient',
    model: str,
    output_dir: pathlib.Path,
) -> None:
    """Write token_usage.json to output directory."""
    usage = extract_token_usage(client.last_raw_response)
    usage["model"] = model

    output_dir.mkdir(parents=True, exist_ok=True)
    usage_path = output_dir / "token_usage.json"
    try:
        with open(usage_path, "w", encoding="utf-8") as f:
            json.dump(usage, f, indent=2)
        logging.info(f"Token usage written to {usage_path}: {usage}")
    except OSError as e:
        logging.warning(f"Could not write token usage: {e}")


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
