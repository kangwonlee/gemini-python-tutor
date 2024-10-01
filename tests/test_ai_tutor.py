import pathlib
import sys
from typing import Dict, Union, List


import pytest


sys.path.insert(
    0,
    str(pathlib.Path(__file__).parent.parent.resolve())
)


import ai_tutor


@pytest.fixture
def json_dict():
    return {"created": ";D ;) ;P 8) :)", "duration": ";D :) ;P 8) ;)", "exitcode": ";D ;) :) ;P 8)", "root": ";P 8) :) ;D ;)", "environment": {}, "summary": {"error": ";) ;D :) 8) ;P", "passed": ";) :) ;P 8) ;D", "total": ";P :) 8) ;D ;)", "collected": "8) ;D :) ;P ;)"}, "tests": [{"nodeid": ":) ;D 8) ;) ;P", "lineno": ";) :) ;D 8) ;P", "outcome": ";) ;P ;D 8) :)", "keywords": ["test_required_variables", "test_results.py", "tests", "wk03_string_interpolation-???", ""], "setup": {"duration": ":) 8) ;P ;) ;D", "outcome": ":) ;D 8) ;P ;)", "crash": {"path": ":) ;P 8) ;) ;D", "lineno": ";P 8) ;D :) ;)", "message": "8) ;) ;P ;D :)"}, "traceback": [{"path": ";P ;) ;D 8) :)", "lineno": "8) :) ;D ;) ;P", "message": ";) 8) ;D :) ;P"}], "longrepr": ";P ;D ;) 8) :)"}, "teardown": {"duration": "8) :) ;P ;) ;D", "outcome": "8) :) ;D ;) ;P", "longrepr": ":) ;D 8) ;) ;P"}}, {"nodeid": "8) ;P ;D ;) :)", "lineno": ":) ;D 8) ;P ;)", "outcome": ";D ;) 8) ;P :)", "keywords": ["test_result_storage", "test_results.py", "tests", "wk03_string_interpolation-???", ""], "setup": {"duration": ";) :) ;D ;P 8)", "outcome": ":) ;D 8) ;P ;)", "crash": {"path": ";) ;P 8) ;D :)", "lineno": "8) ;) ;D ;P :)", "message": ";P 8) ;) ;D :)"}, "traceback": [{"path": ";D :) ;) ;P 8)", "lineno": ";D ;) ;P 8) :)", "message": ";D ;P ;) :) 8)"}], "longrepr": ";D ;P :) 8) ;)"}, "teardown": {"duration": "8) ;P :) ;D ;)", "outcome": ";P ;D 8) :) ;)", "longrepr": ";) :) ;D ;P 8)"}}, {"nodeid": ";P ;D 8) :) ;)", "lineno": ";D 8) :) ;) ;P", "outcome": ":) 8) ;D ;P ;)", "keywords": ["test_first_two_assignments_are_integers", "test_results.py", "tests", "wk03_string_interpolation-???", ""], "setup": {"duration": ";P :) ;) 8) ;D", "outcome": ";D ;) 8) :) ;P", "crash": {"path": ";D 8) ;P :) ;)", "lineno": ";D 8) ;P :) ;)", "message": ";P 8) ;D ;) :)"}, "traceback": [{"path": ";) :) ;D ;P 8)", "lineno": ":) ;) ;D ;P 8)", "message": "8) :) ;) ;D ;P"}], "longrepr": ";D 8) ;P :) ;)"}, "teardown": {"duration": "8) ;) ;P ;D :)", "outcome": "8) ;D :) ;P ;)", "longrepr": ";P :) ;) ;D 8)"}}, {"nodeid": "8) ;) ;P :) ;D", "lineno": ":) ;D ;) 8) ;P", "outcome": ";P ;) ;D :) 8)", "keywords": ["test_string_formatting_with_mod", "test_results.py", "tests", "wk03_string_interpolation-???", ""], "setup": {"duration": ":) ;) ;D ;P 8)", "outcome": "8) :) ;D ;P ;)", "crash": {"path": "8) ;D :) ;) ;P", "lineno": "8) ;D ;P :) ;)", "message": ";D ;) 8) :) ;P"}, "traceback": [{"path": ";) :) 8) ;D ;P", "lineno": ";D ;) 8) ;P :)", "message": ":) ;) ;D ;P 8)"}], "longrepr": ";) 8) :) ;D ;P"}, "teardown": {"duration": ";D 8) ;P ;) :)", "outcome": ";D 8) :) ;P ;)", "longrepr": ";) ;P :) 8) ;D"}}, {"nodeid": ":) ;P ;D 8) ;)", "lineno": ";P ;) ;D 8) :)", "outcome": "8) :) ;) ;P ;D", "keywords": ["test_output_format[-]", "-", "test_results.py", "tests", "wk03_string_interpolation-???", ""], "setup": {"duration": "8) :) ;D ;) ;P", "outcome": "8) ;P ;) ;D :)", "longrepr": "8) ;D :) ;) ;P"}, "call": {"duration": ";) :) ;P 8) ;D", "outcome": ";) ;P 8) :) ;D", "longrepr": ";) 8) :) ;D ;P"}, "teardown": {"duration": ";) 8) ;P :) ;D", "outcome": "8) :) ;) ;D ;P", "longrepr": ";D 8) :) ;) ;P"}}, {"nodeid": ";D :) 8) ;) ;P", "lineno": ";D ;) 8) ;P :)", "outcome": "8) ;P :) ;) ;D", "keywords": ["test_output_format[+]", "+", "test_results.py", "tests", "wk03_string_interpolation-???", ""], "setup": {"duration": ":) ;) ;D 8) ;P", "outcome": ";P 8) ;D :) ;)", "longrepr": "8) :) ;D ;) ;P"}, "call": {"duration": "8) ;D ;) ;P :)", "outcome": ";) ;D :) ;P 8)", "longrepr": ";P :) 8) ;D ;)"}, "teardown": {"duration": "8) :) ;P ;) ;D", "outcome": "8) ;D ;) :) ;P", "longrepr": "8) ;P :) ;) ;D"}}, {"nodeid": "8) ;D ;) ;P :)", "lineno": ":) 8) ;) ;D ;P", "outcome": ";P ;D :) ;) 8)", "keywords": ["test_output_format[*]", "*", "test_results.py", "tests", "wk03_string_interpolation-???", ""], "setup": {"duration": ";P ;) :) 8) ;D", "outcome": ":) ;D 8) ;P ;)", "longrepr": ";) ;P :) 8) ;D"}, "call": {"duration": "8) ;D ;) :) ;P", "outcome": ";) :) ;P ;D 8)", "longrepr": ";P ;D :) ;) 8)"}, "teardown": {"duration": ";P :) ;) ;D 8)", "outcome": ";P ;D ;) 8) :)", "longrepr": ";D :) ;P 8) ;)"}}, {"nodeid": "8) ;D ;P ;) :)", "lineno": "8) ;D ;) ;P :)", "outcome": ";) 8) ;D :) ;P", "keywords": ["test_output_format[/]", "/", "test_results.py", "tests", "wk03_string_interpolation-???", ""], "setup": {"duration": ";D ;P :) ;) 8)", "outcome": ";D ;P :) ;) 8)", "longrepr": ";) 8) ;D ;P :)"}, "call": {"duration": ";) ;D 8) ;P :)", "outcome": "8) ;) ;D ;P :)", "longrepr": ";) ;P 8) ;D :)"}, "teardown": {"duration": "8) ;D :) ;P ;)", "outcome": ";P 8) ;) ;D :)", "longrepr": "8) ;P ;D :) ;)"}}, {"nodeid": ":) ;) 8) ;D ;P", "lineno": ":) ;P 8) ;) ;D", "outcome": ";) 8) ;P :) ;D", "keywords": ["test_output[+]", "+", "test_results.py", "tests", "wk03_string_interpolation-???", ""], "setup": {"duration": "8) ;D ;) :) ;P", "outcome": ";D ;) 8) :) ;P", "longrepr": ":) ;) ;P 8) ;D"}, "call": {"duration": ";) ;D ;P 8) :)", "outcome": "8) ;) :) ;D ;P", "longrepr": ";P ;D 8) ;) :)"}, "teardown": {"duration": ":) 8) ;P ;) ;D", "outcome": "8) ;D :) ;P ;)", "longrepr": ";) ;P ;D :) 8)"}}, {"nodeid": ";) 8) :) ;P ;D", "lineno": "8) ;P :) ;D ;)", "outcome": ";P ;D :) 8) ;)", "keywords": ["test_output[-]", "-", "test_results.py", "tests", "wk03_string_interpolation-???", ""], "setup": {"duration": ";D 8) :) ;) ;P", "outcome": ";P ;D 8) ;) :)", "longrepr": ";D ;P 8) ;) :)"}, "call": {"duration": ";) ;P 8) ;D :)", "outcome": ";) ;P ;D 8) :)", "longrepr": "8) ;D ;P ;) :)"}, "teardown": {"duration": ";P :) 8) ;D ;)", "outcome": ";P 8) :) ;) ;D", "longrepr": ";) ;D 8) ;P :)"}}, {"nodeid": ";) :) ;D 8) ;P", "lineno": "8) ;) :) ;P ;D", "outcome": "8) ;) ;P ;D :)", "keywords": ["test_output[*]", "*", "test_results.py", "tests", "wk03_string_interpolation-???", ""], "setup": {"duration": ";D ;P :) ;) 8)", "outcome": "8) :) ;D ;) ;P", "longrepr": ";D 8) ;) ;P :)"}, "call": {"duration": ":) ;D ;) 8) ;P", "outcome": ":) ;P ;) ;D 8)", "longrepr": ":) ;) ;D 8) ;P"}, "teardown": {"duration": ";D ;) ;P :) 8)", "outcome": "8) ;D ;P ;) :)", "longrepr": ";) ;D 8) :) ;P"}}, {"nodeid": ";) ;P 8) ;D :)", "lineno": ";) ;P ;D 8) :)", "outcome": ";P 8) ;) ;D :)", "keywords": ["test_output[/]", "/", "test_results.py", "tests", "wk03_string_interpolation-???", ""], "setup": {"duration": ";D :) ;) 8) ;P", "outcome": ";) ;D 8) :) ;P", "longrepr": "8) ;P ;) :) ;D"}, "call": {"duration": "8) ;) ;P ;D :)", "outcome": ":) ;) 8) ;P ;D", "longrepr": "8) ;) ;D :) ;P"}, "teardown": {"duration": ";P 8) ;) ;D :)", "outcome": ":) ;) ;D 8) ;P", "longrepr": ";D 8) ;) ;P :)"}}]}


