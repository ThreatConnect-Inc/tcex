"""Rerun failed tests."""
# standard library
import json
import os
import sys

# third-party
import pytest


def rerun():
    """Rerun failed tests."""

    try:
        failed_file = os.path.join(os.getcwd(), '.pytest_cache', 'v', 'cache', 'lastfailed')
        with open(failed_file) as f:
            data = json.load(f)
            tests = list(data.keys())
    except Exception as ex:
        raise RuntimeError('Could not fetch list of failed tests from last run.') from ex

    newline = '\n'
    print(
        'Executing last failed tests serially. Tests '
        f'to execute ({len(tests)}):\n{newline.join(tests)}'
    )
    sys.exit(pytest.main(tests))


if __name__ == '__main__':
    rerun()
