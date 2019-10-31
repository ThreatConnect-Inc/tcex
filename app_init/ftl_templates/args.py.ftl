# -*- coding: utf-8 -*-
"""Auto-generated App Args"""

class Args(object):
    """App Args"""

    def __init__(self, parser):
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
