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


@unittest.mock.patch('prompt.get_prompt')
def test_main_argument_passing__all_exists(mock_gemini_qna, caplog, tmp_path) -> None:
    # Setup

    test_key = 'test-key'
    test_explain_in = 'explain-in'
    test_model = 'test-model'

    test_gemini_key = 'test-gemini-key'
    test_grok_key = 'test-grok-key'
    test_nvidia_key = 'test-nvidia-key'

    os.environ['INPUT_GEMINI-API-KEY'] = test_gemini_key
    os.environ['INPUT_GROK-API-KEY'] = test_grok_key
    os.environ['INPUT_NVIDIA-API-KEY'] = test_nvidia_key

    os.environ['INPUT_EXPLANATION-IN'] = test_explain_in
    os.environ['INPUT_MODEL'] = test_model

    os.environ['GITHUB_OUTPUT'] = str(tmp_path / 'output.txt')

    names_input = ['file1.txt', 'file2.txt', 'file3.txt']
    names_student = ['file4.txt', 'file5.txt', 'file6.txt']

    # create mock files
    paths_input = []
    expected_input_file_paths = []
    for full_path in map(lambda x: tmp_path / x, names_input):
        full_path.write_text(f'{str(full_path.relative_to(tmp_path))} content\n')
        expected_input_file_paths.append(full_path)
        paths_input.append(str(full_path))
    os.environ['INPUT_REPORT-FILES'] = ','.join(paths_input)
    expected_input_file_paths = tuple(expected_input_file_paths)

    paths_student = []
    expected_student_file_paths = []
    for full_path in map(lambda x: tmp_path / x, names_student):
        full_path.write_text(f'{str(full_path.relative_to(tmp_path))} content\n')
        expected_student_file_paths.append(full_path)
        paths_student.append(str(full_path))
    os.environ['INPUT_STUDENT-FILES'] = ','.join(paths_student)
    expected_student_file_paths = tuple(expected_student_file_paths)

    expected_readme_path = tmp_path / 'readme.txt'
    expected_readme_path.touch()
    os.environ['INPUT_README-PATH'] = str(expected_readme_path)

    # mock return value
    mock_gemini_qna.return_value = (0, "This is the feedback message.")

    entrypoint.main()

    mock_gemini_qna.assert_called_once_with(
        expected_input_file_paths,
        expected_student_file_paths,
        expected_readme_path,
        test_key,
        test_explain_in,
        model=test_model,
    )

    assert 'does not exist' not in caplog.text
    assert 'No README file' not in caplog.text


if "__main__" == __name__:
    pytest.main([__file__])
