# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""

import pytest

from ..tcex_init import tcex


# pylint: disable=R0201,W0201
class TestIndicator2:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @pytest.mark.parametrize(
        'indicator,description,label,tag',
        [
            ('2.22.222.1', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('2.22.222.2', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('2.22.222.3', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('2.22.222.4', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_address(self, indicator, description, label, tag):
        """Test address creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'address', indicator])
        ti = batch.indicator(
            indicator_type='Address', summary=indicator, rating='5.0', confidence='100', xid=xid
        )
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'indicator,description,label,tag',
        [
            ('pytest-email_address-i2-001@test.com', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-email_address-i2-002@test.com', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-email_address-i2-003@test.com', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-email_address-i2-004@test.com', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_email_address(self, indicator, description, label, tag):
        """Test email_address creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'email_address', indicator])
        ti = batch.indicator(
            indicator_type='EmailAddress',
            summary=indicator,
            rating='5.0',
            confidence='100',
            xid=xid,
        )
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'md5,sha1,sha256,description,label,tag',
        [
            ('a2', 'a2', 'a2', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('b2', 'b2', 'b2', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('c2', 'c2', 'c2', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('d2', 'd2', 'd2', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_file(self, md5, sha1, sha256, description, label, tag):
        """Test file creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'file', md5, sha1, sha256])
        ti = batch.indicator(
            indicator_type='File',
            summary='{} : {} : {}'.format(md5 * 16, sha1 * 20, sha256 * 32),
            rating='5.0',
            confidence='100',
            xid=xid,
        )
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'indicator,description,label,tag',
        [
            ('pytest-host-i2-001.com', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-host-i2-002.com', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-host-i2-003.com', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-host-i2-004.com', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_host(self, indicator, description, label, tag):
        """Test host creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'host', indicator])
        ti = batch.indicator(
            indicator_type='Host', summary=indicator, rating='5.0', confidence='100', xid=xid
        )
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'indicator,description,label,tag',
        [
            ('https://pytest-url-i2-001.com', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('https://pytest-url-i2-002.com', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('https://pytest-url-i2-003.com', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('https://pytest-url-i2-004.com', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_url(self, indicator, description, label, tag):
        """Test url creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'url', indicator])
        ti = batch.indicator(
            indicator_type='URL', summary=indicator, rating='5.0', confidence='100', xid=xid
        )
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1
