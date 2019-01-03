#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module to test batch group creation using interface 1"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utility  # pylint: disable=C0413


def adversary_create(batch_job):
    """Test adversary creation"""
    name = 'adversary-001'
    xid = utility._create_xid('adversary', name)
    adversary = batch_job.adversary(name, xid=xid)
    adversary.attribute('Description', 'Example Description', True)
    adversary.tag('Example Tag')


def campaign_create(batch_job):
    """Test campaign creation"""
    name = 'campaign-001'
    xid = utility._create_xid('campaign', name)
    campaign = batch_job.campaign(name, xid=xid)
    campaign.attribute('Description', 'Example Description', True)
    campaign.tag('Example Tag')


def document_create(batch_job):
    """Test document creation"""
    name = 'document-001'
    xid = utility._create_xid('document', name)
    document = batch_job.document(name, 'example.txt', xid=xid)
    document.file_content = 'Example file content'
    document.attribute('Description', 'Example Description', True)
    document.tag('Example Tag')


def document_malware_create(batch_job):
    """Test document malware creation"""
    name = 'document-malware'
    xid = utility._create_xid('document', name)
    document = batch_job.document(name, 'example.zip', xid=xid)
    document.malware = True
    document.password = 'test'
    document.file_content = 'example file content'
    document.attribute('Description', 'Example Description', True)
    document.tag('Example Tag')


def email_create(batch_job):
    """Test email creation"""
    name = 'email-001'
    xid = utility._create_xid('email', name)
    email = batch_job.email(name, 'subject', 'test', 'this is just a test', xid=xid)
    email.attribute('Description', 'Example Description', True)
    email.tag('Example Tag')


def event_create(batch_job):
    """Test event creation"""
    name = 'event-001'
    xid = utility._create_xid('event', name)
    event = batch_job.event(name, xid=xid)
    event.attribute('Description', 'Example Description', True)
    event.tag('Example Tag')


def incident_create(batch_job):
    """Test incident creation"""
    name = 'incident-001'
    xid = utility._create_xid('incident', name)
    incident = batch_job.incident(name, xid=xid)
    incident.attribute('Description', 'Example Description', True)
    incident.tag('Example Tag')


def intrusion_set_create(batch_job):
    """Test intrusion set creation"""
    name = 'intrusion_set-001'
    xid = utility._create_xid('intrusion set', name)
    intrusion_set = batch_job.intrusion_set(name, xid=xid)
    intrusion_set.attribute('Description', 'Example Description', True)
    intrusion_set.tag('Example Tag')


def report_create(batch_job):
    """Test report creation"""
    name = 'report-001'
    xid = utility._create_xid('report', name)
    report = batch_job.report(name, file_content='example file content', file_name='report', xid=xid)
    report.attribute('Description', 'Example Description', True)
    report.tag('Example Tag')


def signature_create(batch_job):
    """Test signature creation"""
    name = 'signature-001'
    xid = utility._create_xid('signature', name)
    signature = batch_job.signature(name, 'test.snort', 'snort', 'test', xid=xid)
    signature.attribute('Description', 'Example Description', True)
    signature.tag('Example Tag')


def threat_create(batch_job):
    """Test threat creation"""
    name = 'threat-001'
    xid = utility._create_xid('threat', name)
    threat = batch_job.threat(name, xid=xid)
    threat.attribute('Description', 'Example Description', True)
    threat.tag('Example Tag')
