# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
import utility
import cleaner


def verify_association_created(tcex):
    """."""
    resource = tcex.resource('Address')
    resource.resource_id('4.5.6.7')

    for result in resource:
        this_indicator_resource = tcex.resource('Address')
        this_indicator_resource.resource_id(result['data']['ip'])
        associated_asns = tcex.resource(tcex.safe_rt('ASN', lower=False))
        associations_resource = this_indicator_resource.associations(associated_asns)
        associations_results = associations_resource.request()
        assert len(associations_results['data']) == 1


def test_indicator_associations():
    """."""
    tcex = utility.init_tcex()
    tcex.jobs.indicator({
        "summary": "4.5.6.7",
        "type": "Address",
    })
    tcex.jobs.indicator({
        "summary": "ASN1234",
        "type": tcex.safe_rt('ASN', lower=False),
    })
    tcex.jobs.association({
        'association_value': 'ASN1234',
        'association_type': tcex.safe_rt('ASN', lower=False),
        'resource_value': '4.5.6.7',
        'resource_type': 'Address'
    })
    tcex.jobs.process(tcex.args.api_default_org)
    assert len(tcex.jobs.indicator_results['failed']) == 0
    assert len(tcex.jobs.indicator_results['not_saved']) == 0
    assert len(tcex.jobs.indicator_results['saved']) == 2

    verify_association_created(tcex)
    cleaner.clean()
