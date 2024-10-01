#!/usr/bin/env -S python3 -B

# NOTE: If you are using an alpine docker image
# such as pyaction-lite, the -S option above won't
# work. The above line works fine on other linux distributions
# such as debian, etc, so the above line will work fine
# if you use pyaction:4.0.0 or higher as your base docker image.

import logging
import os
import pathlib
import sys

from typing import Tuple


sys.path.insert(0, pathlib.Path(__file__).parent.resolve())


import ai_tutor


logging.basicConfig(level=logging.INFO)


def main() -> None:
    # Check if the API key is available
    ai_tutor.test_API_key()

    report_files_str = os.getenv('INPUT_REPORT-FILES')
    report_files = get_path_tuple(report_files_str)

    student_files_str = os.getenv('INPUT_STUDENT-FILES')
    student_files = get_path_tuple(student_files_str)

    readme_file_str = os.getenv('INPUT_README-PATH')
    readme_file = pathlib.Path(readme_file_str)
    assert readme_file.exists(), 'No README file'

    feedback = ai_tutor.gemini_qna(report_files, student_files, readme_file)

    print(f'::set-output name=feedback::{feedback}')


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
