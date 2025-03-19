# begin call_nvidia_nim.py

import argparse
import os
import pathlib
import sys
import time

from typing import List

import requests
import ai_tutor  # Reuse your existing ai_tutor.py


def url() -> str:
    """Returns the NVIDIA NIM API endpoint."""
    return "https://integrate.api.nvidia.com/v1/chat/completions"


def ask_nvidia_nim(
    question: str,
    api_key: str,
    model: str = "google/gemma-2-9b-it",
    header: ai_tutor.HEADER = ai_tutor.header(),
    retry_delay_sec: float = 5.0,
    max_retry_attempt: int = 3,
    timeout_sec: int = 60
) -> str:
    """
    Asks a question to NVIDIA NIM API with rate limiting, retry logic, and timeout.

    Args:
        question: The prompt to send to NVIDIA NIM.
        api_key: The NVIDIA API key.
        model: The model to use (default: google/gemma-2-9b-it).
        header: Request headers (reused from ai_tutor.py).
        retry_delay_sec: Initial delay between retries.
        max_retry_attempt: Max number of retry attempts.
        timeout_sec: Max time allowed for retries.

    Returns:
        The response from NVIDIA NIM or None if unsuccessful.
    """
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": question}
        ],
        "temperature": 0.2,
        "top_p": 0.7,
        "max_tokens": 1024,
        "stream": False  # Non-streaming for simplicity
    }

    header["Authorization"] = f"Bearer {api_key}"

    start_time = time.monotonic()
    answer = None

    for attempt in range(max_retry_attempt + 1):
        if time.monotonic() - start_time > timeout_sec:
            ai_tutor.logging.error(f"Timeout exceeded for question: {question}")
            break

        response = requests.post(
            url(),
            headers=header,
            json=data
        )

        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            break

        elif response.status_code == ai_tutor.RESOURCE_EXHAUSTED:  # 429
            if attempt < max_retry_attempt:
                delay = retry_delay_sec * (2 ** attempt)
                ai_tutor.logging.warning(f"Rate limit hit. Retrying in {delay}s (Attempt {attempt + 1}/{max_retry_attempt})")
                time.sleep(delay)
            else:
                ai_tutor.logging.error(f"Max retries exceeded for rate limit. Question: {question}")
        else:
            ai_tutor.logging.error(f"API failed with status {response.status_code}: {response.text}")

    return answer


def parse_argv(argv:List[str]):
    parser = argparse.ArgumentParser(description="Generate feedback using NVIDIA NIM API.")
    parser.add_argument("--readme", type=str, required=True, help="Path to README.md")
    parser.add_argument("--code", type=str, required=True, help="Path to student code file")
    parser.add_argument("--json", type=str, required=True, help="Path to pytest JSON report")
    parser.add_argument("--api-key", type=str, default=os.getenv("NVIDIA_API_KEY"), help="NVIDIA API key")
    parser.add_argument("--model", type=str, default="google/gemma-2-9b-it", help="NVIDIA model")
    parser.add_argument("--lang", type=str, default="Korean", help="Language for explanations")

    parsed = parser.parse_args(argv)
    return parsed


def main(argv:List[str]):
    parsed = parse_argv(argv)

    if not parsed.api_key:
        ai_tutor.logging.error("NVIDIA_API_KEY not provided or found in environment.")
        sys.exit(1)

    report_paths = [pathlib.Path(parsed.json)]
    student_files = [pathlib.Path(parsed.code)]
    readme_file = pathlib.Path(parsed.readme)

    n_failed, question = ai_tutor.get_prompt(report_paths, student_files, readme_file, parsed.lang)

    answer = ask_nvidia_nim(question, parsed.api_key, model=parsed.model)

    if answer:
        ai_tutor.logging.info(f"NVIDIA NIM response: {answer}")
        with open("llm_comment.txt", "w") as f:
            f.write(answer)
    else:
        ai_tutor.logging.error("No response from NVIDIA NIM.")
        sys.exit(1)


if __name__ == "__main__":
    main()
# end call_nvidia_nim.py
