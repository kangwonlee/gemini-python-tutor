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


if '__main__' == __name__:
    pytest.main([__file__])