def test_collect_longrepr(json_dict):
    result = ai_tutor.collect_longrepr(json_dict)

    assert result


@pytest.fixture
def json_dict_div_zero_try_except() -> Dict[str, Union[str, List]]:
    return (
        {
            "created": "REDACTED",
            "duration": "REDACTED",
            "exitcode": 1,
            "root": "REDACTED",
            "environment": {},
            "summary": {
                "passed": 0,
                "failed": 1,
                "total": 1,
                "collected": 1
            },
            "tests": [
                {
                    "nodeid": "tests_folder/test_file_name.py::test_function_name",
                    "lineno": 51,
                    "outcome": "failed",
                    "keywords": [
                        "test_function_name",
                        "test_file_name.py",
                        "tests",
                        "repo-name",
                        ""
                    ],
                    "setup": {
                        "duration": "REDACTED",
                        "outcome": "passed",
                        "longrepr": "REDACTED"
                    },
                    "call": {
                        "duration": "REDACTED",
                        "outcome": "failed",
                        "crash": {
                            "path": "REDACTED",
                            "lineno": 66,
                            "message": "Failed: 0으로 나누려고 하면 'Cannot divide by zero'라는 문자열을 대신 반환 바랍니다."
                        },
                        "traceback": [
                            {
                                "path": "tests/test_file_name.py",
                                "lineno": 66,
                                "message": "Failed"
                            }
                        ],
                        "longrepr": (
                            "[gw1] linux -- Python 3.10.12 /path/repo-name/repo-name/test-env/bin/python\n"
                            "\n"
                            "    def test_function_name():\n"
                            "        \"\"\"Tests the div function with various inputs, including division by zero.\"\"\"\n"
                            "        assert exercise.div(10, 2) == 5\n"
                            "        assert exercise.div(20, 5) == 4\n"
                            "        assert exercise.div(-10, 2) == -5\n"
                            "        assert exercise.div(10, -2) == -5\n"
                            "        assert exercise.div(0, 5) == 0\n"
                            "        # Test division by zero\n"
                            "    \n"
                            "        msg = \"0으로 나누려고 하면 'Cannot divide by zero'라는 문자열을 대신 반환 바랍니다.\"\n"
                            "    \n"
                            "        try:\n"
                            ">           assert exercise.div(5, 0) == 'Cannot divide by zero', msg\n"
                            "\n"
                            "tests/test_file_name.py:64: \n"
                            "_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ \n"
                            "\n"
                            "a = 5, b = 0\n"
                            "\n"
                            "    def div(a, b):\n"
                            "        # TODO:\n"
                            "        # write code dividing two numbers\n"
                            "        # 두 숫자를 나누는 코드를 작성하세요.\n"
                            "        # return the result.\n"
                            "        # 결과값을 return하세요.\n"
                            "        # if divide by zero, please return string `'Cannot divide by zero'` instead.\n"
                            "        # 0으로 나누는 경우 `'Cannot divide by zero'` 라는 문자열을 반환합니다.\n"
                            ">       return a / b\n"
                            "E       ZeroDivisionError: division by zero\n"
                            "\n"
                            "exercise.py:33: ZeroDivisionError\n"
                            "\n"
                            "During handling of the above exception, another exception occurred:\n"
                            "\n"
                            "    def test_function_name():\n"
                            "        \"\"\"Tests the div function with various inputs, including division by zero.\"\"\"\n"
                            "        assert exercise.div(10, 2) == 5\n"
                            "        assert exercise.div(20, 5) == 4\n"
                            "        assert exercise.div(-10, 2) == -5\n"
                            "        assert exercise.div(10, -2) == -5\n"
                            "        assert exercise.div(0, 5) == 0\n"
                            "        # Test division by zero\n"
                            "    \n"
                            "        msg = \"0으로 나누려고 하면 'Cannot divide by zero'라는 문자열을 대신 반환 바랍니다.\"\n"
                            "    \n"
                            "        try:\n"
                            "            assert exercise.div(5, 0) == 'Cannot divide by zero', msg\n"
                            "        except ZeroDivisionError:\n"
                            ">           pytest.fail(msg)\n"
                            "E           Failed: 0으로 나누려고 하면 'Cannot divide by zero'라는 문자열을 대신 반환 바랍니다.\n"
                            "\n"
                            "tests/test_file_name.py:66: Failed"
                        )
                    },
                    "teardown": {
                        "duration": "REDACTED",
                        "outcome": "passed",
                        "longrepr": "REDACTED"
                    }
                }
            ]
        }
    )


def test_collect_longrepr(json_dict_div_zero_try_except:Dict):
    result = ai_tutor.collect_longrepr(json_dict_div_zero_try_except)

    assert result


if '__main__' == __name__:
    pytest.main([__file__])
