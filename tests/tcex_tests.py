# -*- coding: utf-8 -*-
"""Test the TcEx app."""

import tcex

from testing_scripts import batch_group_creation_test, cleaner

tcex_instance = tcex.TcEx()
tcex_instance.log.debug('Creating content in {}. If this is not correct, pass in a different owner name using the --api_default_org flag.'.format(tcex_instance.args.api_default_org))

# TODO: it would be great to have a prefix on everything created using these tests so we can just delete that
# clear out the indicators and groups
cleaner.clean(tcex_instance)

# call the test functions
batch_group_creation_test.group_create_without_xid(tcex_instance)
batch_group_creation_test.test_interface_1(tcex_instance)
batch_group_creation_test.test_interface_2(tcex_instance)
batch_group_creation_test.test_interface_3(tcex_instance)
