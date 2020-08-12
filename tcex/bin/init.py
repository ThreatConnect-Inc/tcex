#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx App Init."""
from ..app_config_object.templates import DownloadTemplates
from .bin import Bin


class Init(Bin):
    """Install required modules for ThreatConnect Job or Playbook App.

    Args:
        _args (namespace): The argparser args Namespace.
    """

    def __init__(self, _args):
        """Initialize Class properties."""
        super().__init__(_args)
        self.download_template = DownloadTemplates(branch=self.args.branch)
