#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module to test batch indicator creation using interface 1"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utility  # pylint: disable=C0413


def address_create(batch_job):
    """Test address creation"""
    address = batch_job.address('123.124.125.126', rating='5.0', confidence='100', xid=utility._create_xid('address', '123.124.125.126'))
    address.attribute('Description', 'Example Description', True)
    address.tag('Example Tag')
    address.security_label('TLP Green')


def email_address_create(batch_job):
    """Test email address creation"""
    email_address = batch_job.email_address('bad@dfadsfaddsfa.com', rating='5.0', confidence='100', xid=utility._create_xid('email address', 'bad@dfadsfaddsfa.com'))
    email_address.attribute('Description', 'Example Description', True)
    email_address.tag('Example Tag')
    email_address.security_label('TLP Green')


def file_create(batch_job):
    """Test file creation"""
    file = batch_job.file(
        md5='a' * 32, sha1='b' * 40, sha256='c' * 64, rating='5.0', confidence='100', xid=utility._create_xid('file', 'a' * 32)
    )
    file.attribute('Description', 'Example Description', True)
    file.tag('Example Tag')
    file.security_label('TLP Green')


def host_create(batch_job):
    """Test host creation"""
    host = batch_job.host('dfadsfaddsfa.com', rating='5.0', confidence='100', xid=utility._create_xid('host', 'dfadsfaddsfa.com'))
    host.attribute('Description', 'Example Description', True)
    host.tag('Example Tag')
    host.security_label('TLP Green')


def url_create(batch_job):
    """Test url creation"""
    url = batch_job.url('https://dfadsfaddsfa.com/index.html', rating='5.0', confidence='100', xid=utility._create_xid('url', 'https://dfadsfaddsfa.com/index.html'))
    url.attribute('Description', 'Example Description', True)
    url.tag('Example Tag')
    url.security_label('TLP Green')
