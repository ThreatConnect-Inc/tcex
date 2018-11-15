#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cleaner


def _add_indicator(batch_job, type_, summary):
    batch_job.add_indicator({
        "type": type_,
        "rating": 5.00,
        "confidence": 100,
        "summary": summary,
        "attribute": [{
            "type": "Description",
            "displayed": True,
            "value": "Example Description"
        }],
        "xid": cleaner._create_xid(type_, summary)
    })


def address_create(batch_job):
    _add_indicator(batch_job, 'Address', '123.124.125.126')


def email_address_create(batch_job):
    _add_indicator(batch_job, 'EmailAddress', 'bad@dfadsfaddsfa.com')


def file_create(batch_job):
    _add_indicator(batch_job, 'File', '{} : {} : {}'.format('a'*32, 'b'*40, 'c'*64))


def host_create(batch_job):
    _add_indicator(batch_job, 'Host', 'dfadsfaddsfa.com')


def url_create(batch_job):
    _add_indicator(batch_job, 'Url', 'https://dfadsfaddsfa.com/index.html')
