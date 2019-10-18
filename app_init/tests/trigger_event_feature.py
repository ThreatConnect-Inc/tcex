# -*- coding: utf-8 -*-
"""Trigger EVent feature class."""
from ..trigger_event import TriggerEvent  # pylint: disable=relative-beyond-top-level


class TriggerEventFeature(TriggerEvent):
    """Trigger Event for Trigger based Apps."""

    def __init__(self, **kwargs):  # pylint: disable=useless-super-delegation
        """Initialize class properties."""
        super(TriggerEventFeature, self).__init__(**kwargs)
