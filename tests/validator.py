#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate that test results are correct."""


def get_groups(tcex):
    resource = tcex.resource('Group')
    resource.owner = tcex.args.api_default_org
    groups = []
    # paginate over results
    for result in resource:
        groups.extend([group for group in result['data']])
    return groups


def get_indicators(tcex):
    resource = tcex.resource('Indicator')
    resource.owner = tcex.args.api_default_org
    indicators = []
    # paginate over results
    for result in resource:
        indicators.extend([indicator for indicator in result['data']])
    return indicators


def validate(tcex, expected_groups=None, expected_indicators=None):
    """Validate that the number of groups and indicators are correct."""
    if expected_groups is not None:
        groups = get_groups(tcex)
        assert len(groups) == expected_groups

    if expected_indicators is not None:
        indicators = get_indicators(tcex)
        assert len(indicators) == expected_indicators
