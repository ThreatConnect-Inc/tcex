"""Python Backports"""


# standard library
# flake8: noqa
from typing import Callable

try:
    # standard library
    from functools import cached_property as functool_cached_property
except ImportError:
    # third-party
    from backports.cached_property import cached_property as functool_cached_property


class cached_property(functool_cached_property):
    """Customized cached_property."""

    instances = []

    def __get__(self, instance, owner=None):
        """Override method."""
        self.instances.append(instance)
        return super().__get__(instance, owner)

    @staticmethod
    def _reset():
        """Reset cache"""
        for i in cached_property.instances:
            for key, value in i.__dict__.items():
                if isinstance(value, cached_property):
                    del i.__dict__[key]
