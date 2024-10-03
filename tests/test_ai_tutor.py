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


@pytest.fixture(
    params=(
        ('Korean', '숙제'),
        ('English', 'Homework'),
        ('Japanese', '宿題'),
        ('Chinese', '作业'),
        ('Spanish', 'Tarea'),
        ('French', 'Devoir'),
        ('German', 'Hausaufgabe'),
       ('Thai', 'การบ้าน'),
    )
)
def int_homework(request):
    return request.param[0].capitalize(), request.param[1].lower()


def test_get_instruction(int_homework):
    human_language, signature = int_homework
    result = ai_tutor.get_instruction(human_language=human_language)

    assert signature in result.lower()


@pytest.fixture(
    params=(
        ('Korean', '메시지'),
        ('English', 'Message'),
        ('Japanese', 'メッセ'),
        ('Chinese', '消息'),
        ('Spanish', 'Mensaje'),
        ('French', 'Message'),
        ('German', 'Fehlermeldung'),
       ('Thai', 'ข้อความ'),
    )
)
def int_msg(request):
    return request.param[0].capitalize(), request.param[1].lower()


@pytest.mark.parametrize("func", (ai_tutor.get_question_header, ai_tutor.get_question_footer))
def test_get_question_header_footer(int_msg, func):
    human_language, signature = int_msg

    result = func(human_language=human_language)

    assert signature in result.lower()


if '__main__' == __name__:
    pytest.main([__file__])
