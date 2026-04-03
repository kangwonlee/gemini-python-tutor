# begin tests/test_entrypoint.py

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
    s, t = path_tuple
    s[0].write_text('file1')
    s[1].write_text('file2')
    s[2].write_text('file3')
    result = entrypoint.get_path_tuple(t)
    assert len(result) == len(s)
    assert all(map(lambda x_y: x_y[0] == x_y[1], zip(result, s)))


def test_get_path_tuple__one_missing(path_tuple:PATH_TUPLE_STR, caplog) -> None:
    caplog.set_level(logging.WARNING)
    s, t = path_tuple
    s[0].write_text('file1')
    s[1].write_text('file2')
    if s[2].exists():
        s[2].unlink()
    result = entrypoint.get_path_tuple(t)
    assert result == (s[0], s[1])
    assert 'file3.txt does not exist' in caplog.text


def test_get_path_tuple__all_missing(path_tuple:PATH_TUPLE_STR, caplog) -> None:
    s, t = path_tuple
    for path in s:
        if path.exists():
            path.unlink()
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


@pytest.mark.parametrize("model, env_key, expected_key", helper_model_envkey_expectedkey())
def test_get_model_key_from_env__valid_specified(monkeypatch, model, env_key, expected_key):
    """Test with specified model and its key available (multiple keys present)."""
    # Set multiple keys including the specified one
    monkeypatch.setenv("INPUT_CLAUDE_API_KEY", "claude_key")
    monkeypatch.setenv("INPUT_GEMINI-API-KEY", "gemini_key")
    monkeypatch.setenv(env_key, expected_key)
    monkeypatch.setenv("INPUT_MODEL", model)
    result_model, result_key = entrypoint.get_model_key_from_env()
    assert result_model == model
    assert result_key == expected_key


@pytest.mark.parametrize("model, env_key, expected_key", helper_model_envkey_expectedkey())
def test_get_model_key_from_env__single_key(monkeypatch, model, env_key, expected_key):
    """Test with only one key available (uses it regardless of INPUT_MODEL)."""
    monkeypatch.setenv(env_key, expected_key)
    result_model, result_key = entrypoint.get_model_key_from_env()
    assert result_model == model
    assert result_key == expected_key


def test_get_model_key_from_env__no_keys(monkeypatch):
    """Test with no API keys available."""
    with pytest.raises(ValueError, match="No API keys provided. Set at least one of"):
        entrypoint.get_model_key_from_env()


def test_get_model_key_from_env__fallback_gemini(monkeypatch):
    """Test fallback to Gemini when specified model unavailable but Gemini available."""
    monkeypatch.setenv("INPUT_MODEL", "invalid")
    monkeypatch.setenv("INPUT_GEMINI-API-KEY", "gemini_key")
    monkeypatch.setenv("INPUT_GROK-API-KEY", "grok_key")  # Multiple, but fallback to Gemini
    result_model, result_key = entrypoint.get_model_key_from_env()
    assert result_model == "gemini-2.5-flash"
    assert result_key == "gemini_key"


def test_get_model_key_from_env__no_model_fallback_gemini(monkeypatch):
    """Test no INPUT_MODEL set, fallback to Gemini if available."""
    monkeypatch.setenv("INPUT_CLAUDE_API_KEY", "claude_key")
    monkeypatch.setenv("INPUT_GEMINI-API-KEY", "gemini_key")
    result_model, result_key = entrypoint.get_model_key_from_env()
    assert result_model == "gemini-2.5-flash"
    assert result_key == "gemini_key"


def test_get_model_key_from_env__invalid_model_no_gemini(monkeypatch):
    """Test invalid specified model, no Gemini available."""
    monkeypatch.setenv("INPUT_MODEL", "invalid")
    monkeypatch.setenv("INPUT_CLAUDE_API_KEY", "claude_key")
    result_model, result_key = entrypoint.get_model_key_from_env()
    assert result_key == "claude_key"
    assert result_model == "claude"


