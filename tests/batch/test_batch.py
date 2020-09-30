"""Test the TcEx Batch Module."""
# standard library
import os
from datetime import datetime, timedelta


class TestAttributes:
    """Test the TcEx Batch Module."""

    @staticmethod
    def test_batch_action(tcex):
        """Test batch attributes creation"""
        batch = tcex.batch(action='Delete', owner=os.getenv('TC_OWNER'))
        assert batch.action == 'Delete'

    @staticmethod
    def test_batch_group_existing(request, tcex):
        """Test batch attributes creation"""
        batch = tcex.batch(owner=os.getenv('TC_OWNER'))
        group_data = {
            'first_seen': (datetime.now() - timedelta(days=2)).isoformat(),
            'name': request.node.name,
            'xid': batch.generate_xid(['pytest', 'campaign', request.node.name]),
        }
        ti = batch.campaign(**group_data)

        # add same indicator again ensuring that previously created indicator is returned
        ti = batch.campaign(name=group_data.get('name'), xid=group_data.get('xid'))
        assert group_data.get('first_seen')[:19] in ti.first_seen
        assert len(batch) == 1
        assert batch.group_len == 1

    @staticmethod
    def test_batch_group_existing_shelf(request, tcex):
        """Test batch attributes creation"""
        batch = tcex.batch(owner=os.getenv('TC_OWNER'))
        group_data = {
            'first_seen': (datetime.now() - timedelta(days=2)).isoformat(),
            'name': request.node.name,
            'xid': batch.generate_xid(['pytest', 'campaign', request.node.name]),
        }
        ti = batch.campaign(**group_data)
        batch.save(ti)

        # add same indicator again ensuring that previously created indicator is returned
        ti = batch.campaign(name=group_data.get('name'), xid=group_data.get('xid'))
        assert group_data.get('first_seen')[:19] in ti.first_seen
        assert len(batch) == 1
        assert batch.group_len == 1

    @staticmethod
    def test_batch_group_file(request, tcex):
        """Test batch attributes creation"""
        batch = tcex.batch(owner=os.getenv('TC_OWNER'))

        def file_content(xid):
            """Return dummy file content."""
            return f'file content for {request.node.name}, xid {xid}'

        group_data = {
            'first_seen': (datetime.now() - timedelta(days=2)).isoformat(),
            'file_content': file_content,
            'name': request.node.name,
            'xid': batch.generate_xid(['pytest', 'campaign', request.node.name]),
        }
        ti = batch.report(**group_data)
        batch.save(ti)

        # add same indicator again ensuring that previously created indicator is returned
        file_content = ti.file_data.get('fileContent')(ti.xid)
        assert file_content == group_data.get('file_content')(group_data.get('xid'))

    @staticmethod
    def test_batch_indicator_existing(request, tcex):
        """Test batch attributes creation"""
        batch = tcex.batch(owner=os.getenv('TC_OWNER'))
        indicator_data = {
            'confidence': 42,
            'ip': '1.1.1.1',
            'rating': 5,
            'xid': batch.generate_xid(['pytest', 'address', request.node.name]),
        }
        ti = batch.address(**indicator_data)

        # add same indicator again ensuring that previously created indicator is returned
        ti = batch.address(ip=indicator_data.get('ip'), xid=indicator_data.get('xid'))
        assert ti.confidence == indicator_data.get('confidence')
        assert ti.rating == indicator_data.get('rating')
        assert len(batch) == 1
        assert batch.indicator_len == 1

    @staticmethod
    def test_batch_indicator_existing_shelf(request, tcex):
        """Test batch attributes creation"""
        batch = tcex.batch(owner=os.getenv('TC_OWNER'))
        indicator_data = {
            'confidence': 42,
            'ip': '1.1.1.1',
            'rating': 5,
            'xid': batch.generate_xid(['pytest', 'address', request.node.name]),
        }
        ti = batch.address(**indicator_data)
        batch.save(ti)

        # add same indicator again ensuring that previously created indicator is returned
        ti = batch.address(ip=indicator_data.get('ip'), xid=indicator_data.get('xid'))
        assert ti.confidence == indicator_data.get('confidence')
        assert ti.rating == indicator_data.get('rating')
        assert len(batch) == 1
        assert batch.indicator_len == 1

    @staticmethod
    def test_batch_indicator_expand(tcex):
        """Test batch attributes creation"""
        batch = tcex.batch(owner=os.getenv('TC_OWNER'))
        indicator_data = (
            'e3fc50a88d0a364313df4b21ef20c29e : '
            '92170cdc034b2ff819323ff670d3b7266c8bffcd : '
            'b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1'
        )
        assert batch._indicator_values(indicator_data) == indicator_data.split(' : ')
