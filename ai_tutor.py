import functools
import json
import logging
import pathlib
import re
import time
from typing import Dict, List, Tuple

import requests


HEADER = Dict[str, str]


logging.basicConfig(level=logging.INFO)


RESOURCE_EXHAUSTED = 429


@functools.lru_cache
def url(api_key:str, model:str='gemini-2.0-flash') -> str:
    return f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}'


@functools.lru_cache
def header() -> HEADER:
    return {'Content-Type': 'application/json'}


def ask_gemini(
            question: str,
            api_key:str,
            model:str='gemini-2.0-flash',
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

        response = requests.post(
            url(api_key, model=model),
            headers=header,
            json=data
        )

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
        readme_file:pathlib.Path,
        api_key:str,
        explanation_in:str='Korean',
        model:str='gemini-2.0-flash',
    ) -> Tuple[int, str]:
    '''
    Queries the Gemini API to provide explanations for failed pytest test cases.

    Args:
        report_paths: A list of pathlib.Path objects representing the paths to JSON pytest report files.
        student_files: A list of pathlib.Path objects representing the paths to student's Python files.
        readme_file: A pathlib.Path object representing the path to the assignment instruction file.

    Returns:
        A string containing the feedback from Gemini.
    '''
    logging.info("Starting Gemini Q&A process...")
    logging.info(f"Report paths: {report_paths}")
    logging.info(f"Student files: {student_files}")
    logging.info(f"Readme file: {readme_file}")

    n_failed, consolidated_question = get_prompt(
        report_paths,
        student_files,
        readme_file,
        explanation_in
    )

    answers = ask_gemini(consolidated_question, api_key, model=model)

    return n_failed, answers


def get_prompt(
        report_paths:Tuple[pathlib.Path],
        student_files:Tuple[pathlib.Path],
        readme_file:pathlib.Path,
        explanation_in:str,
    ) -> Tuple[int, str]:
    pytest_longrepr_list = collect_longrepr_from_multiple_reports(report_paths, explanation_in)

    n_failed_tests = len(pytest_longrepr_list)


    def get_initial_instruction(questions:List[str],language:str) -> str:
        # Add the main directive or instruction based on whether there are failed tests
        if questions:
            initial_instruction = (
                get_directive(language) + '\n' +
                'Please generate comments mutually exclusive and collectively exhaustive for the following failed test cases.'
            )
        else:
            initial_instruction = f'In {language}, please comment on the student code given the assignment instruction.'
        return initial_instruction

    
    prompt_list = (
        # Add the header
        [
            get_initial_instruction(pytest_longrepr_list, explanation_in),
            get_instruction_block(readme_file, explanation_in,),
            get_student_code_block(student_files, explanation_in,),
        ]
        + pytest_longrepr_list
        # Add the footer
        + [
        ]
    )

    # Join all questions into a single string
    prompt_str = "\n\n".join(prompt_list)

    return n_failed_tests, prompt_str


def collect_longrepr_from_multiple_reports(pytest_json_report_paths:Tuple[pathlib.Path], explanation_in:str) -> List[str]:
    questions = []

    # Process each report file
    for pytest_json_report_path in pytest_json_report_paths:
        logging.info(f"Processing report file: {pytest_json_report_path}")
        data = json.loads(pytest_json_report_path.read_text())

        longrepr_list = collect_longrepr(data)

        questions += longrepr_list

    if questions:
        questions.insert(0, get_report_header(explanation_in))
        questions.append(get_report_footer(explanation_in))

    return questions


@functools.lru_cache
def get_directive(explanation_in:str) -> str:
    return f"{load_locale(explanation_in)['directive']}\n"


def collect_longrepr(data:Dict[str, str]) -> List[str]:
    longrepr_list = []
    # Collect questions from tests not-passed yet
    for r in data['tests']:
        if r['outcome'] != 'passed':
            for k in r:
                if isinstance(r[k], dict) and 'longrepr' in r[k]:
                    longrepr_list.append(r['outcome'] + ':' + k + ':' + r[k]['longrepr'])
    return longrepr_list


