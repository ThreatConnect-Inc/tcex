"""Test the TcEx Batch Module."""
# standard library
from typing import TYPE_CHECKING

# third-party
import pytest

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx


# pylint: disable=no-self-use
class TestTags1:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @pytest.mark.parametrize('name,tag', [('pytest-adversary-i1-001', 'PyTest1')])
    def test_tag(self, name, tag, tcex: 'TcEx'):
        """Test adversary creation"""
        batch = tcex.v2.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'adversary', name])
        ti = batch.adversary(name=name, xid=xid)

        # tag testing
        tag_data = ti.tag(name=tag, formatter=self.tag_formatter)
        tcex.log.debug(f'tag_data: {tag_data}')  # cover __str__ method
        ti.tag(name=None)  # cover "not name"

        # submit batch
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    def tag_formatter(self, tag):
        """Return formatted tag."""
        return tag.lower()
