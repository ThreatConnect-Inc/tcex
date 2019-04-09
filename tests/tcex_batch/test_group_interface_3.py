# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""

import pytest

from ..tcex_init import tcex


# pylint: disable=R0201,W0201
class TestGroup3:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-adversary-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-adversary-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-adversary-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-adversary-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_adversary(self, name, description, label, tag):
        """Test adversary creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'adversary', name])
        ti = batch.add_group(
            {
                'name': name,
                'type': 'Adversary',
                'xid': xid,
                'attribute': [{'displayed': True, 'type': 'Description', 'value': description}],
                'securityLabel': [
                    {'color': 'ffc0cb', 'name': label, 'description': 'Pytest Label Description'}
                ],
                'tag': [{'name': tag}],
            }
        )
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-campaign-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-campaign-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-campaign-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-campaign-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_campaign(self, name, description, label, tag):
        """Test campaign creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'campaign', name])
        ti = batch.add_group(
            {
                'name': name,
                'type': 'Campaign',
                'xid': xid,
                'attribute': [{'displayed': True, 'type': 'Description', 'value': description}],
                'securityLabel': [
                    {'color': 'ffc0cb', 'name': label, 'description': 'Pytest Label Description'}
                ],
                'tag': [{'name': tag}],
            }
        )
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-document-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-document-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-document-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-document-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_document(self, name, description, label, tag):
        """Test document creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'document', name])
        ti = batch.add_group(
            {
                'name': name,
                'fileName': 'test.txt',
                'fileContent': 'Example file content',
                'type': 'Document',
                'xid': xid,
                'attribute': [{'displayed': True, 'type': 'Description', 'value': description}],
                'securityLabel': [
                    {'color': 'ffc0cb', 'name': label, 'description': 'Pytest Label Description'}
                ],
                'tag': [{'name': tag}],
            }
        )
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-document-malware-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-document-malware-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-document-malware-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-document-malware-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_document_malware(self, name, description, label, tag):
        """Test document creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'document', name])
        ti = batch.add_group(
            {
                'name': name,
                'fileName': 'test.zip',
                'fileContent': 'Example file content',
                'malware': True,
                'password': 'test',
                'type': 'Document',
                'xid': xid,
                'attribute': [{'displayed': True, 'type': 'Description', 'value': description}],
                'securityLabel': [
                    {'color': 'ffc0cb', 'name': label, 'description': 'Pytest Label Description'}
                ],
                'tag': [{'name': tag}],
            }
        )
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-email-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-email-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-email-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-email-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_email(self, name, description, label, tag):
        """Test email creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'email', name])
        ti = batch.add_group(
            {
                'name': name,
                'body': 'Email Body',
                'header': 'Email Header',
                'subject': 'Email Subject',
                'type': 'Email',
                'xid': xid,
                'attribute': [{'displayed': True, 'type': 'Description', 'value': description}],
                'securityLabel': [
                    {'color': 'ffc0cb', 'name': label, 'description': 'Pytest Label Description'}
                ],
                'tag': [{'name': tag}],
            }
        )
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-event-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-event-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-event-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-event-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_event(self, name, description, label, tag):
        """Test event creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'event', name])
        ti = batch.add_group(
            {
                'name': name,
                'type': 'Event',
                'xid': xid,
                'attribute': [{'displayed': True, 'type': 'Description', 'value': description}],
                'securityLabel': [
                    {'color': 'ffc0cb', 'name': label, 'description': 'Pytest Label Description'}
                ],
                'tag': [{'name': tag}],
            }
        )
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-incident-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-incident-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-incident-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-incident-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_incident(self, name, description, label, tag):
        """Test incident creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'incident', name])
        ti = batch.add_group(
            {
                'name': name,
                'type': 'Incident',
                'xid': xid,
                'attribute': [{'displayed': True, 'type': 'Description', 'value': description}],
                'securityLabel': [
                    {'color': 'ffc0cb', 'name': label, 'description': 'Pytest Label Description'}
                ],
                'tag': [{'name': tag}],
            }
        )
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-intrusion_set-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-intrusion_set-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-intrusion_set-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-intrusion_set-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_intrusion_set(self, name, description, label, tag):
        """Test intrusion_set creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'intrusion_set', name])
        ti = batch.add_group(
            {
                'name': name,
                'type': 'Intrusion Set',
                'xid': xid,
                'attribute': [{'displayed': True, 'type': 'Description', 'value': description}],
                'securityLabel': [
                    {'color': 'ffc0cb', 'name': label, 'description': 'Pytest Label Description'}
                ],
                'tag': [{'name': tag}],
            }
        )
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-report-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-report-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-report-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-report-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_report(self, name, description, label, tag):
        """Test report creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'report', name])
        ti = batch.add_group(
            {
                'name': name,
                'fileContent': 'Report Content',
                'fileName': 'test.pdf',
                'type': 'Report',
                'xid': xid,
                'attribute': [{'displayed': True, 'type': 'Description', 'value': description}],
                'securityLabel': [
                    {'color': 'ffc0cb', 'name': label, 'description': 'Pytest Label Description'}
                ],
                'tag': [{'name': tag}],
            }
        )
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-signature-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-signature-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-signature-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-signature-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_signature(self, name, description, label, tag):
        """Test signature creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'signature', name])
        ti = batch.add_group(
            {
                'name': name,
                'fileName': 'test.snort',
                'fileType': 'Snort',
                'fileText': 'Signature content',
                'type': 'Signature',
                'xid': xid,
                'attribute': [{'displayed': True, 'type': 'Description', 'value': description}],
                'securityLabel': [
                    {'color': 'ffc0cb', 'name': label, 'description': 'Pytest Label Description'}
                ],
                'tag': [{'name': tag}],
            }
        )
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-threat-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-threat-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-threat-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-threat-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_threat(self, name, description, label, tag):
        """Test threat creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'threat', name])
        ti = batch.add_group(
            {
                'name': name,
                'type': 'Threat',
                'xid': xid,
                'attribute': [{'displayed': True, 'type': 'Description', 'value': description}],
                'securityLabel': [
                    {'color': 'ffc0cb', 'name': label, 'description': 'Pytest Label Description'}
                ],
                'tag': [{'name': tag}],
            }
        )
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1
