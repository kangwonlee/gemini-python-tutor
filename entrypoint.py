#!/usr/bin/env -S python3 -B

# NOTE: If you are using an alpine docker image
# such as pyaction-lite, the -S option above won't
# work. The above line works fine on other linux distributions
# such as debian, etc, so the above line will work fine
# if you use pyaction:4.0.0 or higher as your base docker image.


import os
import pathlib
import sys

from typing import Tuple


import ai_tutor


def main():
    report_files_str = os.getenv('INPUT_REPORT-FILES')
    report_files = get_path_tuple(report_files_str)

    student_files_str = os.getenv('INPUT_STUDENT-FILES')
    student_files = get_path_tuple(student_files_str)

    readme_file_str = os.getenv('INPUT_README-PATH')
    readme_file = pathlib.Path(readme_file_str)

    feedback = ai_tutor.gemini_qna(report_files, student_files, readme_file)

    print(f'::set-output name=feedback::{feedback}')


def get_path_tuple(report_files_str:str) -> Tuple[pathlib.Path]:
    return tuple(
        map(
            pathlib.Path,
            report_files_str.split(',')
        )
    )


if __name__ == "__main__" :
    main()
