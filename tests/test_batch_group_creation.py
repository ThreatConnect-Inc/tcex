#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from batch_group_tests import batch_group_creation_interface_1
from batch_group_tests import batch_group_creation_interface_2
from batch_group_tests import batch_group_creation_interface_3
import validator
import cleaner

# This deletes the first path which will be to the ../tcex directory. This is added automatically by pytest and must be removed to make sure that the tests use the version of tcex in the ./lib_2.7.12 directory.
del sys.path[0]

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "./lib_2.7.12")))
import tcex


def init_tcex():
    """Initialize the tcex instance."""
    tcex_instance = tcex.TcEx()
    tcex_instance.log.debug('Creating content in {}. If this is not correct, pass in a different owner name using the --api_default_org flag.'.format(tcex_instance.args.api_default_org))
    tcex_instance.args.api_access_id = os.environ['API_ACCESS_ID']
    tcex_instance.args.tc_temp_path = 'log'
    # this manually sets the logging level
    tcex_instance.log.setLevel(logging.DEBUG)
    tcex_instance.args.tc_log_path = 'log'
    tcex_instance.args.tc_out_path = 'log'
    tcex_instance.args.tc_api_path = os.environ['TC_API_PATH']
    tcex_instance.args.api_default_org = os.environ['API_DEFAULT_ORG']
    tcex_instance.args.api_secret_key = os.environ['API_SECRET_KEY']

    # clear out any data in the source
    cleaner.clean(tcex_instance)
    validator.validate(tcex_instance, expected_groups=0, expected_indicators=0)

    return tcex_instance


def test_interface_1():
    """Test group creation via the first interface."""
    tcex_instance = init_tcex()
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
    batch.submit_all()
    validator.validate(tcex_instance, expected_groups=11)


def test_interface_2():
    """Test group creation via the second interface."""
    tcex_instance = init_tcex()
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
    batch.submit_all()
    validator.validate(tcex_instance, expected_groups=11)


def test_interface_3():
    """Test group creation via the third interface."""
    tcex_instance = init_tcex()
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
    batch.submit_all()
    validator.validate(tcex_instance, expected_groups=11)
