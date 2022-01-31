"""Rerun failed tests."""
# standard library
import json
import os
import sys

# third-party
import pytest

try:
    with open(os.path.join(os.getcwd(), '.pytest_cache', 'v', 'cache', 'lastfailed')) as f:
        data = json.load(f)
        tests = list(data.keys())
except Exception as ex:
    raise RuntimeError('Could not fetch list of failed tests from last run.') from ex

newline = '\n'
print(
    f'Executing last failed tests serially. Tests to execute ({len(tests)}):\n{newline.join(tests)}'
)
print(tests)

sys.exit(pytest.main(tests))
