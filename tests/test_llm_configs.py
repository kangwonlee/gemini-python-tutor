# begin tests/test_llm_configs.py
import pathlib
import sys

from typing import Dict


HEADER = Dict[str, str]


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
def sample_header() -> HEADER:
    return {"Test-Type": "test/test"}


@pytest.fixture
def llm_config_instance(
        sample_api_key:str,
        sample_url:str,
        sample_model:str,
        sample_header:HEADER,
    ) -> llm_configs.LLMConfig:
    return llm_configs.LLMConfig(
        sample_api_key,
        sample_url,
        sample_model,
        sample_header,
    )


@pytest.fixture
def llm_config__default_header(
        sample_api_key:str,
        sample_url:str,
        sample_model:str,
    ) -> llm_configs.LLMConfig:
    return llm_configs.LLMConfig(
        sample_api_key,
        sample_url,
        sample_model,
    )


@pytest.fixture
def gemini_config(sample_api_key: str) -> llm_configs.GeminiConfig:
    return llm_configs.GeminiConfig(api_key=sample_api_key)


@pytest.fixture
def grok_config(sample_api_key: str) -> llm_configs.GrokConfig:
    return llm_configs.GrokConfig(api_key=sample_api_key)


@pytest.fixture
def nvidia_nim_config(sample_api_key: str) -> llm_configs.NvidiaNIMConfig:
    return llm_configs.NvidiaNIMConfig(api_key=sample_api_key)


def test_config_instance(
        llm_config_instance:llm_configs.LLMConfig,
        sample_api_key:str,
        sample_model:str,
        sample_url:str,
        sample_header:HEADER,
    ):
    assert llm_config_instance.api_key == sample_api_key
    assert llm_config_instance.api_url == sample_url
    assert llm_config_instance.model == sample_model
    assert llm_config_instance.default_headers == sample_header


def test_config__default_header(
        llm_config__default_header:llm_configs.LLMConfig,
        sample_api_key:str,
        sample_url:str,
        sample_model:str,):
    assert llm_config__default_header.api_key == sample_api_key
    assert llm_config__default_header.api_url == sample_url
    assert llm_config__default_header.model == sample_model
    assert isinstance(llm_config__default_header.default_headers, dict)


if '__main__' == __name__:
    pytest.main(['--verbose', __file__])
# end tests/test_llm_configs.py
