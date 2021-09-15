"""Test the TcEx Batch Module."""
# third-party
import pytest


# pylint: disable=no-self-use
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
    def test_adversary(self, name, description, label, tag, tcex):
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
            ('pytest-attack-pattern-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-attack-pattern-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-attack-pattern-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-attack-pattern-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_attack_pattern(self, name, description, label, tag, tcex):
        """Test attack_pattern creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'attack_pattern', name])
        ti = batch.add_group(
            {
                'name': name,
                'type': 'Attack Pattern',
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
            ('pytest-course-of-action-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-course-of-action-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-course-of-action-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-course-of-action-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_course_of_action(self, name, description, label, tag, tcex):
        """Test course of action creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'course_of_action', name])
        ti = batch.add_group(
            {
                'name': name,
                'type': 'Course of Action',
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
    def test_campaign(self, name, description, label, tag, tcex):
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
    def test_document(self, name, description, label, tag, tcex):
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
    def test_document_malware(self, name, description, label, tag, tcex):
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
    def test_email(self, name, description, label, tag, tcex):
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
    def test_event(self, name, description, label, tag, tcex):
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
    def test_incident(self, name, description, label, tag, tcex):
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
    def test_intrusion_set(self, name, description, label, tag, tcex):
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
            ('pytest-malware-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-malware-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-malware-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-malware-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_malware(self, name, description, label, tag, tcex):
        """Test malware creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'malware', name])
        ti = batch.add_group(
            {
                'name': name,
                'type': 'Malware',
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
    def test_report(self, name, description, label, tag, tcex):
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
    def test_signature(self, name, description, label, tag, tcex):
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
            ('pytest-tactic-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-tactic-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-tactic-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-tactic-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_tactic(self, name, description, label, tag, tcex):
        """Test tactic creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'tactic', name])
        ti = batch.add_group(
            {
                'name': name,
                'type': 'Tactic',
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
    def test_threat(self, name, description, label, tag, tcex):
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

    @pytest.mark.parametrize(
        'name,description,label,tag',
        [
            ('pytest-tool-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-tool-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-tool-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-tool-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_tool(self, name, description, label, tag, tcex):
        """Test tool creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'tool', name])
        ti = batch.add_group(
            {
                'name': name,
                'type': 'Tool',
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
            ('pytest-vulnerability-i3-001', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('pytest-vulnerability-i3-002', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('pytest-vulnerability-i3-003', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('pytest-vulnerability-i3-004', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_vulnerability(self, name, description, label, tag, tcex):
        """Test vulnerability creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'vulnerability', name])
        ti = batch.add_group(
            {
                'name': name,
                'type': 'Vulnerability',
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
