#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Delete indicators and groups which have been created for the tests."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import validator  # pylint: disable=C0413
import utility


def _delete_groups(tcex):
    batch = tcex.batch(tcex.args.api_default_org, action='Delete')
    groups = validator.get_groups(tcex)
    for group in groups:
        group['xid'] = utility._create_xid(group['type'], group['name'])
        batch.add_group(group)
    batch.submit_all()


def _delete_indicators(tcex):
    batch = tcex.batch(tcex.args.api_default_org, action='Delete')
    indicators = validator.get_indicators(tcex)
    for indicator in indicators:
        indicator['xid'] = utility._create_xid(indicator['type'], indicator['summary'])
        batch.add_indicator(indicator)
    batch.submit_all()


def clean(tcex):
    """Delete all indicators and groups in the source."""
    _delete_groups(tcex)
    _delete_indicators(tcex)
