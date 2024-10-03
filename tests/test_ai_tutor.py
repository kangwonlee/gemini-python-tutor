import json
import os
import pathlib
import sys

from typing import Dict, Union, List

import pytest


test_folder = pathlib.Path(__file__).parent.resolve()
project_folder = test_folder.parent.resolve()


sys.path.insert(
    0,
    str(project_folder)
)


import ai_tutor


@pytest.fixture
def json_dict() -> Dict[str, Union[str, List]]:
    with open(test_folder/'sample_report.json', 'r') as f:
        result = json.load(f)
    return result


def test_collect_longrepr(json_dict):
    result = ai_tutor.collect_longrepr(json_dict)

    assert result


@pytest.fixture
def json_dict_div_zero_try_except() -> Dict[str, Union[str, List]]:
    with open(test_folder/'json_dict_div_zero_try_except.json', 'r') as f:
        result = json.load(f)
    return result


def test_collect_longrepr(json_dict_div_zero_try_except:Dict):
    result = ai_tutor.collect_longrepr(json_dict_div_zero_try_except)

    assert result


@pytest.fixture(params=('Korean', 'English', 'Japanese', 'Chinese', 'Spanish', 'French', 'German', 'Thai'))
def human_language(request) -> str:
    return request.param.capitalize()


@pytest.fixture
def homework(human_language:str) -> str:
    d = {
        'Korean': '숙제',
        'English': 'Homework',
        'Japanese': '宿題',
        'Chinese': '作业',
        'Spanish': 'Tarea',
        'French': 'Devoir',
        'German': 'Hausaufgabe',
        'Thai': 'การบ้าน',
    }    
    return d[human_language].lower()


@pytest.fixture
def msg(human_language:str) -> str:
    d = {
        'Korean': '메시지',
        'English': 'Message',
        'Japanese': 'メッセ',
        'Chinese': '消息',
        'Spanish': 'Mensaje',
        'French': 'Message',
        'German': 'Fehlermeldung',
        'Thai': 'ข้อความ',
    }
    return d[human_language].lower()


def test_get_instruction(human_language, homework,):
    result = ai_tutor.get_directive(human_language=human_language)

    assert homework in result.lower()


@pytest.mark.parametrize("func", (ai_tutor.get_question_header, ai_tutor.get_question_footer))
def test_get_question_header_footer(human_language, msg, func):

    result = func(human_language=human_language)

    assert msg in result.lower()


if '__main__' == __name__:
    pytest.main([__file__])
