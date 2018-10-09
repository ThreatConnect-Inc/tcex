#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import batch_group_creation_interface_1
import batch_group_creation_interface_2
import batch_group_creation_interface_3
import validator
import cleaner


def test_interface_1(tcex):
    """Test group creation via the first interface."""
    owner = tcex.args.api_default_org
    batch = tcex.batch(owner)
    batch_group_creation_interface_1.adversary_create(batch)
    batch_group_creation_interface_1.campaign_create(batch)
    batch_group_creation_interface_1.document_create(batch)
    batch_group_creation_interface_1.document_malware_create(batch)
    batch_group_creation_interface_1.email_create(batch)
    batch_group_creation_interface_1.event_create(batch)
    batch_group_creation_interface_1.incident_create(batch)
    batch_group_creation_interface_1.intrusion_set_create(batch)
    batch_group_creation_interface_1.report_create(batch)
    batch_group_creation_interface_1.signature_create(batch)
    batch_group_creation_interface_1.threat_create(batch)
    batch.submit_all()
    validator.validate(tcex, expected_groups=11)
    cleaner.clean(tcex)


def test_interface_2(tcex):
    """Test group creation via the second interface."""
    owner = tcex.args.api_default_org
    batch = tcex.batch(owner)
    batch_group_creation_interface_2.adversary_create(batch)
    batch_group_creation_interface_2.campaign_create(batch)
    batch_group_creation_interface_2.document_create(batch)
    batch_group_creation_interface_2.document_malware_create(batch)
    batch_group_creation_interface_2.email_create(batch)
    batch_group_creation_interface_2.event_create(batch)
    batch_group_creation_interface_2.incident_create(batch)
    batch_group_creation_interface_2.intrusion_set_create(batch)
    batch_group_creation_interface_2.report_create(batch)
    batch_group_creation_interface_2.signature_create(batch)
    batch_group_creation_interface_2.threat_create(batch)
    batch.submit_all()
    validator.validate(tcex, expected_groups=11)
    cleaner.clean(tcex)


def test_interface_3(tcex):
    """Test group creation via the third interface."""
    owner = tcex.args.api_default_org
    batch = tcex.batch(owner)
    batch_group_creation_interface_3.adversary_create(batch)
    batch_group_creation_interface_3.campaign_create(batch)
    batch_group_creation_interface_3.document_create(batch)
    batch_group_creation_interface_3.document_malware_create(batch)
    batch_group_creation_interface_3.email_create(batch)
    batch_group_creation_interface_3.event_create(batch)
    batch_group_creation_interface_3.incident_create(batch)
    batch_group_creation_interface_3.intrusion_set_create(batch)
    batch_group_creation_interface_3.report_create(batch)
    batch_group_creation_interface_3.signature_create(batch)
    batch_group_creation_interface_3.threat_create(batch)
    batch.submit_all()
    validator.validate(tcex, expected_groups=11)
    cleaner.clean(tcex)


def group_create_without_xid(tcex):
    """Try to create an adversary without an XID to make sure a key-error is thrown."""
    owner = tcex.args.api_default_org
    batch_job = tcex.batch(owner)
    try:
        batch_job.add_group({
            'name': 'adversary-broken',
            'type': 'Adversary',
            'attribute': [{
                "displayed": True,
                "type": "Description",
                "value": "Example Description"
            }],
            'tag': [{
                'name': 'Example Tag'
            }]
        })
    except KeyError:
        # we can move on if a KeyError is thrown - we are expecting a KeyError
        pass
    else:
        raise RuntimeError('No "KeyError" was thrown when trying to create an adversary without an xid')
