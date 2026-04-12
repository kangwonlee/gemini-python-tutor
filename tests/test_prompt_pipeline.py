# begin tests/test_prompt_pipeline.py
"""Tests for prompt_pipeline code-generation config overrides."""
import pathlib
import sys

import pytest


# Adjust sys.path to import from project root
test_folder = pathlib.Path(__file__).parent.resolve()
project_folder = test_folder.parent.resolve()
sys.path.insert(0, str(project_folder))

from llm_configs import (
    ClaudeConfig, GeminiConfig, GrokConfig, NvidiaNIMConfig, PerplexityConfig,
)

# prompt_pipeline.entrypoint imports from the tutor entrypoint via sys.path
# manipulation that only works inside Docker.  Import the constants and
# function we need by loading the file directly with importlib.
import importlib.util

_pp_spec = importlib.util.spec_from_file_location(
    "prompt_pipeline_entrypoint",
    project_folder / "prompt_pipeline" / "entrypoint.py",
    submodule_search_locations=[],
)
_pp_mod = importlib.util.module_from_spec(_pp_spec)

# Satisfy the "from entrypoint import ..." that prompt_pipeline/entrypoint.py
# does at import time — point it at the tutor's entrypoint module.
sys.modules['entrypoint'] = importlib.import_module('entrypoint')
_pp_spec.loader.exec_module(_pp_mod)

CODEGEN_MAX_TOKENS = _pp_mod.CODEGEN_MAX_TOKENS
CODEGEN_TEMPERATURE = _pp_mod.CODEGEN_TEMPERATURE
patch_config_for_codegen = _pp_mod.patch_config_for_codegen


SAMPLE_API_KEY = "test_api_key_for_codegen"
SAMPLE_QUESTION = "Write a function that computes factorial."


# --- patch_config_for_codegen tests ---


class TestPatchGemini:
    """Gemini uses generationConfig with different key names."""

    @pytest.fixture
    def config(self):
        c = GeminiConfig(api_key=SAMPLE_API_KEY)
        patch_config_for_codegen(c)
        return c

    def test_has_generation_config(self, config):
        data = config.format_request_data(SAMPLE_QUESTION)
        assert 'generationConfig' in data

    def test_max_output_tokens(self, config):
        data = config.format_request_data(SAMPLE_QUESTION)
        assert data['generationConfig']['maxOutputTokens'] == CODEGEN_MAX_TOKENS

    def test_temperature_zero(self, config):
        data = config.format_request_data(SAMPLE_QUESTION)
        assert data['generationConfig']['temperature'] == CODEGEN_TEMPERATURE

    def test_contents_preserved(self, config):
        data = config.format_request_data(SAMPLE_QUESTION)
        assert 'contents' in data
        assert data['contents'][0]['parts'][0]['text'] == SAMPLE_QUESTION


class TestPatchGrok:
    """Grok already sets temperature=0; patch should override max_tokens."""

    @pytest.fixture
    def config(self):
        c = GrokConfig(api_key=SAMPLE_API_KEY)
        patch_config_for_codegen(c)
        return c

    def test_max_tokens(self, config):
        data = config.format_request_data(SAMPLE_QUESTION)
        assert data['max_tokens'] == CODEGEN_MAX_TOKENS

    def test_temperature_zero(self, config):
        data = config.format_request_data(SAMPLE_QUESTION)
        assert data['temperature'] == CODEGEN_TEMPERATURE

    def test_model_preserved(self, config):
        data = config.format_request_data(SAMPLE_QUESTION)
        assert data['model'] == 'grok-code-fast'


class TestPatchNvidiaNIM:
    """NVIDIA NIM inherits base defaults (96 tokens, temp 0.2)."""

    @pytest.fixture
    def config(self):
        c = NvidiaNIMConfig(api_key=SAMPLE_API_KEY)
        patch_config_for_codegen(c)
        return c

    def test_max_tokens_overridden(self, config):
        data = config.format_request_data(SAMPLE_QUESTION)
        assert data['max_tokens'] == CODEGEN_MAX_TOKENS

    def test_temperature_overridden(self, config):
        data = config.format_request_data(SAMPLE_QUESTION)
        assert data['temperature'] == CODEGEN_TEMPERATURE


