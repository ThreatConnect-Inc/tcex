# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""

import pytest

from ..tcex_init import tcex


# pylint: disable=R0201,W0201
class TestIndicator3:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @pytest.mark.parametrize(
        'indicator,description,label,tag',
        [
            ('3.33.33.1', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('3.33.33.2', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('3.33.33.3', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('3.33.33.4', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_address(self, indicator, description, label, tag):
        """Test address creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'address', indicator])
        ti = batch.add_indicator(
            {
                'type': 'Address',
                'rating': 5.00,
                'confidence': 100,
                'summary': indicator,
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
        'indicator,description,label,tag',
        [
            ('pytest-email_address-i3-001@test.com', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-email_address-i3-002@test.com', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-email_address-i3-003@test.com', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-email_address-i3-004@test.com', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_email_address(self, indicator, description, label, tag):
        """Test email_address creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'email_address', indicator])
        ti = batch.add_indicator(
            {
                'type': 'EmailAddress',
                'rating': 5.00,
                'confidence': 100,
                'summary': indicator,
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
        'md5,sha1,sha256,description,label,tag',
        [
            ('a3', 'a3', 'a3', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('b3', 'b3', 'b3', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('c3', 'c3', 'c3', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('d3', 'd3', 'd3', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_file(self, md5, sha1, sha256, description, label, tag):
        """Test file creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'file', md5, sha1, sha256])
        ti = batch.add_indicator(
            {
                'type': 'File',
                'rating': 5.00,
                'confidence': 100,
                'summary': '{} : {} : {}'.format(md5 * 16, sha1 * 20, sha256 * 32),
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
        'indicator,description,label,tag',
        [
            ('pytest-host-i3-001.com', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-host-i3-002.com', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-host-i3-003.com', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-host-i3-004.com', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_host(self, indicator, description, label, tag):
        """Test host creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'host', indicator])
        ti = batch.add_indicator(
            {
                'type': 'Host',
                'rating': 5.00,
                'confidence': 100,
                'summary': indicator,
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
        'indicator,description,label,tag',
        [
            ('https://pytest-url-i3-001.com', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('https://pytest-url-i3-002.com', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('https://pytest-url-i3-003.com', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('https://pytest-url-i3-004.com', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_url(self, indicator, description, label, tag):
        """Test url creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'url', indicator])
        ti = batch.add_indicator(
            {
                'type': 'Url',
                'rating': 5.00,
                'confidence': 100,
                'summary': indicator,
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
