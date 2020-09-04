# -*- coding: utf-8 -*-
"""Auto-generated App Args"""
from argparse import ArgumentParser

class Args:
    """App Args"""

    def __init__(self, parser: ArgumentParser):
        """Initialize class properties."""
<#list install.params as param>
<#if param.type == "Boolean">
        parser.add_argument('--${param.name}', action='store_true')
<#elseif param.type == "MultiChoice" || param.allowMultiple == true>
        parser.add_argument('--${param.name}', action='append')
<#else>
        parser.add_argument('--${param.name}'<#if param.defaultValue??>, default='${param.defaultValue}'</#if>)
</#if>
</#list>
