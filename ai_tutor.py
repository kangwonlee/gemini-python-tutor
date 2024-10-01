import functools
import json
import logging
import os
import pathlib
import time

from typing import Dict, List, Tuple


import pytest
import requests


HEADER = Dict[str, str]
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


logging.basicConfig(level=logging.INFO)


RESOURCE_EXHAUSTED = 429


def test_API_key():
    assert GOOGLE_API_KEY, 'API KEY NOT Available'


@functools.lru_cache
def url() -> str:
    return f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GOOGLE_API_KEY}'


@functools.lru_cache
def header() -> HEADER:
    return {'Content-Type': 'application/json'}


def ask_gemini(
            question: str,
            url:str=url(),
            header:HEADER=header(),
            retry_delay_sec: float = 5.0,
            max_retry_attempt: int = 3,
            timeout_sec: int = 60
    ) -> str:
    """
    Asks a question to Gemini with rate limiting, retry logic, and timeout.

    Args:
        question: The question to ask.
        url: The Gemini API URL.
        header: The request headers.
        retry_delay_sec: The initial delay in seconds between retries.
        max_retry_attempt: The maximum number of retry attempts.
        timeout_sec: The maximum time in seconds allowed for retries.

    Returns:
        The answer from Gemini or None if all retries fail or timeout is reached.
    """

    data = {'contents': [{'parts': [{'text': question}]}]}
    start_time = time.monotonic()
    answer = None  # Initialize the answer variable

    for attempt in range(max_retry_attempt + 1):
        if time.monotonic() - start_time > timeout_sec:
            logging.error(f"Timeout exceeded for question: {question}")
            break  # Exit the loop on timeout

        response = requests.post(url, headers=header, json=data)

        if response.status_code == 200:
            result = response.json()
            results = [part['text'] for part in result['candidates'][0]['content']['parts']]
            answer = '\n'.join(results)
            break  # Exit the loop on success

        elif response.status_code == RESOURCE_EXHAUSTED:
            if attempt < max_retry_attempt:
                delay = retry_delay_sec * (2 ** attempt)
                logging.warning(f"Rate limit exceeded. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retry_attempt})")
                time.sleep(delay)
            else:
                logging.error(f"Max retries exceeded for RESOURCE_EXHAUSTED error. Question: {question}")

        else:
            logging.error(f"API request failed with status code {response.status_code}: {response.text}")

    return answer  # Return the answer (or None if unsuccessful) at the end


def gemini_qna(
        report_paths:List[pathlib.Path],
        student_files:List[pathlib.Path],
        readme_file:pathlib.Path
    ) -> str:
    '''
    Queries the Gemini API to provide explanations for failed pytest test cases.

    Args:
        report_paths: A list of pathlib.Path objects representing the paths to JSON pytest report files.
        student_files: A list of pathlib.Path objects representing the paths to student's Python files.
        readme_file: A pathlib.Path object representing the path to the assignment instruction file.

    Returns:
        A string containing the feedback from Gemini.
    '''
    answers = None
    try:
        message_count = 0
        questions = [
            "# 숙제 답안으로 제출한 코드가 오류를 일으킨 원인을 입문자 용어만으로 중복 없는 간결한 문장으로 설명하시오.:\n"
        ]  # Collect all questions in a list

        # Process each report file
        for report_path in report_paths:
            data = json.loads(report_path.read_text())

            longrepr_list = collect_longrepr(data)

            message_count += len(longrepr_list)
            questions += longrepr_list

        # Query Gemini with consolidated questions if there are any
        if questions:
            consolidated_question = "\n\n".join(questions) + get_code_instruction(readme_file, student_files)  # Add code & instruction only once
            answers = ask_gemini(consolidated_question)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        answers = "An unexpected error occurred while processing your request."

    return answers


def collect_longrepr(data:Dict[str, str]) -> List[str]:
    longrepr_list = []
    # Collect questions from tests not-passed yet
    for r in data['tests']:
        if r['outcome'] != 'passed':
            for k in r:
                if isinstance(r[k], dict) and 'longrepr' in r[k]:
                    longrepr_list.append(r['outcome'] + ':' + k + ':' + r[k]['longrepr'])
    return longrepr_list


def get_question(longrepr:str) -> str:
    return (
        get_question_header() + f"{longrepr}\n" + get_question_footer()
    )


@functools.lru_cache
def get_question_header() -> str:
    return (
        "## 오류 메시지 시작\n"
    )


@functools.lru_cache
def get_question_footer() -> str:
    return (
        "## 오류 메시지 끝\n"
    )


def get_code_instruction(
        student_files,
        readme_file:pathlib.Path,
    ) -> str:
    return (
        "\n\n## 숙제 제출 코드 시작\n"
        f"{assignment_code(student_files)}\n"
        "## 숙제 제출 코드 끝\n"
        "## 과제 지침 시작\n"
        f"{assignment_instruction(readme_file)}\n"
        "## 과제 지침 끝\n"
    )


@functools.lru_cache
def assignment_code(student_files:Tuple[pathlib.Path]) -> str:
    return '\n\n'.join([f"# begin : {str(f.name)} ======\n{f.read_text()}\n# end : {str(f.name)} ======\n" for f in student_files])


@functools.lru_cache
def assignment_instruction(readme_file:pathlib.Path) -> str:
    return readme_file.read_text()
