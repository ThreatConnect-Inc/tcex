#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module to test batch creation using interface 2"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utility  # pylint: disable=C0413


def adversary_create(batch_job):
    """Test adversary creation"""
    name = 'adversary-002'
    xid = utility._create_xid('adversary', name)
    adversary = batch_job.group('Adversary', name, xid=xid)
    adversary.attribute('Description', 'Example Description', True)
    adversary.tag('Example Tag')


def campaign_create(batch_job):
    """Test campaign creation"""
    name = 'campaign-002'
    xid = utility._create_xid('campaign', name)
    campaign = batch_job.group('Campaign', name, xid=xid)
    campaign.attribute('Description', 'Example Description', True)
    campaign.tag('Example Tag')


def document_create(batch_job):
    """Test document creation"""
    name = 'document-002'
    xid = utility._create_xid('document', name)
    document = batch_job.group('Document', name, xid=xid)
    document.add_file('test.txt', 'Document content')
    document.attribute('Description', 'Example Description', True)
    document.tag('Example Tag')


def document_malware_create(batch_job):
    """Test malware document creation"""
    name = 'document-malware-002'
    xid = utility._create_xid('document', name)
    document = batch_job.group('Document', name, xid=xid)
    document.add_key_value('file_data', {'fileContent': 'test', 'type': 'Document'})
    document.add_key_value('fileName', 'test.pdf')
    document.add_key_value('malware', True)
    document.add_key_value('password', 'test')
    document.attribute('Description', 'Example Description', True)
    document.tag('Example Tag')


def email_create(batch_job):
    """Test email creation"""
    name = 'email-002'
    xid = utility._create_xid('email', name)
    email = batch_job.group('Email', name, xid=xid)
    email.add_key_value('subject', 'Greetings!')
    email.add_key_value('header', 'This is just a test')
    email.add_key_value('body', 'This is just a test')
    email.attribute('Description', 'Example Description', True)
    email.tag('Example Tag')


def event_create(batch_job):
    """Test event creation"""
    name = 'event-002'
    xid = utility._create_xid('event', name)
    event = batch_job.group('Event', name, xid=xid)
    event.attribute('Description', 'Example Description', True)
    event.tag('Example Tag')


def incident_create(batch_job):
    """Test incident creation"""
    name = 'incident-002'
    xid = utility._create_xid('incident', name)
    incident = batch_job.group('Incident', name, xid=xid)
    incident.attribute('Description', 'Example Description', True)
    incident.tag('Example Tag')


def intrusion_set_create(batch_job):
    """Test intrusion set creation"""
    name = 'intrusion_set-002'
    xid = utility._create_xid('intrusion set', name)
    intrusion_set = batch_job.group('Intrusion Set', name, xid=xid)
    intrusion_set.attribute('Description', 'Example Description', True)
    intrusion_set.tag('Example Tag')


def report_create(batch_job):
    """Test report creation"""
    name = 'report-002'
    xid = utility._create_xid('report', name)
    report = batch_job.group('Report', name, xid=xid)
    report.add_file('test.txt', 'Report content')
    report.attribute('Description', 'Example Description', True)
    report.tag('Example Tag')


def signature_create(batch_job):
    """Test signature creation"""
    name = 'signature-002'
    xid = utility._create_xid('signature', name)
    signature = batch_job.group('Signature', name, xid=xid)
    signature.add_key_value('fileName', 'test.snort')
    signature.add_key_value('fileType', 'Snort')
    signature.add_key_value('fileText', 'This is just a test...')
    signature.attribute('Description', 'Example Description', True)
    signature.tag('Example Tag')


def threat_create(batch_job):
    """Test threat creation"""
    name = 'threat-002'
    xid = utility._create_xid('threat', name)
    threat = batch_job.group('Threat', name, xid=xid)
    threat.attribute('Description', 'Example Description', True)
    threat.tag('Example Tag')
