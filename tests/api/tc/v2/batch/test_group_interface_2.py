"""Test the TcEx Batch Module."""
# standard library
from typing import TYPE_CHECKING

# third-party
import pytest

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx


# pylint: disable=no-self-use
class TestGroup2:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-adversary-i2-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-adversary-i2-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-adversary-i2-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-adversary-i2-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_adversary(self, name, description, label, tag, tcex: 'TcEx'):
        """Test adversary creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'adversary', name])
        ti = batch.group(group_type='Adversary', name=name, xid=xid)
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-campaign-i2-001', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-campaign-i2-002', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-campaign-i2-003', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-campaign-i2-004', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_campaign(self, name, description, label, tag, tcex: 'TcEx'):
        """Test campaign creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'campaign', name])
        ti = batch.group(group_type='Campaign', name=name, xid=xid)
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-document-i2-001', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-document-i2-002', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-document-i2-003', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-document-i2-004', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_document(self, name, description, label, tag, tcex: 'TcEx'):
        """Test document creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'document', name])
        ti = batch.group(group_type='Document', name=name, file_name='example.txt', xid=xid)
        ti.file_content = 'Example file content'
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-document-i2-malware-001', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-document-i2-malware-002', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-document-i2-malware-003', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-document-i2-malware-004', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_document_malware(self, name, description, label, tag, tcex: 'TcEx'):
        """Test document creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'document', name])
        ti = batch.group(group_type='Document', name=name, file_name='example.zip', xid=xid)
        ti.malware = True
        ti.password = 'test'
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-email-i2-001', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-email-i2-002', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-email-i2-003', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-email-i2-004', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_email(self, name, description, label, tag, tcex: 'TcEx'):
        """Test email creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'email', name])
        ti = batch.group(
            group_type='Email',
            name=name,
            subject='subject',
            header='test',
            body='this is just a test',
            xid=xid,
        )
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-event-i2-001', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-event-i2-002', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-event-i2-003', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-event-i2-004', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_event(self, name, description, label, tag, tcex: 'TcEx'):
        """Test event creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'event', name])
        ti = batch.group(group_type='Event', name=name, event_data='2008-12-12T12:12:12Z', xid=xid)
        ti.status = 'Escalated'
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-incident-i2-001', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-incident-i2-002', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-incident-i2-003', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-incident-i2-004', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_incident(self, name, description, label, tag, tcex: 'TcEx'):
        """Test incident creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'incident', name])
        ti = batch.group(group_type='Incident', name=name, xid=xid)
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-intrusion_set-i2-001', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-intrusion_set-i2-002', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-intrusion_set-i2-003', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-intrusion_set-i2-004', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_intrusion_set(self, name, description, label, tag, tcex: 'TcEx'):
        """Test intrusion_set creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'intrusion_set', name])
        ti = batch.group(group_type='Intrusion Set', name=name, xid=xid)
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-report-i2-001', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-report-i2-002', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-report-i2-003', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-report-i2-004', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_report(self, name, description, label, tag, tcex: 'TcEx'):
        """Test report creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'report', name])
        ti = batch.group(
            group_type='Report',
            name=name,
            file_name='report.pdf',
            publish_date='2008-12-12',
            xid=xid,
        )
        ti.file_content = 'test 123'
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-signature-i2-001', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-signature-i2-002', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-signature-i2-003', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-signature-i2-004', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_signature(self, name, description, label, tag, tcex: 'TcEx'):
        """Test signature creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'signature', name])
        ti = batch.group(
            group_type='Signature',
            name=name,
            file_name='test.snort',
            file_type='snort',
            file_text='test',
            xid=xid,
        )
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-threat-i2-001', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-threat-i2-002', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-threat-i2-003', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-threat-i2-004', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_threat(self, name, description, label, tag, tcex: 'TcEx'):
        """Test threat creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'threat', name])
        ti = batch.group(group_type='Threat', name=name, xid=xid)
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1
