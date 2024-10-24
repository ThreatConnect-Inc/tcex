"""TcEx Framework Module"""

# third-party
import pytest

# first-party
from tcex.app.playbook.playbook import Playbook


class TestPlaybookRaw:
    """Test the TcEx Batch Module."""

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:r1!Raw', b'bytes 1'),
            ('#App:0002:r2!Raw', b'string'),
            ('#App:0002:r3!Raw', b'1'),
        ],
    )
    def test_playbook_raw(self, variable: str, value: bytes, playbook: Playbook):
        """Test playbook variables."""
        playbook.create.raw(variable, value)
        result = playbook.read.raw(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    def test_playbook_create_raw_none(self, playbook: Playbook):
        """Test playbook variables."""
        result = playbook.create.raw(None, None)  # type: ignore
        assert result is None, f'result of ({result}) is not None'

    def test_playbook_read_raw_none(self, playbook: Playbook):
        """Test playbook variables."""
        result = playbook.read.raw(None)  # type: ignore
        assert result is None, f'result of ({result}) is not None'
