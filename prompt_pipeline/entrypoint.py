#!/usr/bin/env python3
# begin prompt_pipeline/entrypoint.py
#
# Generate exercise.py from student's prompt.txt via LLM.
# Called from the Docker container during the prompt pipeline workflow step.
#
# Environment variables (set by classroom-prompt-reusable.yml):
#   INPUT_PROMPT-FILE    Path to student's prompt.txt inside the container
#   CONTAINER_OUTPUT     Directory where exercise.py will be written
#   INPUT_MODEL          LLM model name (optional)
#   INPUT_CLAUDE_API_KEY, INPUT_GEMINI-API-KEY, INPUT_GROK-API-KEY,
#   INPUT_NVIDIA-API-KEY, INPUT_PERPLEXITY-API-KEY  (at least one required)

import logging
import os
import pathlib
import re
import sys

logging.basicConfig(level=logging.INFO)

# ai_tutor/ lives one level above prompt_pipeline/ inside the container:
#   /app/ai_tutor/   ← llm_client.py, llm_configs.py, entrypoint.py
#   /app/prompt_pipeline/  ← this file
# In CI / local dev, the modules live at the repo root instead.
_project_root = pathlib.Path(__file__).parent.parent
_ai_tutor = _project_root / 'ai_tutor'
if _ai_tutor.is_dir():
    sys.path.insert(0, str(_ai_tutor))
else:
    sys.path.insert(0, str(_project_root))

from llm_client import LLMAPIClient  # noqa: E402
from llm_configs import GeminiConfig, LLMConfig  # noqa: E402
from entrypoint import get_model_key_from_env, get_config_class  # noqa: E402


# Code generation needs higher token limits and deterministic output.
# Tutoring (entrypoint.py) uses the config defaults (96 tokens, temp 0.2).
CODEGEN_MAX_TOKENS = 4096
CODEGEN_TEMPERATURE = 0


def patch_config_for_codegen(config: LLMConfig) -> None:
    """Override generation parameters for code generation.

    Wraps config.format_request_data to set higher max_tokens and
    temperature=0. Gemini uses ``generationConfig``; OpenAI-compatible
    providers use top-level ``max_tokens`` / ``temperature``.
    """
    original = config.format_request_data

    if isinstance(config, GeminiConfig):
        def patched(question: str):
            data = original(question)
            data['generationConfig'] = {
                'maxOutputTokens': CODEGEN_MAX_TOKENS,
                'temperature': CODEGEN_TEMPERATURE,
            }
            return data
    else:
        def patched(question: str):
            data = original(question)
            data['max_tokens'] = CODEGEN_MAX_TOKENS
            data['temperature'] = CODEGEN_TEMPERATURE
            return data

    config.format_request_data = patched


# Python code detection patterns — prompts containing these are rejected.
# The intent is to prevent students from submitting code instead of prompts.
_CODE_PATTERNS = re.compile(
    r'^\s*(def |class |import |from .+ import|if .+:|for .+:|while .+:|print\(|[a-zA-Z_]\w*\s*=\s*)',
    re.MULTILINE,
)


def contains_python_code(text: str) -> bool:
    """Return True if *text* appears to contain Python code constructs."""
    return bool(_CODE_PATTERNS.search(text))


_SYSTEM_INSTRUCTION = (
    "You are a Python code generator for a university programming assignment. "
    "The student has described what Python code they need. "
    "Generate clean, correct Python code that satisfies their requirements. "
    "Rules:\n"
    "- Output ONLY a single ```python code block.\n"
    "- Do not include any explanations, prose, or text outside the code block.\n"
    "- All executable code must be inside functions.\n"
    "- Do not import modules that are not needed.\n"
    "- Do not add a main guard or standalone executable code at module level.\n"
)


def extract_python_code(response: str) -> str:
    """Return Python source from the first ```python … ``` block in *response*.

    Falls back to the first plain ``` … ``` block, then to the raw response.
    """
    for pattern in (r'```python\s*(.*?)```', r'```\s*(.*?)```'):
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
    return response.strip()


def build_question(student_prompt: str) -> str:
    return f"{_SYSTEM_INSTRUCTION}\n\nStudent requirements:\n{student_prompt}"


def main() -> None:
    prompt_path = pathlib.Path(os.environ['INPUT_PROMPT-FILE'])
    output_dir = pathlib.Path(os.environ['CONTAINER_OUTPUT'])

    if not prompt_path.exists():
        logging.error("Prompt file not found: %s", prompt_path)
        sys.exit(1)

    student_prompt = prompt_path.read_text(encoding='utf-8').strip()
    if not student_prompt:
        logging.error("Prompt file is empty: %s", prompt_path)
        sys.exit(1)

    if contains_python_code(student_prompt):
        logging.warning(
            "Prompt appears to contain Python code constructs. "
            "This will be penalized by the grader. "
            "Write a natural language description, not code."
        )

    logging.info("Prompt length: %d chars", len(student_prompt))

    model, api_key = get_model_key_from_env()
    config_class = get_config_class(model)
    config_args = {'api_key': api_key}
    if model:
        config_args['model'] = model
    config = config_class(**config_args)
    patch_config_for_codegen(config)
    client = LLMAPIClient(config)

    question = build_question(student_prompt)
    logging.info("Calling %s for code generation...", model)
    response = client.call_api(question)

    if not response:
        logging.error("No response from LLM — check API key and model name")
        sys.exit(1)

    code = extract_python_code(response)
    if not code:
        logging.error("LLM response contained no Python code block")
        logging.error("Raw response (first 500 chars): %s", response[:500])
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'exercise.py'
    output_file.write_text(code, encoding='utf-8')
    logging.info("exercise.py written to %s (%d chars)", output_file, len(code))


if __name__ == '__main__':
    main()

# end prompt_pipeline/entrypoint.py
