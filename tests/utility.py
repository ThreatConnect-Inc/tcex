#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
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
