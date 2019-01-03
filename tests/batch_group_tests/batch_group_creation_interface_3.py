#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module to test batch creation using interface 3"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utility  # pylint: disable=C0413


def adversary_create(batch_job):
    """Test adversary creation"""
    batch_job.add_group(
        {
            'name': 'adversary-003',
            'type': 'Adversary',
            'xid': utility._create_xid('Adversary', 'adversary-003'),  # pylint: disable=W0212
            'attribute': [
                {'displayed': True, 'type': 'Description', 'value': 'Example Description'}
            ],
            'tag': [{'name': 'Example Tag'}],
        }
    )


def campaign_create(batch_job):
    """Test campaign creation"""
    batch_job.add_group(
        {
            'name': 'campaign-003',
            'type': 'Campaign',
            'xid': utility._create_xid('Campaign', 'campaign-003'),  # pylint: disable=W0212
            'attribute': [
                {'displayed': True, 'type': 'Description', 'value': 'Example Description'}
            ],
            'tag': [{'name': 'Example Tag'}],
        }
    )


def document_create(batch_job):
    """Test document creation"""
    batch_job.add_group(
        {
            'name': 'document-003',
            'fileName': 'test.txt',
            'fileContent': 'Document content',
            'type': 'Document',
            'xid': utility._create_xid('Document', 'document-003'),  # pylint: disable=W0212
            'attribute': [
                {'displayed': True, 'type': 'Description', 'value': 'Example Description'}
            ],
            'tag': [{'name': 'Example Tag'}],
        }
    )


def document_malware_create(batch_job):
    """Test malware document creation"""
    batch_job.add_group(
        {
            'name': 'document-malware-003',
            'fileName': 'test.txt',
            'fileContent': 'Document content',
            'type': 'Document',
            'malware': True,
            'xid': utility._create_xid('Document', 'document-malware-003'),  # pylint: disable=W0212
            'attribute': [
                {'displayed': True, 'type': 'Description', 'value': 'Example Description'}
            ],
            'tag': [{'name': 'Example Tag'}],
        }
    )


def email_create(batch_job):
    """Test email creation"""
    batch_job.add_group(
        {
            'name': 'email-003',
            'type': 'Email',
            'xid': utility._create_xid('Email', 'email-003'),  # pylint: disable=W0212
            'attribute': [
                {'displayed': True, 'type': 'Description', 'value': 'Example Description'}
            ],
            'tag': [{'name': 'Example Tag'}],
            'subject': 'Greetings!',
            'header': 'This is just a test',
            'body': 'This is just a test',
        }
    )


def event_create(batch_job):
    """Test event creation"""
    batch_job.add_group(
        {
            'name': 'event-003',
            'type': 'Event',
            'xid': utility._create_xid('Event', 'event-003'),  # pylint: disable=W0212
            'attribute': [
                {'displayed': True, 'type': 'Description', 'value': 'Example Description'}
            ],
            'tag': [{'name': 'Example Tag'}],
        }
    )


def incident_create(batch_job):
    """Test incident creation"""
    batch_job.add_group(
        {
            'name': 'incident-003',
            'type': 'Incident',
            'xid': utility._create_xid('Incident', 'incident-003'),  # pylint: disable=W0212
            'attribute': [
                {'displayed': True, 'type': 'Description', 'value': 'Example Description'}
            ],
            'tag': [{'name': 'Example Tag'}],
        }
    )


def intrusion_set_create(batch_job):
    """Test intrusion set creation"""
    batch_job.add_group(
        {
            'name': 'intrusion_set-003',
            'type': 'Intrusion Set',
            'xid': utility._create_xid(  # pylint: disable=W0212
                'Intrusion Set', 'intrusion_set-003'
            ),
            'attribute': [
                {'displayed': True, 'type': 'Description', 'value': 'Example Description'}
            ],
            'tag': [{'name': 'Example Tag'}],
        }
    )


def report_create(batch_job):
    """Test report creation"""
    batch_job.add_group(
        {
            'name': 'report-003',
            'fileName': 'test.txt',
            'fileContent': 'Report content',
            'type': 'Report',
            'xid': utility._create_xid('Report', 'report-003'),  # pylint: disable=W0212
            'attribute': [
                {'displayed': True, 'type': 'Description', 'value': 'Example Description'}
            ],
            'tag': [{'name': 'Example Tag'}],
        }
    )


def signature_create(batch_job):
    """Test signature creation"""
    batch_job.add_group(
        {
            'name': 'signature-003',
            'fileName': 'test.snort',
            'fileType': 'Snort',
            'fileText': 'Signature content',
            'type': 'Signature',
            'xid': utility._create_xid('Signature', 'signature-003'),  # pylint: disable=W0212
            'attribute': [
                {'displayed': True, 'type': 'Description', 'value': 'Example Description'}
            ],
            'tag': [{'name': 'Example Tag'}],
        }
    )


def threat_create(batch_job):
    """Test threat creation"""
    batch_job.add_group(
        {
            'name': 'threat-003',
            'type': 'Threat',
            'xid': utility._create_xid('Threat', 'threat-003'),  # pylint: disable=W0212
            'attribute': [
                {'displayed': True, 'type': 'Description', 'value': 'Example Description'}
            ],
            'tag': [{'name': 'Example Tag'}],
        }
    )
