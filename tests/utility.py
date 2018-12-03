#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
import validator
import cleaner

import tcex


def init_tcex(requires_tc_token=False, clean_data=True):
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

    if requires_tc_token:
        if os.environ.get('TC_TOKEN'):
            tcex_instance.args.tc_token = os.environ['TC_TOKEN']
            # parse the expiration timestamp from the tc_token
            tcex_instance.args.tc_token_expires = tcex_instance.args.tc_token.split(':')[4]
        # if the request requires a token and a token is not found, raise an error
        else:
            raise RuntimeError('The TC_TOKEN environmental variable is required and was not found. Please add it (you can find instructions for doing so here: https://gitlab.com/fhightower-tc/tcex-playground#setup).')

    if clean_data:
        # clear out any data in the source
        cleaner.clean(tcex_instance)
        validator.validate(tcex_instance, expected_groups=0, expected_indicators=0)

    return tcex_instance
