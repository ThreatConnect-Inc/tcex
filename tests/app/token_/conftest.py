"""Conftest for token tests — force serial execution under xdist."""

# third-party
import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Assign all token_ tests to the same xdist group so they run serially."""
    for item in items:
        if 'token_' in item.nodeid:
            item.add_marker(pytest.mark.xdist_group('token'))
