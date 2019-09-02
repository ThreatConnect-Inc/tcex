# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import pytest


# pylint: disable=R0201,W0201
class TestTags1:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @pytest.mark.parametrize('name,label', [('pytest-adversary-i1-001', 'PYTEST1')])
    def test_security_labels(self, name, label, tcex):
        """Test adversary creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'adversary', name])
        ti = batch.adversary(name=name, xid=xid)

        # security label testing - option 1
        ti.security_label(name=label, description='Pytest Label Description', color='ffc0cb')

        # security label testing - option 2
        sl = ti.security_label(name=label)
        sl.description = 'Pytest Label Description'
        sl.color = 'ffc0cb'

        tcex.log.debug('sl color: {}'.format(sl.color))  # cover color property
        tcex.log.debug('sl description: {}'.format(sl.description))  # cover color description
        tcex.log.debug('sl data: {}'.format(sl))  # cover __str__ method
        assert sl.description == 'Pytest Label Description'
        assert sl.color == 'ffc0cb'
        assert sl.name == label

        # submit batch
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1
