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

    found_keys = []

    with open(os.environ['GITHUB_OUTPUT'], 'r') as f:
        txt = f.read()

    logging.info(f'Contents of GITHUB_OUTPUT: {len(txt)} characters')

    txt_lines = txt.splitlines()

    logging.info(f'# lines of GITHUB_OUTPUT: {len(txt_lines)}')

    for line in txt.splitlines():
        key, value = line.strip().split('=')
        found_keys.append(key)
        if key == output_name:
            result = value

    if result is None:
        logging.warning(
            f'Output {output_name} not found in GITHUB_OUTPUT file\n'
            f'Keys found: {found_keys}'
        )

    return result  # Or raise an exception if the output is not found


def test_feedback() -> None:
    feedback_str = get_github_output('feedback')
    assert feedback_str, 'No feedback found'