class TestPatchClaude:
    """Claude overrides max_tokens to 1024; patch should raise to CODEGEN_MAX_TOKENS."""

    @pytest.fixture
    def config(self):
        c = ClaudeConfig(api_key=SAMPLE_API_KEY)
        patch_config_for_codegen(c)
        return c

    def test_max_tokens_overridden(self, config):
        data = config.format_request_data(SAMPLE_QUESTION)
        assert data['max_tokens'] == CODEGEN_MAX_TOKENS

    def test_temperature_overridden(self, config):
        data = config.format_request_data(SAMPLE_QUESTION)
        assert data['temperature'] == CODEGEN_TEMPERATURE


class TestPatchPerplexity:
    """Perplexity overrides max_tokens to 384; patch should raise to CODEGEN_MAX_TOKENS."""

    @pytest.fixture
    def config(self):
        c = PerplexityConfig(api_key=SAMPLE_API_KEY)
        patch_config_for_codegen(c)
        return c

    def test_max_tokens_overridden(self, config):
        data = config.format_request_data(SAMPLE_QUESTION)
        assert data['max_tokens'] == CODEGEN_MAX_TOKENS

    def test_temperature_overridden(self, config):
        data = config.format_request_data(SAMPLE_QUESTION)
        assert data['temperature'] == CODEGEN_TEMPERATURE


class TestUnpatchedDefaults:
    """Verify that unpatched configs retain their original defaults."""

    def test_base_max_tokens_96(self):
        c = NvidiaNIMConfig(api_key=SAMPLE_API_KEY)
        data = c.format_request_data(SAMPLE_QUESTION)
        assert data['max_tokens'] == 96

    def test_base_temperature_02(self):
        c = NvidiaNIMConfig(api_key=SAMPLE_API_KEY)
        data = c.format_request_data(SAMPLE_QUESTION)
        assert data['temperature'] == 0.2

    def test_gemini_no_generation_config(self):
        c = GeminiConfig(api_key=SAMPLE_API_KEY)
        data = c.format_request_data(SAMPLE_QUESTION)
        assert 'generationConfig' not in data

    def test_claude_max_tokens_1024(self):
        c = ClaudeConfig(api_key=SAMPLE_API_KEY)
        data = c.format_request_data(SAMPLE_QUESTION)
        assert data['max_tokens'] == 1024

    def test_perplexity_max_tokens_384(self):
        c = PerplexityConfig(api_key=SAMPLE_API_KEY)
        data = c.format_request_data(SAMPLE_QUESTION)
        assert data['max_tokens'] == 384


class TestPatchDoesNotMutateOtherInstances:
    """Patching one config must not affect a separate instance."""

    def test_two_gemini_instances(self):
        patched = GeminiConfig(api_key=SAMPLE_API_KEY)
        unpatched = GeminiConfig(api_key=SAMPLE_API_KEY)
        patch_config_for_codegen(patched)

        assert 'generationConfig' in patched.format_request_data(SAMPLE_QUESTION)
        assert 'generationConfig' not in unpatched.format_request_data(SAMPLE_QUESTION)

    def test_two_grok_instances(self):
        patched = GrokConfig(api_key=SAMPLE_API_KEY)
        unpatched = GrokConfig(api_key=SAMPLE_API_KEY)
        patch_config_for_codegen(patched)

        assert patched.format_request_data(SAMPLE_QUESTION)['max_tokens'] == CODEGEN_MAX_TOKENS
        assert 'max_tokens' not in unpatched.format_request_data(SAMPLE_QUESTION)


if __name__ == "__main__":
    pytest.main(["--verbose", __file__])

# end tests/test_prompt_pipeline.py
