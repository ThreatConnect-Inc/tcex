#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from batch_group_tests import batch_group_creation_interface_1
from batch_group_tests import batch_group_creation_interface_2
from batch_group_tests import batch_group_creation_interface_3
import validator
import utility


def test_interface_1():
    """Test group creation via the first interface."""
    tcex_instance = utility.init_tcex()
    owner = tcex_instance.args.api_default_org
    batch = tcex_instance.batch(owner)
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
    results = batch.submit_all()
    assert results[0]['errorCount'] == 0
    assert results[0]['successCount'] == 11
    validator.validate(tcex_instance, expected_groups=11)


def test_interface_2():
    """Test group creation via the second interface."""
    tcex_instance = utility.init_tcex()
    owner = tcex_instance.args.api_default_org
    batch = tcex_instance.batch(owner)
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
    results = batch.submit_all()
    assert results[0]['errorCount'] == 0
    assert results[0]['successCount'] == 11
    validator.validate(tcex_instance, expected_groups=11)


def test_interface_3():
    """Test group creation via the third interface."""
    tcex_instance = utility.init_tcex()
    owner = tcex_instance.args.api_default_org
    batch = tcex_instance.batch(owner)
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
    results = batch.submit_all()
    assert results[0]['errorCount'] == 0
    assert results[0]['successCount'] == 11
    validator.validate(tcex_instance, expected_groups=11)
