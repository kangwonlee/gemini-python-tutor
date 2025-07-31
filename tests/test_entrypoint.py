import logging
import os
import pathlib
import sys

from typing import Tuple


import pytest


sys.path.insert(
    0,
    str(pathlib.Path(__file__).parent.parent.resolve())
)


import entrypoint
import llm_configs


PATH_TUPLE = Tuple[pathlib.Path]
PATH_TUPLE_STR = Tuple[PATH_TUPLE, str]


@pytest.fixture
def path_tuple(tmp_path) -> PATH_TUPLE_STR:
    s = [
        tmp_path / 'file1.txt',
        tmp_path / 'file2.txt',
        tmp_path / 'file3.txt',
    ]

    t = f'{s[0]},{s[1]},{s[2]}'

    return s, t


def test_get_path_tuple__normal(path_tuple:PATH_TUPLE_STR) -> None:
    # Setup
    s, t = path_tuple
    s[0].write_text('file1')
    s[1].write_text('file2')
    s[2].write_text('file3')

    # When
    result = entrypoint.get_path_tuple(t)

    # Then
    assert len(result) == len(s)
    assert all(map(lambda x_y: x_y[0] == x_y[1], zip(result, s)))


def test_get_path_tuple__one_missing(path_tuple:PATH_TUPLE_STR, caplog) -> None:
    # Setup
    caplog.set_level(logging.WARNING)
    s, t = path_tuple
    s[0].write_text('file1')
    s[1].write_text('file2')

    if s[2].exists():
        s[2].unlink()

    # function under test
    result = entrypoint.get_path_tuple(t)

    # Then
    assert result == (s[0], s[1])
    assert 'file3.txt does not exist' in caplog.text


def test_get_path_tuple__all_missing(path_tuple:PATH_TUPLE_STR, caplog) -> None:
    # Setup
    s, t = path_tuple
    for path in s:
        if path.exists():
            path.unlink()

    # Then
    with pytest.raises(ValueError) as e:
        _ = entrypoint.get_path_tuple(t)

    assert 'No valid paths provided' in str(e.value)


def helper_model_envkey_expectedkey() -> Tuple[Tuple[str, str, str]]:
    return (
        ("claude", "INPUT_CLAUDE_API_KEY", "claude_key"),
        ("gemini", "INPUT_GEMINI-API-KEY", "gemini_key"),
        ("grok", "INPUT_GROK-API-KEY", "grok_key"),
        ("nvidia_nim", "INPUT_NVIDIA-API-KEY", "nvidia_key"),
        ("perplexity", "INPUT_PERPLEXITY-API-KEY", "perplexity_key"),
    )


@pytest.fixture
def mock_env_api_keys(monkeypatch):
    """Fixture to mock environment variables for testing."""
    for _, env_key, expected_key in helper_model_envkey_expectedkey():
        monkeypatch.setenv(env_key, expected_key)


@pytest.mark.parametrize("model, env_key, expected_key", helper_model_envkey_expectedkey())
def test_get_model_key_from_env(monkeypatch, mock_env_api_keys, model, env_key, expected_key):
    """Test get_model_key_from_env with valid model and API key."""
    monkeypatch.setenv("INPUT_MODEL", model)
    result_model, result_key = entrypoint.get_model_key_from_env()
    assert result_model == model
    assert result_key == expected_key


def test_get_model_key_from_env_invalid_model(monkeypatch, mock_env_api_keys):
    """Test get_model_key_from_env with invalid model."""
    monkeypatch.setenv("INPUT_MODEL", "invalid_model")
    with pytest.raises(AssertionError):
        entrypoint.get_model_key_from_env()


def test_get_model_key_from_env_missing_key(monkeypatch):
    """Test get_model_key_from_env with missing API key."""
    monkeypatch.setenv("INPUT_MODEL", "claude")
    with pytest.raises(AssertionError, match="No API key provided for claude"):
        entrypoint.get_model_key_from_env()


@pytest.mark.parametrize("model, expected_class", [
    ("claude", llm_configs.ClaudeConfig),
    ("gemini", llm_configs.GeminiConfig),
    ("grok", llm_configs.GrokConfig),
    ("nvidia_nim", llm_configs.NvidiaNIMConfig),
    ("perplexity", llm_configs.PerplexityConfig),
])
def test_get_config_class(model, expected_class):
    """Test get_config_class returns correct configuration class."""
    assert entrypoint.get_config_class(model) == expected_class


def test_get_config_class_invalid_model():
    """Test get_config_class with invalid model."""
    with pytest.raises(ValueError, match="Unsupported LLM type: invalid_model"):
        entrypoint.get_config_class("invalid_model")


if __name__ == '__main__':
    pytest.main([__file__])
