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


def get_github_output(output_name:str) -> str:
    '''
    Reads the GITHUB_OUTPUT environment file and returns the value of the specified output.
    '''
    result = None

    with open(os.environ['GITHUB_OUTPUT'], 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            if key == output_name:
                result = value

    if result is None:
        logging.warning(f'Output {output_name} not found in GITHUB_OUTPUT file')

    return result  # Or raise an exception if the output is not found


def test_feedback() -> None:
    feedback_str = get_github_output('feedback')
    assert feedback_str, 'No feedback found'
