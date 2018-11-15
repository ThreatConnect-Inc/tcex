#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def adversary_create(batch_job):
    adversary = batch_job.group('Adversary', 'adversary-002')
    adversary.attribute('Description', 'Example Description', True)
    adversary.tag('Example Tag')


def campaign_create(batch_job):
    campaign = batch_job.group('Campaign', 'campaign-002')
    campaign.attribute('Description', 'Example Description', True)
    campaign.tag('Example Tag')


def document_create(batch_job):
    document = batch_job.group('Document', 'document-002')
    document.add_file('test.txt', 'Document content')
    document.attribute('Description', 'Example Description', True)
    document.tag('Example Tag')


def document_malware_create(batch_job):
    document = batch_job.group('Document', 'document-malware-002')
    document.add_key_value('file_data', {
        'fileContent': 'test',
        'type': 'Document'
    })
    document.add_key_value('fileName', 'test.pdf')
    document.add_key_value('malware', True)
    document.add_key_value('password', 'test')
    document.attribute('Description', 'Example Description', True)
    document.tag('Example Tag')


def email_create(batch_job):
    email = batch_job.group('Email', 'email-002')
    email.add_key_value('subject', 'Greetings!')
    email.add_key_value('header', 'This is just a test')
    email.add_key_value('body', 'This is just a test')
    email.attribute('Description', 'Example Description', True)
    email.tag('Example Tag')


def event_create(batch_job):
    event = batch_job.group('Event', 'event-002')
    event.attribute('Description', 'Example Description', True)
    event.tag('Example Tag')


def incident_create(batch_job):
    incident = batch_job.group('Incident', 'incident-002')
    incident.attribute('Description', 'Example Description', True)
    incident.tag('Example Tag')


def intrusion_set_create(batch_job):
    intrusion_set = batch_job.group('Intrusion Set', 'intrusion_set-002')
    intrusion_set.attribute('Description', 'Example Description', True)
    intrusion_set.tag('Example Tag')


def report_create(batch_job):
    report = batch_job.group('Report', 'report-002')
    report.add_file('test.txt', 'Report content')
    report.attribute('Description', 'Example Description', True)
    report.tag('Example Tag')


def signature_create(batch_job):
    signature = batch_job.group('Signature', 'signature-002')
    signature.add_key_value('fileName', 'test.snort')
    signature.add_key_value('fileType', 'Snort')
    signature.add_key_value('fileText', 'This is just a test...')
    signature.attribute('Description', 'Example Description', True)
    signature.tag('Example Tag')


def threat_create(batch_job):
    threat = batch_job.group('Threat', 'threat-002')
    threat.attribute('Description', 'Example Description', True)
    threat.tag('Example Tag')
