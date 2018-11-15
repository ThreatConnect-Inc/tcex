#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from batch_indicator_tests import batch_ind_creation_interface_1, batch_ind_creation_interface_2, batch_ind_creation_interface_3
import validator
import utility


def test_interface_1():
    """Test indicator creation via the first interface."""
    tcex_instance = utility.init_tcex()
    owner = tcex_instance.args.api_default_org
    batch = tcex_instance.batch(owner)
    batch_ind_creation_interface_1.address_create(batch)
    batch_ind_creation_interface_1.email_address_create(batch)
    batch_ind_creation_interface_1.file_create(batch)
    batch_ind_creation_interface_1.host_create(batch)
    batch_ind_creation_interface_1.url_create(batch)
    batch.submit_all()
    validator.validate(tcex_instance, expected_indicators=5)


def test_interface_2():
    """Test indicator creation via the second interface."""
    tcex_instance = utility.init_tcex()
    owner = tcex_instance.args.api_default_org
    batch = tcex_instance.batch(owner)
    batch_ind_creation_interface_2.address_create(batch)
    batch_ind_creation_interface_2.email_address_create(batch)
    batch_ind_creation_interface_2.file_create(batch)
    batch_ind_creation_interface_2.host_create(batch)
    batch_ind_creation_interface_2.url_create(batch)
    batch.submit_all()
    validator.validate(tcex_instance, expected_indicators=5)


def test_interface_3():
    """Test indicator creation via the third interface."""
    tcex_instance = utility.init_tcex()
    owner = tcex_instance.args.api_default_org
    batch = tcex_instance.batch(owner)
    batch_ind_creation_interface_3.address_create(batch)
    batch_ind_creation_interface_3.email_address_create(batch)
    batch_ind_creation_interface_3.file_create(batch)
    batch_ind_creation_interface_3.host_create(batch)
    batch_ind_creation_interface_3.url_create(batch)
    batch.submit_all()
    validator.validate(tcex_instance, expected_indicators=5)
