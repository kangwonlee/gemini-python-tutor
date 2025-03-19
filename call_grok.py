# begin call_grok.py
import argparse
import os
import pathlib
import sys
import time


import requests


import ai_tutor  # Reuse existing ai_tutor.py


def url() -> str:
    """Returns the xAI API endpoint for Grok."""
    return "https://api.x.ai/v1/chat/completions"


def ask_grok(
    question: str,
    api_key: str,
    model: str = "grok-2-1212",
    header: ai_tutor.HEADER = ai_tutor.header(),
    retry_delay_sec: float = 5.0,
    max_retry_attempt: int = 3,
    timeout_sec: int = 60
) -> str:
    """
    Asks a question to Grok with rate limiting, retry logic, and timeout.
    
    Args:
        question: The prompt to send to Grok.
        api_key: The xAI API key.
        model: The Grok model to use (default: grok-2-latest).
        header: The request headers (reused from ai_tutor.py).
        retry_delay_sec: Initial delay between retries.
        max_retry_attempt: Max number of retry attempts.
        timeout_sec: Max time allowed for retries.

    Returns:
        The response from Grok or None if unsuccessful.
    """
    # Adapt to xAI's chat completions format
    data = {
        "messages": [
            {"role": "user", "content": question}
        ],
        "model": model,
        "stream": False,
        "temperature": 0  # Keep deterministic for consistency
    }
    
    # Add Authorization header as per xAI API docs
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


def main():
    parser = argparse.ArgumentParser(description="Generate feedback using Grok from xAI.")
    parser.add_argument("--readme", type=str, required=True, help="Path to README.md")
    parser.add_argument("--code", type=str, required=True, help="Path to student code file")
    parser.add_argument("--json", type=str, required=True, help="Path to pytest JSON report")
    parser.add_argument("--api-key", type=str, default=os.getenv("GROK_API_KEY"), help="xAI API key")
    parser.add_argument("--model", type=str, default="grok-2-latest", help="Grok model to use")
    parser.add_argument("--lang", type=str, default="Korean", help="Language for explanations")

    args = parser.parse_args()

    if not args.api_key:
        ai_tutor.logging.error("GROK_API_KEY not provided or found in environment.")
        sys.exit(1)

    # Convert paths to pathlib.Path objects
    report_paths = [pathlib.Path(args.json)]
    student_files = [pathlib.Path(args.code)]
    readme_file = pathlib.Path(args.readme)

    # Generate prompt using ai_tutor.py's logic
    n_failed, question = ai_tutor.get_prompt(report_paths, student_files, readme_file, args.lang)

    # Query Grok
    answer = ask_grok(question, args.api_key, model=args.model)

    if answer:
        ai_tutor.logging.info(f"Grok response: {answer}")
        with open("llm_comment.txt", "w") as f:
            f.write(answer)
    else:
        ai_tutor.logging.error("No response from Grok.")
        sys.exit(1)


if __name__ == "__main__":
    main()
# end call_grok.py
