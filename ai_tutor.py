# begin ai_tutor.py
import functools
import json
import logging
import pathlib
import re

from typing import Dict, List, Tuple


logging.basicConfig(level=logging.INFO)


def generate_feedback(
    report_paths:List[pathlib.Path],
    student_files:List[pathlib.Path],
    readme_file:pathlib.Path,
    explanation_in:str = 'Korean'
) -> Tuple[int, str]:
    """
    Generates a prompt for an LLM to provide feedback on student code.
    Returns the number of failed tests and the prompt string.
    """

    n_failed, consolidated_question = get_prompt(
        report_paths,
        student_files,
        readme_file,
        explanation_in
    )
    return n_failed, consolidated_question


def get_prompt(
    report_paths:List[pathlib.Path],
    student_files:List[pathlib.Path],
    readme_file:pathlib.Path,
    explanation_in:str
) -> Tuple[int, str]:
    """Constructs the prompt from test reports, code, and instructions."""
    pytest_longrepr_list = collect_longrepr_from_multiple_reports(report_paths, explanation_in)

    n_failed_tests = len(pytest_longrepr_list)


    def get_initial_instruction(questions:List[str], language:str) -> str:
        if questions:
            return (
                get_directive(language) + '\n' +
                'Please generate comments mutually exclusive and collectively exhaustive for the following failed test cases.'
            )
        return f'In {language}, please comment on the student code given the assignment instruction.'


    prompt_list = (
        [
            get_initial_instruction(pytest_longrepr_list, explanation_in),
            get_instruction_block(readme_file, explanation_in),
            get_student_code_block(student_files, explanation_in),
        ]
        + pytest_longrepr_list
    )
    prompt_str = "\n\n".join(prompt_list)
    return n_failed_tests, prompt_str


def collect_longrepr_from_multiple_reports(
    pytest_json_report_paths:List[pathlib.Path],
    explanation_in:str
) -> List[str]:
    """Collects test failure details from multiple pytest JSON reports."""
    questions = []

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


def collect_longrepr(data: Dict[str, str]) -> List[str]:
    """Extracts longrepr and stderr from failed tests."""
    longrepr_list = []
    for r in data['tests']:
        if r['outcome'] != 'passed':
            for k in r:
                if isinstance(r[k], dict) and 'longrepr' in r[k]:
                    longrepr_list.append(f"{r['outcome']}:{k}: longrepr begin:{r[k]['longrepr']}:longrepr end\n")
                if isinstance(r[k], dict) and 'stderr' in r[k]:
                    longrepr_list.append(f"{r['outcome']}:{k}: stderr begin:{r[k]['stderr']}:stderr end\n")
    return longrepr_list


@functools.lru_cache
def get_report_header(explanation_in:str) -> str:
    return f"## {load_locale(explanation_in)['report_header']}\n"


@functools.lru_cache
def get_report_footer(explanation_in:str) -> str:
    return f"## {load_locale(explanation_in)['report_footer']}\n"


def get_instruction_block(readme_file:pathlib.Path, explanation_in:str) -> str:
    return (
        f"## {load_locale(explanation_in)['instruction_start']}\n"
        f"{assignment_instruction(readme_file)}\n"
        f"## {load_locale(explanation_in)['instruction_end']}\n"
    )


def get_student_code_block(student_files:List[pathlib.Path], explanation_in:str) -> str:
    return (
        "\n\n##### Start mutable code block\n"
        f"## {{load_locale('{explanation_in}')['homework_start']}}\n"
        f"{assignment_code(student_files)}\n"
        f"## {{load_locale('{explanation_in}')['homework_end']}}\n"
        "##### End mutable code block\n"
    )


@functools.lru_cache
def assignment_code(student_files:List[pathlib.Path]) -> str:
    return '\n\n'.join(
        [
            f"# begin: {f.name} ======\n{f.read_text()}\n# end: {f.name} ======" for f in student_files
        ]
    )


@functools.lru_cache
def assignment_instruction(
    readme_file:pathlib.Path,
    common_content_start_marker:str = r"``From here is common to all assignments\.``",
    common_content_end_marker:str = r"``Until here is common to all assignments\.``",
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
    )


def exclude_common_contents(
    readme_content:str,
    common_content_start_marker:str = r"``From here is common to all assignments\.``",
    common_content_end_marker:str = r"``Until here is common to all assignments\.``",
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

    instruction = readme_content

    if not found_list:
        logging.warning(f"Common content markers not found in README.md. Returning entire file.")
    else:
        for found in found_list:
            # Remove the common content
            instruction = instruction.replace(found, "")

    return instruction


@functools.lru_cache(maxsize=None)
def load_locale(explain_in:str) -> Dict[str, str]:
    """Loads language-specific strings from JSON files in locale/ directory."""
    locale_folder = pathlib.Path(__file__).parent / 'locale'
    assert locale_folder.exists(), f"Locale folder not found: {locale_folder}"
    assert locale_folder.is_dir(), f"Locale folder is not a directory: {locale_folder}"

    locale_file = locale_folder / f'{explain_in}.json'
    assert locale_file.exists(), f"Locale file not found: {locale_file}"
    assert locale_file.is_file(), f"Locale file is not a file: {locale_file}"

    return json.loads(locale_file.read_text())
# end ai_tutor.py
