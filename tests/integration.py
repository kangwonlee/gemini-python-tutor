# The test cases here should use appropriate
# asserts to verify that the output of the
# integration is correct.
# That is, after separately running the
# unit test cases (see tests.py), your
# workflow should run the action locally
# against the action's own repository,
# and then after that, run these integration
# tests.

import logging
import os


import pytest


logging.basicConfig(level=logging.INFO)


def get_github_output() -> str:
    '''
    Reads the GITHUB_OUTPUT environment file and returns the value of the specified output.
    '''

    with open(os.environ['GITHUB_OUTPUT'], 'r') as f:
        txt = f.read()

    logging.warning(f'Contents of GITHUB_OUTPUT: {len(txt)} characters')

    txt_lines = txt.splitlines()

    logging.warning(f'# lines of GITHUB_OUTPUT: {len(txt_lines)}')

    if len(txt_lines) < 100:
        logging.info(txt)

    return len(txt)


def test_feedback() -> None:
    feedback_str = get_github_output()
    assert feedback_str, 'No feedback found'


if "__main__" == __name__:
    pytest.main([__file__])
