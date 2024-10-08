import json
import os
import pathlib
import sys

from typing import Callable, Dict, List, Tuple, Union

import pytest


test_folder = pathlib.Path(__file__).parent.resolve()
project_folder = test_folder.parent.resolve()


sys.path.insert(
    0,
    str(project_folder)
)


import ai_tutor


@pytest.fixture
def sample_report_path() -> pathlib.Path:
    return test_folder/'sample_report.json'


@pytest.fixture
def json_dict(sample_report_path) -> Dict[str, Union[str, List]]:
    with sample_report_path.open('rt') as f:
        result = json.load(f)
    return result


def test_collect_longrepr(json_dict):
    result = ai_tutor.collect_longrepr(json_dict)

    assert result


@pytest.fixture
def div_zero_report_path() -> pathlib.Path:
    return test_folder/'json_dict_div_zero_try_except.json'


@pytest.fixture
def json_dict_div_zero_try_except(div_zero_report_path:pathlib.Path) -> Dict[str, Union[str, List]]:
    with div_zero_report_path.open('rt') as f:
        result = json.load(f)
    return result


def test_collect_longrepr(json_dict_div_zero_try_except:Dict):
    result = ai_tutor.collect_longrepr(json_dict_div_zero_try_except)

    assert result


@pytest.fixture(params=('Korean', 'English', 'Bahasa Indonesia', 'Chinese', 'French', 'German', 'Italian', 'Japanese', 'Nederlands', 'Spanish', 'Thai', 'Vietnamese'))
def explanation_in(request) -> str:
    return request.param


@pytest.fixture
def homework(explanation_in:str) -> Tuple[str]:
    d = {
        'Korean': ('숙제',),
        'English': ('Homework',),
        'Bahasa Indonesia': ('tugas', 'pekerjaan rumah', 'PR'),
        'Chinese': ('作业',),
        'French': ('Devoir',),
        'German': ('Hausaufgabe',),
        'Italian': ('Compito', 'Compiti'),
        'Japanese': ('宿題',),
        'Nederlands': ('Huiswerk',),
        'Spanish': ('Tarea',),
        'Thai': ('การบ้าน',),
        'Vietnamese': ('Bài tập',),
    }    
    return tuple(
        map(
            lambda x: x.lower(),
            d[explanation_in]
        )
    )


@pytest.fixture
def msg(explanation_in:str) -> str:
    d = {
        'Korean': '메시지',
        'English': 'Message',
        'Bahasa Indonesia': 'Pesan',
        'Chinese': '消息',
        'French': 'Message',
        'German': 'Fehlermeldung',
        'Italian': 'Messaggio',
        'Japanese': 'メッセ',
        'Nederlands': 'Foutmelding', # error message
        'Spanish': 'Mensaje',
        'Thai': 'ข้อความ',
        'Vietnamese': 'thông báo', # notification
    }
    return d[explanation_in].lower()


def test_get_directive(explanation_in:str, homework:Tuple[str]):
    result = ai_tutor.get_directive(explanation_in=explanation_in)

    assert any(
        map(
            lambda x: x in result.lower(),
            homework
        )
    ), (
        f"Could not find homework: {homework} in result: {result}."
    )


def test_get_instruction(explanation_in:str, homework:Tuple[str],):
    result = ai_tutor.get_directive(explanation_in=explanation_in).lower()

    assert any(
        map(
            lambda x: x in result,
            homework
        )
    ), (
        f"Could not find homework: {homework} in result: {result}."
    )


@pytest.mark.parametrize("func", (ai_tutor.get_report_header, ai_tutor.get_report_footer))
def test_get_report__header__footer(explanation_in:str, msg:str, func:Callable):

    result = func(explanation_in=explanation_in)

    assert msg in result.lower(), f"Could not find msg: {msg} in result: {result}."


@pytest.fixture
def sample_student_code_path() -> pathlib.Path:
    return test_folder/'sample_code.py'


@pytest.fixture
def sample_readme_path() -> pathlib.Path:
    return test_folder/'sample_readme.md'


@pytest.fixture
def instruction(explanation_in:str) -> str:
    d = {
        'Korean': ('지침',),
        'English': ('Instruction',),
        'Bahasa Indonesia': ('Petunjuk', 'Instruksi'),
        'Chinese': ('说明',),
        'French': ('instruction',),
        'German': ('Aufgabenanweisung',),
        'Italian': ('istruzione',),
        'Japanese': ('指示',),
        'Nederlands': ('instructie',),
        'Spanish': ('instrucción',),
        'Thai': ('แนะนำ',),
        'Vietnamese': ('hướng dẫn',),
    }
    return tuple(
        map(
            lambda x: x.lower(),
            d[explanation_in]
        )
    )


def test_get_code_instruction(
        sample_student_code_path:pathlib.Path,
        sample_readme_path:pathlib.Path,
        explanation_in:str,
        homework:Tuple[str],
        instruction:str,
    ):

    result = ai_tutor.get_code_instruction(
        student_files = (sample_student_code_path,),
        readme_file = sample_readme_path,
        explanation_in=explanation_in
    ).lower()

    assert any(
        map(
            lambda x: x in result,
            homework
        )
    )

    assert any(
        map(
            lambda x: x in result,
            instruction
        )
    ), f"Could not find instruction: {instruction} in result: {result}."


def test_get_the_question(
        sample_report_path:pathlib.Path,
        div_zero_report_path:pathlib.Path,
        sample_student_code_path:pathlib.Path,
        sample_readme_path:pathlib.Path,
        explanation_in:str,
        homework:Tuple[str],
        msg:str,
        instruction:str,
    ):
    result = ai_tutor.get_the_question(
        report_paths=(sample_report_path,div_zero_report_path),
        student_files=(sample_student_code_path,),
        readme_file=sample_readme_path,
        explanation_in=explanation_in,
    ).lower()

    assert any(
        map(
            lambda x: x in result,
            homework
        )
    )
    assert msg in result

    assert any(
        map(
            lambda x: x in result,
            instruction
        )
    ), f"Could not find instruction: {instruction} in result: {result}."


if '__main__' == __name__:
    pytest.main([__file__])
