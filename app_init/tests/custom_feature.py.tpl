# -*- coding: utf-8 -*-
"""Custom test method feature class."""
from ..custom import Custom  # pylint: disable=relative-beyond-top-level


class CustomFeature(TriggerEvent):
    """Custom test method class Apps."""

    def __init__(self, **kwargs):  # pylint: disable=useless-super-delegation
        """Initialize class properties."""
        super(CustomFeature, self).__init__(**kwargs)
