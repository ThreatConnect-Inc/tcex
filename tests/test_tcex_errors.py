#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import tcex

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
import validator


def test_invalid_token_error():
    """Test to make sure a proper error is raised when there is an invalid token."""
    tcex_instance = tcex.TcEx()
    tcex_instance.args.tc_token = "85:-1:-1:-1:1539988200:-1:TbYcs7Ad9BWCepdT8Lr8aPvWmcD3fvtWFLc4O0M0QSU="
    # this parses the expiration timestamp from the token
    tcex_instance.args.tc_token_expires = tcex_instance.args.tc_token.split(':')[4]

    # make sure an error is raised when there is an invalid token
    recieved_error = False
    try:
        validator.get_groups(tcex_instance)
    except RuntimeError as e:
        recieved_error = True
        assert "205, 'Invalid token" in str(e)
    assert recieved_error
