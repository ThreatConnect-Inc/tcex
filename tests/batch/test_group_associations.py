"""Test the TcEx Batch Module."""


# pylint: disable=no-self-use
class TestGroup1:
    """Test the TcEx Batch Module."""

    previous_xids = []

    def setup_class(self):
        """Configure setup before all tests."""

    def test_group_associations(self, tcex):
        """Test adversary creation"""
        batch = tcex.batch(owner='TCI', halt_on_error=False)

        # reduce max chunk size to ensure associations are correct
        batch._batch_max_chunk = 2

        groups = {
            'pytest-adversary-i1-001': {
                'additional_data': {},
                'description': 'Example #1',
                'label': 'PYTEST1',
                'tag': 'PyTest1',
                'type': 'Adversary',
            },
            'pytest-campaign-i1-001': {
                'additional_data': {'first_seen': '2020-09-01T00:00:00Z'},
                'description': 'Example #1',
                'label': 'PYTEST1',
                'tag': 'PyTest1',
                'type': 'Campaign',
            },
            'pytest-document-i1-001': {
                'additional_data': {'file_name': 'pytest-1'},
                'description': 'Example #1',
                'label': 'PYTEST1',
                'tag': 'PyTest1',
                'type': 'Document',
            },
            'pytest-email-i1-001': {
                'additional_data': {
                    'subject': 'pytest-1',
                    'header': 'pytest-headers-1',
                    'body': 'pytest-body-1',
                },
                'description': 'Example #1',
                'label': 'PYTEST1',
                'tag': 'PyTest1',
                'type': 'Email',
            },
            'pytest-event-i1-001': {
                'additional_data': {},
                'description': 'Example #1',
                'label': 'PYTEST1',
                'tag': 'PyTest1',
                'type': 'event',
            },
            'pytest-incident-i1-001': {
                'additional_data': {},
                'description': 'Example #1',
                'label': 'PYTEST1',
                'tag': 'PyTest1',
                'type': 'Incident',
            },
            'pytest-intrusion_set-i1-001': {
                'additional_data': {},
                'description': 'Example #1',
                'label': 'PYTEST1',
                'tag': 'PyTest1',
                'type': 'Intrusion Set',
            },
            'pytest-report-i1-001': {
                'additional_data': {'file_name': 'pytest-1.pdf'},
                'description': 'Example #1',
                'label': 'PYTEST1',
                'tag': 'PyTest1',
                'type': 'Report',
            },
            'pytest-signature-i1-001': {
                'additional_data': {
                    'file_name': 'pytest-1.pdf',
                    'file_type': 'YARA',
                    'file_text': 'pytest-1',
                },
                'description': 'Example #1',
                'label': 'PYTEST1',
                'tag': 'PyTest1',
                'type': 'Signature',
            },
            'pytest-threat-i1-001': {
                'additional_data': {},
                'description': 'Example #1',
                'label': 'PYTEST1',
                'tag': 'PyTest1',
                'type': 'Threat',
            },
        }

        for name, group_data in groups.items():
            additional_data = group_data.get('additional_data')
            description = group_data.get('description')
            label = group_data.get('label')
            tag = group_data.get('tag')
            type_ = group_data.get('type')

            # generate a unique xid
            xid = batch.generate_xid(['pytest', type_.lower(), name])

            ti = batch.group(group_type=type_, name=name, xid=xid, **additional_data)
            for p_xid in self.previous_xids:
                ti.association(p_xid)

            if xid == '2197e43b831d0d8152ef47c9fa55bd2fb46632548ffa40fc51759e55bea4f205':
                # associate adversary (first entry) to threat (last entry)
                ti.association('9ada379c7d1adf626e96735711d34cb973a08399e235840410d9acdae3610163')

            ti.attribute(attr_type='Description', attr_value=description, displayed=True)
            ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
            ti.tag(name=tag)
            batch.save(ti)

            # set previous xid for next run
            self.previous_xids.append(xid)

        # submit
        batch_status = batch.submit_all(halt_on_error=False)
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 10