def test_get_model_key_from_env__empty_key_ignored(monkeypatch):
    """Test empty/whitespace keys are ignored (treated as unavailable)."""
    monkeypatch.setenv("INPUT_CLAUDE_API_KEY", "   ")  # Empty after strip
    monkeypatch.setenv("INPUT_GEMINI-API-KEY", "gemini_key")
    result_model, result_key = entrypoint.get_model_key_from_env()
    assert result_model == "gemini"
    assert result_key == "gemini_key"


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


def test_get_model_key_from_env_with_api_key(monkeypatch):
    """Test that INPUT_API-KEY is used when provided with a model."""
    monkeypatch.setenv("INPUT_API-KEY", "test-api-key")
    monkeypatch.setenv("INPUT_MODEL", "gemini")
    model, api_key = entrypoint.get_model_key_from_env()
    assert model == "gemini"
    assert api_key == "test-api-key"


class TestExtractTokenUsage:
    """Tests for extract_token_usage multi-provider support."""

    def test_gemini_format(self):
        raw = {
            "usageMetadata": {
                "promptTokenCount": 150,
                "candidatesTokenCount": 200,
                "totalTokenCount": 350,
            }
        }
        result = entrypoint.extract_token_usage(raw)
        assert result["input_tokens"] == 150
        assert result["output_tokens"] == 200
        assert result["total_tokens"] == 350

    def test_claude_format(self):
        raw = {
            "usage": {
                "input_tokens": 100,
                "output_tokens": 250,
            }
        }
        result = entrypoint.extract_token_usage(raw)
        assert result["input_tokens"] == 100
        assert result["output_tokens"] == 250
        assert result["total_tokens"] == 350  # computed

    def test_openai_format(self):
        raw = {
            "usage": {
                "prompt_tokens": 80,
                "completion_tokens": 120,
                "total_tokens": 200,
            }
        }
        result = entrypoint.extract_token_usage(raw)
        assert result["input_tokens"] == 80
        assert result["output_tokens"] == 120
        assert result["total_tokens"] == 200

    def test_none_response(self):
        result = entrypoint.extract_token_usage(None)
        assert result["input_tokens"] is None
        assert result["output_tokens"] is None

    def test_empty_dict(self):
        result = entrypoint.extract_token_usage({})
        assert result["input_tokens"] is None

    def test_missing_usage(self):
        raw = {"id": "123", "choices": []}
        result = entrypoint.extract_token_usage(raw)
        assert result["input_tokens"] is None


class TestWriteTokenUsage:
    """Tests for write_token_usage file output."""

    def test_writes_json(self, tmp_path):
        class MockClient:
            last_raw_response = {
                "usageMetadata": {
                    "promptTokenCount": 50,
                    "candidatesTokenCount": 100,
                    "totalTokenCount": 150,
                }
            }
        entrypoint.write_token_usage(MockClient(), "gemini-2.5-flash", tmp_path)
        usage_file = tmp_path / "token_usage.json"
        assert usage_file.exists()
        import json
        data = json.loads(usage_file.read_text())
        assert data["model"] == "gemini-2.5-flash"
        assert data["input_tokens"] == 50
        assert data["output_tokens"] == 100

    def test_creates_directory(self, tmp_path):
        nested = tmp_path / "sub" / "dir"
        class MockClient:
            last_raw_response = {}
        entrypoint.write_token_usage(MockClient(), "claude", nested)
        assert (nested / "token_usage.json").exists()

    def test_handles_none_response(self, tmp_path):
        class MockClient:
            last_raw_response = None
        entrypoint.write_token_usage(MockClient(), "grok", tmp_path)
        import json
        data = json.loads((tmp_path / "token_usage.json").read_text())
        assert data["model"] == "grok"
        assert data["input_tokens"] is None


if __name__ == '__main__':
    pytest.main([__file__])

# end tests/test_entrypoint.py
