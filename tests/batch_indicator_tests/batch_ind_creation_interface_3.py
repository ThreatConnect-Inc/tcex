#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module to test batch indicator creation using interface 3"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utility  # pylint: disable=C0413


def _add_indicator(batch_job, type_, summary):
    """Test indicator creation"""
    batch_job.add_indicator(
        {
            'type': type_,
            'rating': 5.00,
            'confidence': 100,
            'summary': summary,
            'attribute': [
                {'type': 'Description', 'displayed': True, 'value': 'Example Description'}
            ],
            'xid': utility._create_xid(type_, summary),  # pylint: disable=W0212
        }
    )


def address_create(batch_job):
    """Test address creation"""
    _add_indicator(batch_job, 'Address', '123.124.125.126')


def email_address_create(batch_job):
    """Test email address creation"""
    _add_indicator(batch_job, 'EmailAddress', 'bad@dfadsfaddsfa.com')


def file_create(batch_job):
    """Test file creation"""
    _add_indicator(batch_job, 'File', '{} : {} : {}'.format('a' * 32, 'b' * 40, 'c' * 64))


def host_create(batch_job):
    """Test host creation"""
    _add_indicator(batch_job, 'Host', 'dfadsfaddsfa.com')


def url_create(batch_job):
    """Test url creation"""
    _add_indicator(batch_job, 'Url', 'https://dfadsfaddsfa.com/index.html')
