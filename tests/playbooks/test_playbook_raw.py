"""Test the TcEx Batch Module."""
# third-party
import pytest


# pylint: disable=no-self-use
class TestPlaybookRaw:
    """Test the TcEx Batch Module."""

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:r1!Raw', b'bytes 1'),
            ('#App:0002:r2!Raw', 'string'),
            ('#App:0002:r3!Raw', 1),
        ],
    )
    def test_playbook_raw(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_raw(variable, value)
        result = tcex.playbook.read_raw(variable)
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        assert result == str(value), f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    def test_playbook_create_raw_none(self, tcex):
        """Test the create output method of Playbook module.

        Args:
            tcex (TcEx, fixture): The tcex fixture.
        """
        # parse variable and send to create_output() method
        result = tcex.playbook.create_raw(None, None)
        assert result is None, f'result of ({result}) is not None'

    def test_playbook_read_raw_none(self, tcex):
        """Test the create output method of Playbook module.

        Args:
            tcex (TcEx, fixture): The tcex fixture.
        """
        # parse variable and send to create_output() method
        result = tcex.playbook.read_raw(None)
        assert result is None, f'result of ({result}) is not None'
