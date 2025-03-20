# begin main.py
import argparse
import logging
import os
import pathlib
import sys

from typing import List

import ai_tutor
from llm_client import LLMAPIClient
from llm_configs import GeminiConfig, GrokConfig, NvidiaNIMConfig


logging.basicConfig(level=logging.INFO)


def main(argv:List[str]):
    parser = argparse.ArgumentParser(description="Generate feedback using a specified LLM.")
    parser.add_argument("--llm", type=str, required=True, choices=['gemini', 'grok', 'nvidia_nim'], help="LLM to use (gemini, grok, nvidia_nim)")
    parser.add_argument("--readme", type=str, required=True, help="Path to README.md")
    parser.add_argument("--code", type=str, required=True, help="Path to student code file")
    parser.add_argument("--json", type=str, required=True, help="Path to pytest JSON report")
    parser.add_argument("--api-key", type=str, help="API key for the selected LLM")
    parser.add_argument("--model", type=str, help="Model to use (overrides default)")
    parser.add_argument("--lang", type=str, default="Korean", help="Language for explanations (default: Korean)")

    args = parser.parse_args(argv[1:])

    # Determine API key from argument or environment variable
    if args.llm == 'gemini':
        api_key = args.api_key or os.getenv('GOOGLE_API_KEY')
        config_class = GeminiConfig
    elif args.llm == 'grok':
        api_key = args.api_key or os.getenv('XAI_API_KEY')
        config_class = GrokConfig
    elif args.llm == 'nvidia_nim':
        api_key = args.api_key or os.getenv('NVIDIA_API_KEY')
        config_class = NvidiaNIMConfig
    else:
        logging.error("Invalid LLM specified.")
        sys.exit(1)

    if not api_key:
        logging.error(f"API key for {args.llm} not provided (use --api-key or set environment variable).")
        sys.exit(1)

    # Prepare configuration with optional model override
    config_args = {'api_key': api_key}
    if args.model:
        config_args['model'] = args.model
    config = config_class(**config_args)

    # Initialize client
    client = LLMAPIClient(config)

    # Prepare file paths
    report_paths = [pathlib.Path(args.json)]
    student_files = [pathlib.Path(args.code)]
    readme_file = pathlib.Path(args.readme)

    # Generate prompt
    n_failed, question = ai_tutor.generate_feedback(report_paths, student_files, readme_file, args.lang)

    # Call API and get response
    answer = client.call_api(question)

    if answer:
        logging.info(f"LLM response: {answer}")
        with open("llm_comment.txt", "w", encoding='utf-8') as f:
            f.write(answer)
    else:
        logging.error("No response received from LLM.")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
# end main.py
