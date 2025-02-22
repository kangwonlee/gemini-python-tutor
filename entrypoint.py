#!/usr/bin/env -S python3 -B

# NOTE: If you are using an alpine docker image
# such as pyaction-lite, the -S option above won't
# work. The above line works fine on other linux distributions
# such as debian, etc, so the above line will work fine
# if you use pyaction:4.0.0 or higher as your base docker image.

import logging
import os
import pathlib
from typing import Tuple


import ai_tutor


logging.basicConfig(level=logging.INFO)


def main() -> None:
    report_files_str = os.environ['INPUT_REPORT-FILES']
    report_files = get_path_tuple(report_files_str)

    student_files_str = os.environ['INPUT_STUDENT-FILES']
    student_files = get_path_tuple(student_files_str)

    readme_file_str = os.environ['INPUT_README-PATH']
    readme_file = pathlib.Path(readme_file_str)
    assert readme_file.exists(), 'No README file'

    api_key = os.environ['INPUT_API-KEY'].strip()
    assert api_key, "Please check API-KEY"

    model = os.getenv(
        'INPUT_MODEL',              # Get model from environment
        'gemini-2.0-flash'   # use default if not provided
    )
    explanation_in = os.environ['INPUT_EXPLANATION-IN']

    b_fail_expected = ('true' == os.getenv('INPUT_FAIL-EXPECTED', 'false').lower())

    n_failed, feedback = ai_tutor.gemini_qna(
        report_files,
        student_files,
        readme_file,
        api_key,
        explanation_in,
        model=model,
    )

    print(feedback)

    # Write the feedback to the environment file
    if os.getenv('GITHUB_OUTPUT', False):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
            out_string = f'feedback<<EOF\n{feedback}\nEOF'
            logging.info(f"Writing to GITHUB_OUTPUT: {f.write(out_string)} characters")

    if not b_fail_expected:
        assert n_failed == 0, f'{n_failed} failed tests'
    elif b_fail_expected:
        assert n_failed > 0, 'No failed tests'
    else:
        raise NotImplementedError('Unexpected value for INPUT_FAIL-EXPECTED')


def get_path_tuple(report_files_str:str) -> Tuple[pathlib.Path]:
    """
    Converts a comma-separated string of file paths to a tuple of pathlib.Path objects.

    Args:
        paths_str: Comma-separated string of file paths.

    Returns:
        A tuple of pathlib.Path objects.
    """

    gen = map(
        pathlib.Path,
        report_files_str.split(',')
    )

    result_list = []

    for path in gen:
        if path.exists():
            result_list.append(path)
        else:
            logging.warning(f'{path} does not exist')

    assert result_list, 'No valid paths found'

    return tuple(result_list)


if __name__ == "__main__" :
    main()
