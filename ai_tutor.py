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
    if not GOOGLE_API_KEY:
        pytest.fail('API KEY NOT Available')


def tutor_folder() -> pathlib.Path:
    p = pathlib.Path(__file__).parent.resolve()
    assert p.exists()
    assert p.is_dir()
    return p


def proj_folder(tutor_folder_path:pathlib.Path=tutor_folder()) -> pathlib.Path:
    p = tutor_folder_path.parent.resolve()
    assert p.exists()
    assert p.is_dir()
    return p


def script_path(proj_folder:pathlib.Path=proj_folder()) -> pathlib.Path:
    '''
    Automatically discover ex??.py file
    Force only one ex??.py file in the project folder at the moment
    '''
    exercise_files = tuple(proj_folder.glob('ex*.py'))

    result = None
    if len(exercise_files) == 0:
        raise FileNotFoundError("No Python file starting with 'ex' found in the project folder.")
    elif len(exercise_files) > 1:
        raise ValueError("Multiple Python files starting with 'ex' found in the project folder. Please ensure there is only one.")
    else:
        result = exercise_files[0]

    return result


@pytest.fixture
def report_paths() -> Tuple[pathlib.Path]:
    result = []
    for e_key in os.environ:
        if e_key.endswith('_REPORT'):
            report_path = pathlib.Path(os.environ[e_key])
            assert report_path.exists(), f"does not exist : {report_path}"
            assert report_path.is_file(), f"not a file : {report_path}"
            result.append(report_path)

    assert result, "Could not find report filenames"

    return tuple(result)


@functools.lru_cache
def url() -> str:
    return f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GOOGLE_API_KEY}'


@functools.lru_cache
def header() -> HEADER:
    return {'Content-Type': 'application/json'}


@functools.lru_cache
def assignment_code() -> str:
    return script_path().read_text()


@functools.lru_cache
def assignment_instruction() -> str:
    return (proj_folder() / 'README.md').read_text()


def ask_gemini(question: str, url=url(), header=header(), retry_delay_sec: float = 5.0, max_retry_attempt: int = 3, timeout_sec: int = 60) -> str:
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


def test_json_reports(report_paths:Tuple[pathlib.Path]):
    message_count = gemini_qna(report_paths)

    assert 0 == message_count, (
        "\nplease check Captured stdout call\n"
        "Captured stdout call 메시지를 확인하시오"
    )


def gemini_qna(report_paths):
    '''
    Queries the Gemini API to provide explanations for failed pytest test cases.

    Args:
        report_paths: A tuple of pathlib.Path objects representing the paths to JSON pytest report files.

    Returns:
        The total number of failed test cases processed.
    '''

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
        consolidated_question = "\n\n".join(questions) + get_code_instruction()  # Add code & instruction only once
        answers = ask_gemini(consolidated_question)
        print(answers)  # Print the consolidated answers directly

    return message_count


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


def get_code_instruction():
    return (
        "\n\n## 숙제 제출 코드 시작\n"
        f"{assignment_code()}\n"
        "## 숙제 제출 코드 끝\n"
        "## 과제 지침 시작\n"
        f"{assignment_instruction()}\n"
        "## 과제 지침 끝\n"
    )


if "__main__" == __name__:
    pytest.main([__file__])
