#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cleaner import _create_xid


def adversary_create(batch_job):
    batch_job.add_group({
        'name': 'adversary-003',
        'type': 'Adversary',
        'xid': _create_xid('Adversary', 'adversary-003'),
        'attribute': [{
            "displayed": True,
            "type": "Description",
            "value": "Example Description"
        }],
        'tag': [{
            'name': 'Example Tag'
        }]
    })


def campaign_create(batch_job):
    batch_job.add_group({
        'name': 'campaign-003',
        'type': 'Campaign',
        'xid': _create_xid('Campaign', 'campaign-003'),
        'attribute': [{
            "displayed": True,
            "type": "Description",
            "value": "Example Description"
        }],
        'tag': [{
            'name': 'Example Tag'
        }]
    })


def document_create(batch_job):
    batch_job.add_group({
        'name': 'document-003',
        'fileName': 'test.txt',
        'fileContent': 'Document content',
        'type': 'Document',
        'xid': _create_xid('Document', 'document-003'),
        'attribute': [{
            "displayed": True,
            "type": "Description",
            "value": "Example Description"
        }],
        'tag': [{
            'name': 'Example Tag'
        }]
    })


def document_malware_create(batch_job):
    batch_job.add_group({
        'name': 'document-malware-003',
        'fileName': 'test.txt',
        'fileContent': 'Document content',
        'type': 'Document',
        'malware': True,
        'xid': _create_xid('Document', 'document-malware-003'),
        'attribute': [{
            "displayed": True,
            "type": "Description",
            "value": "Example Description"
        }],
        'tag': [{
            'name': 'Example Tag'
        }]
    })


def email_create(batch_job):
    batch_job.add_group({
        'name': 'email-003',
        'type': 'Email',
        'xid': _create_xid('Email', 'email-003'),
        'attribute': [{
            "displayed": True,
            "type": "Description",
            "value": "Example Description"
        }],
        'tag': [{
            'name': 'Example Tag'
        }],
        'subject': 'Greetings!',
        'header': 'This is just a test',
        'body': 'This is just a test'
    })


def event_create(batch_job):
    batch_job.add_group({
        'name': 'event-003',
        'type': 'Event',
        'xid': _create_xid('Event', 'event-003'),
        'attribute': [{
            "displayed": True,
            "type": "Description",
            "value": "Example Description"
        }],
        'tag': [{
            'name': 'Example Tag'
        }]
    })


def incident_create(batch_job):
    batch_job.add_group({
        'name': 'incident-003',
        'type': 'Incident',
        'xid': _create_xid('Incident', 'incident-003'),
        'attribute': [{
            "displayed": True,
            "type": "Description",
            "value": "Example Description"
        }],
        'tag': [{
            'name': 'Example Tag'
        }]
    })


def intrusion_set_create(batch_job):
    batch_job.add_group({
        'name': 'intrusion_set-003',
        'type': 'Intrusion Set',
        'xid': _create_xid('Intrusion Set', 'intrusion_set-003'),
        'attribute': [{
            "displayed": True,
            "type": "Description",
            "value": "Example Description"
        }],
        'tag': [{
            'name': 'Example Tag'
        }]
    })


def report_create(batch_job):
    batch_job.add_group({
        'name': 'report-003',
        'fileName': 'test.txt',
        'fileContent': 'Report content',
        'type': 'Report',
        'xid': _create_xid('Report', 'report-003'),
        'attribute': [{
            "displayed": True,
            "type": "Description",
            "value": "Example Description"
        }],
        'tag': [{
            'name': 'Example Tag'
        }]
    })


def signature_create(batch_job):
    batch_job.add_group({
        'name': 'signature-003',
        'fileName': 'test.snort',
        'fileType': 'Snort',
        'fileContent': 'Signature content',
        'type': 'Signature',
        'xid': _create_xid('Signature', 'signature-003'),
        'attribute': [{
            "displayed": True,
            "type": "Description",
            "value": "Example Description"
        }],
        'tag': [{
            'name': 'Example Tag'
        }]
    })


def threat_create(batch_job):
    batch_job.add_group({
        'name': 'threat-003',
        'type': 'Threat',
        'xid': _create_xid('Threat', 'threat-003'),
        'attribute': [{
            "displayed": True,
            "type": "Description",
            "value": "Example Description"
        }],
        'tag': [{
            'name': 'Example Tag'
        }]
    })
