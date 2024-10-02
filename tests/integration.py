# The test cases here should use appropriate
# asserts to verify that the output of the
# integration is correct.
# That is, after separately running the
# unit test cases (see tests.py), your
# workflow should run the action locally
# against the action's own repository,
# and then after that, run these integration
# tests.

import os


import pytest


def test_feedback() -> None:
    feedback_str = os.getenv('FEEDBACK')
    assert feedback_str, 'No feedback found'
