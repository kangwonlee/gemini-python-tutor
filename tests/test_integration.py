import os
import pathlib
import sys
import unittest.mock

import pytest


sys.path.insert(
    0,
    str(pathlib.Path(__file__).parent.parent.resolve())
)


import entrypoint


@unittest.mock.patch('ai_tutor.gemini_qna')
def test_main_argument_passing__all_exists(mock_gemini_qna, caplog, tmp_path) -> None:
    # Setup
    os.environ['INPUT_API-KEY'] = 'test_key'
    os.environ['INPUT_EXPLANATION-IN'] = 'Korean'
    os.environ['INPUT_MODEL'] = 'gemini-2.0-flash-exp'

    os.environ['GITHUB_OUTPUT'] = str(tmp_path / 'output.txt')

    names_input = ['file1.txt', 'file2.txt', 'file3.txt']
    names_student = ['file4.txt', 'file5.txt', 'file6.txt']

    # create mock files
    paths_input = []
    for f in map(lambda x: tmp_path / x, names_input):
        (tmp_path / f).write_text('comment')
        paths_input.append(str(f))
    os.environ['INPUT_REPORT-FILES'] = ','.join(paths_input)

    paths_student = []
    for f in map(lambda x: tmp_path / x, names_student):
        (tmp_path / f).write_text('comment')
        paths_student.append(str(f))
    os.environ['INPUT_STUDENT-FILES'] = ','.join(paths_student)

    path_readme = tmp_path / 'readme.txt'
    path_readme.touch()
    os.environ['INPUT_README-PATH'] = str(path_readme)

    # mock return value
    mock_gemini_qna.return_value = (0, "This is the feedback message.")

    entrypoint.main()

    mock_gemini_qna.assert_called_once_with(
        (tmp_path / 'file1.txt', tmp_path / 'file2.txt', tmp_path / 'file3.txt'),
        (tmp_path / 'file4.txt', tmp_path / 'file5.txt', tmp_path / 'file6.txt'),
        tmp_path / 'readme.txt',
        'test_key',
        'Korean',
         model='gemini-2.0-flash-exp',
    )

    assert 'does not exist' not in caplog.text
    assert 'No README file' not in caplog.text


if "__main__" == __name__:
    pytest.main([__file__])
