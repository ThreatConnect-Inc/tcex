#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def adversary_create(batch_job):
    adversary = batch_job.adversary('adversary-001')
    adversary.attribute('Description', 'Example Description', True)
    adversary.tag('Example Tag')


def campaign_create(batch_job):
    campaign = batch_job.campaign('campaign-001')
    campaign.attribute('Description', 'Example Description', True)
    campaign.tag('Example Tag')


def document_create(batch_job):
    document = batch_job.document('document-001', 'example.txt')
    document.file_content = 'Example file content'
    document.attribute('Description', 'Example Description', True)
    document.tag('Example Tag')


def document_malware_create(batch_job):
    document = batch_job.document('document-malware-001', 'example.zip')
    document.malware = True
    document.password = 'test'
    document.file_content = 'example file content'
    document.attribute('Description', 'Example Description', True)
    document.tag('Example Tag')


def email_create(batch_job):
    email = batch_job.email('email-001', 'subject', 'test', 'this is just a test')
    email.attribute('Description', 'Example Description', True)
    email.tag('Example Tag')


def event_create(batch_job):
    event = batch_job.event('event-001')
    event.attribute('Description', 'Example Description', True)
    event.tag('Example Tag')


def incident_create(batch_job):
    incident = batch_job.incident('incident-001')
    incident.attribute('Description', 'Example Description', True)
    incident.tag('Example Tag')


def intrusion_set_create(batch_job):
    intrusion_set = batch_job.intrusion_set('intrusion_set-001')
    intrusion_set.attribute('Description', 'Example Description', True)
    intrusion_set.tag('Example Tag')


def report_create(batch_job):
    report = batch_job.report('report-001', 'report')
    report.file_content = 'example file content'
    report.attribute('Description', 'Example Description', True)
    report.tag('Example Tag')


def signature_create(batch_job):
    signature = batch_job.signature('signature-001', 'test.snort', 'snort', 'test')
    signature.attribute('Description', 'Example Description', True)
    signature.tag('Example Tag')


def threat_create(batch_job):
    threat = batch_job.threat('threat-001')
    threat.attribute('Description', 'Example Description', True)
    threat.tag('Example Tag')
