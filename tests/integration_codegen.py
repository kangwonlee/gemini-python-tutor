# begin tests/integration_codegen.py
"""Integration tests for the prompt pipeline (code generation).

Run after prompt_pipeline/entrypoint.py has generated exercise.py.
Verifies the output is valid Python containing the expected functions.
"""
import ast
import logging
import os
import pathlib

import pytest


logging.basicConfig(level=logging.INFO)


@pytest.fixture
def exercise_path():
    """Path to the generated exercise.py."""
    output_dir = os.environ.get('CONTAINER_OUTPUT', '')
    if not output_dir:
        pytest.skip("CONTAINER_OUTPUT not set")
    path = pathlib.Path(output_dir) / 'exercise.py'
    if not path.exists():
        pytest.fail(f"exercise.py not found at {path}")
    return path


@pytest.fixture
def exercise_source(exercise_path):
    """Raw source code of generated exercise.py."""
    return exercise_path.read_text(encoding='utf-8')


@pytest.fixture
def exercise_ast(exercise_source):
    """Parsed AST of generated exercise.py."""
    try:
        return ast.parse(exercise_source)
    except SyntaxError as e:
        pytest.fail(f"exercise.py has invalid syntax: {e}")


def test_exercise_exists(exercise_path):
    """exercise.py was written to disk."""
    assert exercise_path.exists()


def test_exercise_not_empty(exercise_source):
    """exercise.py is not empty."""
    assert len(exercise_source.strip()) > 0


def test_exercise_valid_python(exercise_ast):
    """exercise.py parses as valid Python."""
    assert exercise_ast is not None


def test_exercise_has_add_function(exercise_ast):
    """exercise.py defines an `add` function."""
    func_names = [
        node.name for node in ast.walk(exercise_ast)
        if isinstance(node, ast.FunctionDef)
    ]
    assert 'add' in func_names, (
        f"Expected 'add' function, found: {func_names}"
    )


def test_exercise_has_multiply_function(exercise_ast):
    """exercise.py defines a `multiply` function."""
    func_names = [
        node.name for node in ast.walk(exercise_ast)
        if isinstance(node, ast.FunctionDef)
    ]
    assert 'multiply' in func_names, (
        f"Expected 'multiply' function, found: {func_names}"
    )


def test_exercise_not_truncated(exercise_source):
    """exercise.py is long enough to contain two function definitions."""
    assert len(exercise_source) > 50, (
        f"exercise.py suspiciously short ({len(exercise_source)} chars) "
        "— may have been truncated by low max_tokens"
    )


if __name__ == "__main__":
    pytest.main(["--verbose", __file__])

# end tests/integration_codegen.py