@functools.lru_cache
def get_report_header(explanation_in:str) -> str:

    return (
        f"## {load_locale(explanation_in)['report_header']}\n"
    )


@functools.lru_cache
def get_report_footer(explanation_in:str) -> str:

    return (
        f"## {load_locale(explanation_in)['report_footer']}\n"
    )


def get_instruction_block(readme_file:pathlib.Path, explanation_in:str='Korean',) -> str:

    return (
        f"## {load_locale(explanation_in)['instruction_start']}\n"
        f"{assignment_instruction(readme_file)}\n"
        f"## {load_locale(explanation_in)['instruction_end']}\n"
    )


def get_student_code_block(student_files:Tuple[pathlib.Path], explanation_in:str) -> str:

    return (
        "\n"
        "\n"
        "##### Start mutable code block\n"
        "## {load_locale(explanation_in)['homework_start']}\n"
        f"{assignment_code(student_files)}\n"
        f"## {load_locale(explanation_in)['homework_end']}\n"
        "##### End mutable code block\n"
    )


@functools.lru_cache
def assignment_code(student_files:Tuple[pathlib.Path]) -> str:
    return '\n\n'.join([f"# begin : {str(f.name)} ======\n{f.read_text()}\n# end : {str(f.name)} ======\n" for f in student_files])


@functools.lru_cache
def assignment_instruction(
    readme_file: pathlib.Path,
    common_content_start_marker: str = r"``From here is common to all assignments\.``",
    common_content_end_marker: str = r"``Until here is common to all assignments\.``",
) -> str:
    """Extracts assignment-specific instructions from a README.md file.

    This function reads a README.md file and removes content marked as common
    to all assignments, returning only the assignment-specific instructions.

    Args:
        readme_file: Path to the README.md file.
        common_content_start_marker: The marker indicating the start of common content.
        common_content_end_marker: The marker indicating the end of common content.

    Returns:
        A string containing the assignment-specific instructions.
    """

    return exclude_common_contents(
        readme_file.read_text(),
        common_content_start_marker,
        common_content_end_marker,
    )  # Single exit point


def exclude_common_contents(
    readme_content:str,
    common_content_start_marker: str = r"``From here is common to all assignments.``",
    common_content_end_marker: str = r"``Until here is common to all assignments.``",
) -> str:
    """Removes common content from a string.

    This function takes a string and removes the content between the specified
    start and end markers.

    Args:
        readme_content: The input string containing the README content.
        common_content_start_marker: The marker indicating the start of common content.
        common_content_end_marker: The marker indicating the end of common content.

    Returns:
        A string with the common content removed.
    """
    # Include the markers in the pattern itself
    pattern = rf"({common_content_start_marker}\s*.*?\s*{common_content_end_marker})"
    found_list = re.findall(pattern, readme_content, re.DOTALL | re.IGNORECASE)

    instruction = str(readme_content)

    if not found_list:
        logging.warning(f"Common content markers '{common_content_start_marker}' and '{common_content_end_marker}' not found in README.md. Returning entire file.")
    else:
        for found in found_list:
            # Remove the common content
            instruction = instruction.replace(found, "")

    return instruction


@functools.lru_cache(maxsize=None)
def load_locale(explain_in:str) -> Dict[str, str]:
    locale_folder = pathlib.Path(__file__).parent/'locale'
    assert locale_folder.exists(), f"Locale folder not found: {locale_folder}"
    assert locale_folder.is_dir(), f"Locale folder is not a directory: {locale_folder}"

    locale_file = locale_folder/f'{explain_in}.json'
    assert locale_file.exists(), f"Locale file not found: {locale_file}"
    assert locale_file.is_file(), f"Locale file is not a file: {locale_file}"

    return json.loads(locale_file.read_text())
