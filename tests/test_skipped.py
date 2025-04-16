# begin tests/test_skipped.py
import os
import pathlib
import pytest
import sys


file_path = pathlib.Path(__file__)
test_path = file_path.parent.resolve()
skipped_path = test_path / 'skipped'
proj_folder = test_path.parent.resolve()
sys.path.insert(0, str(proj_folder))

import entrypoint


assert skipped_path.exists(), f"Path {skipped_path} does not exist"
assert skipped_path.is_dir(), f"Path {skipped_path} is not a directory"


def test_skipped_do_not_count() -> None:
    """
    Test that skipped tests do not count towards the total number of tests.
    """
    
    os.environ['INPUT_MODEL'] = 'grok'
    os.environ['INPUT_REPORT-FILES'] = ','.join([str(p) for p in skipped_path.glob('*.json')])
    os.environ['INPUT_STUDENT-FILES'] = str(test_path/'sample_code.py')
    os.environ['INPUT_README-PATH'] = str(test_path/'sample_readme.md')
    os.environ['INPUT_CLAUDE_API_KEY'] = 'test-key'
    os.environ['INPUT_GEMINI-API-KEY'] = 'test-key'
    os.environ['INPUT_GROK-API-KEY'] = 'test-key'
    os.environ['INPUT_NVIDIA-API-KEY'] = 'test-key'
    os.environ['INPUT_PERPLEXITY-API-KEY'] = 'test-key'

    entrypoint.main(b_ask=False)


if "__main__" == __name__:
    pytest.main([__file__])
# end tests/test_skipped.py
