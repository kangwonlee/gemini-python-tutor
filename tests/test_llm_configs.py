# begin tests/test_llm_configs.py
import pathlib
import sys

import pytest

test_folder = pathlib.Path(__file__).parent.resolve()
project_folder = test_folder.parent.resolve()
sys.path.insert(
    0,
    str(project_folder)
)


import llm_configs


@pytest.fixture
def sample_api_key() -> str:
    return 'test_key'


@pytest.fixture
def sample_url() -> str:
    return 'test_url'


@pytest.fixture
def sample_model() -> str:
    return 'test_model'


@pytest.fixture
def llm_config_instance(sample_api_key:str, sample_url:str, sample_model:str) -> llm_configs.LLMConfig:
    return llm_configs.LLMConfig(sample_api_key, sample_url, sample_model)


def test_config_instance(
        llm_config_instance:llm_configs.LLMConfig,
        sample_api_key:str,
        sample_model:str,
        sample_url:str):
    assert llm_config_instance.api_key == sample_api_key
    assert llm_config_instance.api_url == sample_url
    assert llm_config_instance.model == sample_model


if '__main__' == __name__:
    pytest.main(['--verbose', __file__])
# end tests/test_llm_configs.py
