"""Test the TcEx Batch Module."""
# standard library
from typing import TYPE_CHECKING

# third-party
import pytest

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx


# pylint: disable=no-self-use
class TestIndicator1:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @pytest.mark.parametrize(
        'indicator,description,label,tag',
        [
            ('1.11.111.1', 'Example #1', 'PYTEST1', 'PyTest1'),
            ('1.11.111.2', 'Example #2', 'PYTEST2', 'PyTest2'),
            ('1.11.111.3', 'Example #3', 'PYTEST3', 'PyTest3'),
            ('1.11.111.4', 'Example #4', 'PYTEST4', 'PyTest4'),
        ],
    )
    def test_address(self, indicator, description, label, tag, tcex: 'TcEx'):
        """Test address creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'address', indicator])
        ti = batch.address(ip=indicator, rating='5.0', confidence='100', xid=xid)
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'indicator,description,label,tag',
        [
            ('pytest-email_address-i1-001@test.com', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-email_address-i1-002@test.com', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-email_address-i1-003@test.com', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-email_address-i1-004@test.com', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_email_address(self, indicator, description, label, tag, tcex: 'TcEx'):
        """Test email_address creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'email_address', indicator])
        ti = batch.email_address(address=indicator, rating='5.0', confidence='100', xid=xid)
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'md5,sha1,sha256,description,label,tag',
        [
            ('a1', 'a1', 'a1', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('b1', 'b1', 'b1', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('c1', 'c1', 'c1', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('d1', 'd1', 'd1', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_file(self, md5, sha1, sha256, description, label, tag, tcex: 'TcEx'):
        """Test file creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'file', md5, sha1, sha256])
        ti = batch.file(
            md5=md5 * 16,
            sha1=sha1 * 20,
            sha256=sha256 * 32,
            rating='5.0',
            confidence='100',
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
        'indicator,description,label,tag',
        [
            ('pytest-host-i1-001.com', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('pytest-host-i1-002.com', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('pytest-host-i1-003.com', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('pytest-host-i1-004.com', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_host(self, indicator, description, label, tag, tcex: 'TcEx'):
        """Test host creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'host', indicator])
        ti = batch.host(hostname=indicator, rating='5.0', confidence='100', xid=xid)
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @pytest.mark.parametrize(
        'indicator,description,label,tag',
        [
            ('https://pytest-url-i1-001.com', 'Example #1', 'PYTEST:1', 'PyTest1'),
            ('https://pytest-url-i1-002.com', 'Example #2', 'PYTEST:2', 'PyTest2'),
            ('https://pytest-url-i1-003.com', 'Example #3', 'PYTEST:3', 'PyTest3'),
            ('https://pytest-url-i1-004.com', 'Example #4', 'PYTEST:4', 'PyTest4'),
        ],
    )
    def test_url(self, indicator, description, label, tag, tcex: 'TcEx'):
        """Test url creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'url', indicator])
        ti = batch.url(text=indicator, rating='5.0', confidence='100', xid=xid)
        ti.attribute(attr_type='Description', attr_value=description, displayed=True)
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')
        ti.tag(name=tag)
        batch.save(ti)
        batch_status = batch.submit_all()
        batch.close()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1
