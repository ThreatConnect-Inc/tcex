"""TcEx Framework Module"""
# standard library
import os

# first-party
from tcex import TcEx


class TestMessageTc:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @staticmethod
    def test_message_tc(tcex: TcEx):
        """Test message tc method."""
        # get the current out path from tcex
        message_tc_file = os.path.join(tcex.inputs.model.tc_out_path, 'message.tc')

        # cleanup any previous message.tc file
        if os.path.isfile(message_tc_file):
            os.remove(message_tc_file)

        # create and write a test message
        message = 'test'
        tcex.exit._message_tc(message)

        # assert the file exists
        if not os.path.isfile(message_tc_file):
            assert False, f'The message.tc file {message_tc_file} could not be found.'

        # read contents of file for assert
        with open(message_tc_file) as fh:
            message_tc = fh.read()

        # add a new line if not already there (tcex will add a newline if it doesn't exist)
        if not message.endswith('\n'):
            message += '\n'

        # assert message is correct
        assert message == message_tc, 'message.tc did not match message'

    @staticmethod
    def test_message_tc_long_message(tcex: TcEx):
        """Test long provided to message.tc method."""
        # get the current out path from tcex
        message_tc_file = os.path.join(tcex.inputs.model.tc_out_path, 'message.tc')

        # cleanup any previous message.tc file
        if os.path.isfile(message_tc_file):
            os.remove(message_tc_file)

        # create and write a test message
        message = (
            'word word word word word word word word word word word word word word word word word '
            'word word word word word word word word word word word word word word word word word '
            'word word word word word word word word word word word word word word word word word '
            'word word word word word word word word word word word word word word word word word '
        )
        tcex.exit._message_tc(message)

        # assert the file exists
        if not os.path.isfile(message_tc_file):
            assert False, f'The message.tc file {message_tc_file} could not be found.'

        # read contents of file for assert
        with open(message_tc_file) as fh:
            message_tc = fh.read()

        # add a new line if not already there (tcex will add a newline if it doesn't exist)
        if not message.endswith('\n'):
            message += '\n'

        # assert message is correct
        assert message[-255:] == message_tc, 'message.tc did not match message'

    @staticmethod
    def test_message_tc_multiple_messages(tcex: TcEx):
        """Test long provided to message.tc method."""
        # get the current out path from tcex
        message_tc_file = os.path.join(tcex.inputs.model.tc_out_path, 'message.tc')

        # cleanup any previous message.tc file
        if os.path.isfile(message_tc_file):
            os.remove(message_tc_file)

        message = (
            'word word word word word word word word word word word word word word word word word '
        )
        tcex.exit._message_tc(message)
        tcex.exit._message_tc(message)
        tcex.exit._message_tc(message)
        tcex.exit._message_tc(message)

        # assert the file exists
        if not os.path.isfile(message_tc_file):
            assert False, f'The message.tc file {message_tc_file} could not be found.'

        # read contents of file for assert
        with open(message_tc_file) as fh:
            message_tc = fh.read()

        assert f'{message[-255:]}\n' == message_tc, 'message.tc did not match message'
